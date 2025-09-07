"""Torque Logger Coordinator."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import slugify

from .sensor import TorqueSensor
from .device_tracker import TorqueDeviceTracker
from .const import DOMAIN, ENTITY_GPS, TORQUE_GPS_LAT, TORQUE_GPS_LON

if TYPE_CHECKING:
    from .api import TorqueReceiveDataView

_LOGGER: logging.Logger = logging.getLogger(__package__)


class TorqueLoggerCoordinator(DataUpdateCoordinator):
    """GÃ¨re lâ€™Ã©tat et la crÃ©ation des entitÃ©s Torque."""

    # RenseignÃ©s par les plateformes lors de leur setup
    async_add_sensor: Optional[AddEntitiesCallback] = None
    async_add_device_tracker: Optional[AddEntitiesCallback] = None

    def __init__(
        self,
        hass: HomeAssistant,
        client: "TorqueReceiveDataView",
        entry: ConfigEntry,
    ) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN)
        self.api = client
        self.entry = entry
        client.coordinator = self

        # Capteurs dÃ©jÃ  crÃ©Ã©s (par voiture) via clef "car_id:sensor_key"
        self.tracked: set[str] = set()
        # DerniÃ¨res donnÃ©es reÃ§ues par voiture (car_id -> session_data)
        self.cars: dict[str, dict] = {}

    async def _async_update_data(self):
        """Aucune mise Ã  jour planifiÃ©e : on est en push uniquement."""
        return None

    # --------- Lecture de donnÃ©es ----------
    def get_value(self, car_id: str, key: str):
        data = self.cars.get(car_id)
        if not data:
            return None
        return data.get(key)

    def get_meta(self, car_id: str) -> dict:
        data = self.cars.get(car_id)
        if not data:
            return {}
        return data.get("meta", {})

    # --------- RÃ©ception depuis lâ€™API ----------
    def update_from_session(self, session_data: dict) -> None:
        """AppelÃ© par lâ€™API quand un nouveau payload est parsÃ©."""
        car_id = slugify(session_data["profile"]["Name"])
        self.cars[car_id] = session_data
        self.async_set_updated_data(session_data)

    async def add_entities(self, session_data: dict) -> None:
        """CrÃ©er les entitÃ©s manquantes pour une voiture donnÃ©e."""
        car_name = session_data["profile"]["Name"]
        car_id = slugify(car_name)

        # MÃ©morise/rafraÃ®chit les derniÃ¨res donnÃ©es
        self.cars[car_id] = session_data

        device = DeviceInfo(
            identifiers={(DOMAIN, car_id)},
            manufacturer="Torque",
            model=car_name,
            name=car_name,
            sw_version=session_data["profile"].get("version"),
        )

        new_sensors: list[TorqueSensor] = []
        new_trackers: list[TorqueDeviceTracker] = []

        # --- Capteurs ---
        for key, meta in session_data.get("meta", {}).items():
            sensor_name = meta.get("name")
            tracked_key = f"{car_id}:{key}"

            # Ne pas crÃ©er de capteur pour les coordonnÃ©es (rÃ©servÃ© au device_tracker)
            if key in (TORQUE_GPS_LAT, TORQUE_GPS_LON):
                continue

            # CrÃ©er mÃªme si l'unitÃ© est vide
            if sensor_name and sensor_name != key and tracked_key not in self.tracked:
                new_sensors.append(TorqueSensor(self, self.entry, key, device))

        # --- Device tracker (GPS lat/lon requis) ---
        if (
            TORQUE_GPS_LAT in session_data
            and TORQUE_GPS_LON in session_data
            and f"{car_id}:{ENTITY_GPS}" not in self.tracked
        ):
            new_trackers.append(TorqueDeviceTracker(self, self.entry, device))

        sensor_cb_ready = callable(self.async_add_sensor)
        tracker_cb_ready = callable(self.async_add_device_tracker)

        if new_sensors and sensor_cb_ready:
            self.tracked.update(f"{car_id}:{s.sensor_key}" for s in new_sensors)
            self.async_add_sensor(new_sensors)
        elif new_sensors and not sensor_cb_ready:
            _LOGGER.debug(
                "Sensor platform not ready yet; will try again on next payload "
                "(%d sensors pending for %s).",
                len(new_sensors),
                car_name,
            )

        if new_trackers and tracker_cb_ready:
            self.tracked.update(f"{car_id}:{t.sensor_key}" for t in new_trackers)
            self.async_add_device_tracker(new_trackers)
        elif new_trackers and not tracker_cb_ready:
            _LOGGER.debug(
                "Device tracker platform not ready yet; will try again on next payload "
                "(%d trackers pending for %s).",
                len(new_trackers),
                car_name,
            )

        _LOGGER.debug("Tracked entities: %s", ", ".join(sorted(self.tracked)))

    # --------- Support suppression dâ€™un vÃ©hicule depuis lâ€™UI ----------
    def forget_vehicle(self, vehicle_key: str) -> None:
        """Oublier dÃ©finitivement un vÃ©hicule (clef = car_id)."""
        # Supprime les donnÃ©es mÃ©morisÃ©es
        self.cars.pop(vehicle_key, None)
        # Purge les capteurs/tracker associÃ©s
        to_remove = {k for k in self.tracked if k.startswith(f"{vehicle_key}:")}
        if to_remove:
            self.tracked.difference_update(to_remove)
        _LOGGER.debug("Forgot vehicle %s; removed %d tracked keys", vehicle_key, len(to_remove))

