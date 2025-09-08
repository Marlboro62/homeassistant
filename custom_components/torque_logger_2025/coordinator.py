# -*- coding: utf-8 -*-
"""Torque Logger Coordinator."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers import device_registry as dr
from homeassistant.util import slugify

from .sensor import TorqueSensor
from .device_tracker import TorqueDeviceTracker
from .const import DOMAIN, ENTITY_GPS, TORQUE_GPS_LAT, TORQUE_GPS_LON

if TYPE_CHECKING:
    from .api import TorqueReceiveDataView

_LOGGER: logging.Logger = logging.getLogger(__package__)


def _looks_like_hex_hash(text: str) -> bool:
    """True si `text` est un hash hexadécimal de 32 caractères."""
    if not isinstance(text, str):
        return False
    t = text.strip()
    return len(t) == 32 and all(c in "0123456789abcdef" for c in t.lower())


class TorqueLoggerCoordinator(DataUpdateCoordinator):
    """Gère l’état et la création des entités Torque."""

    # Renseignés par les plateformes lors de leur setup
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

        # Capteurs déjà créés (par véhicule) via clef "<vehicle_key>:<sensor_key>"
        self.tracked: set[str] = set()
        # Dernières données reçues par véhicule (vehicle_key -> session_data)
        self.cars: dict[str, dict] = {}

    async def _async_update_data(self):
        """Aucune mise à jour planifiée : on est en push uniquement."""
        return None

    # ---------- Helpers ----------
    def _vehicle_key(self, profile: dict) -> str:
        """Clé stable de l'appareil: entry_id + id (fallback: slug du Name)."""
        raw_id = profile.get("id")
        if raw_id:
            base = str(raw_id).strip()
        else:
            base = slugify(profile.get("Name", "vehicle"))
        return f"{self.entry.entry_id}:{base}"

    # ---------- Lecture de données ----------
    def get_value(self, car_key: str, key: str):
        data = self.cars.get(car_key)
        if not data:
            return None
        return data.get(key)

    def get_meta(self, car_key: str) -> dict:
        data = self.cars.get(car_key)
        if not data:
            return {}
        return data.get("meta", {})

    # ---------- Réception depuis l’API ----------
    def update_from_session(self, session_data: dict) -> None:
        """Appelé par l’API quand un nouveau payload est parsé."""
        profile = session_data["profile"]
        car_key = self._vehicle_key(profile)
        self.cars[car_key] = session_data
        self.async_set_updated_data(session_data)

    async def add_entities(self, session_data: dict) -> None:
        """Créer les entités manquantes pour un véhicule donné."""
        profile = session_data["profile"]
        raw_name = profile.get("Name") or "Vehicle"

        # Alias lisible si le nom ressemble à un hash
        display_name = raw_name
        if _looks_like_hex_hash(raw_name):
            base = (profile.get("id") or raw_name)[:6]
            display_name = f"Véhicule {base}"

        car_key = self._vehicle_key(profile)

        # Mémorise/rafraîchit les dernières données
        self.cars[car_key] = session_data

        device = DeviceInfo(
            identifiers={(DOMAIN, car_key)},  # <-- clé stable
            manufacturer="Torque",
            model=display_name,
            name=display_name,
            sw_version=profile.get("version"),
        )

        # Si le device existe déjà et que le nom a changé -> on le renomme
        try:
            dev_reg = dr.async_get(self.hass)
            dev = dev_reg.async_get_device(identifiers={(DOMAIN, car_key)})
            if dev and (dev.name != display_name or dev.model != display_name):
                dev_reg.async_update_device(dev.id, name=display_name, model=display_name)
        except Exception:  # pas bloquant
            _LOGGER.debug("Device rename skipped for %s", car_key)

        new_sensors: list[TorqueSensor] = []
        new_trackers: list[TorqueDeviceTracker] = []

        # --- Capteurs ---
        for key, meta in session_data.get("meta", {}).items():
            sensor_name = meta.get("name")
            tracked_key = f"{car_key}:{key}"

            # Ne pas créer de capteur pour les coordonnées (réservé au device_tracker)
            if key in (TORQUE_GPS_LAT, TORQUE_GPS_LON):
                continue

            # On crée même si l'unité est vide (certains PIDs n'ont pas d'unité)
            if sensor_name and sensor_name != key and tracked_key not in self.tracked:
                new_sensors.append(TorqueSensor(self, self.entry, key, device))

        # --- Device tracker (GPS lat/lon requis) ---
        if (
            TORQUE_GPS_LAT in session_data
            and TORQUE_GPS_LON in session_data
            and f"{car_key}:{ENTITY_GPS}" not in self.tracked
        ):
            new_trackers.append(TorqueDeviceTracker(self, self.entry, device))

        sensor_cb_ready = callable(self.async_add_sensor)
        tracker_cb_ready = callable(self.async_add_device_tracker)

        if new_sensors and sensor_cb_ready:
            self.tracked.update(f"{car_key}:{s.sensor_key}" for s in new_sensors)
            self.async_add_sensor(new_sensors)
        elif new_sensors and not sensor_cb_ready:
            _LOGGER.debug(
                "Sensor platform not ready yet; will try again on next payload "
                "(%d sensors pending for %s).",
                len(new_sensors),
                display_name,
            )

        if new_trackers and tracker_cb_ready:
            self.tracked.update(f"{car_key}:{t.sensor_key}" for t in new_trackers)
            self.async_add_device_tracker(new_trackers)
        elif new_trackers and not tracker_cb_ready:
            _LOGGER.debug(
                "Device tracker platform not ready yet; will try again on next payload "
                "(%d trackers pending for %s).",
                len(new_trackers),
                display_name,
            )

        _LOGGER.debug("Tracked entities: %s", ", ".join(sorted(self.tracked)))

    # ---------- Support suppression d’un véhicule depuis l’UI ----------
    def forget_vehicle(self, vehicle_key: str) -> None:
        """Oublier définitivement un véhicule (clef = vehicle_key)."""
        # Supprime les données mémorisées
        self.cars.pop(vehicle_key, None)
        # Purge les capteurs/tracker associés
        to_remove = {k for k in self.tracked if k.startswith(f"{vehicle_key}:")}
        if to_remove:
            self.tracked.difference_update(to_remove)
        _LOGGER.debug("Forgot vehicle %s; removed %d tracked keys", vehicle_key, len(to_remove))
