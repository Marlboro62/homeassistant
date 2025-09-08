# -*- coding: utf-8 -*-
"""Device tracker for Torque Logger 2025."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Dict, Any
import logging

from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.components.device_tracker.const import SourceType as TrackerSourceType

from homeassistant.const import (
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    ATTR_GPS_ACCURACY,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers import device_registry as dr

from .entity import TorqueEntity
from .const import (
    ATTR_ALTITUDE,
    DOMAIN,
    ENTITY_GPS,
    GPS_ICON,
    TORQUE_GPS_ACCURACY,
    TORQUE_GPS_LAT,
    TORQUE_GPS_LON,
)

# URL d'image personnalisée : on essaye d'abord de l'importer depuis const.py,
# sinon on utilise un fallback direct.
try:
    from .const import ENTITY_PICTURE_URL  # type: ignore
except Exception:
    ENTITY_PICTURE_URL = "https://brands.home-assistant.io/tarif_edf/dark_icon.png"

if TYPE_CHECKING:
    from .coordinator import TorqueLoggerCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup device_tracker platform."""
    coordinator: "TorqueLoggerCoordinator" = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    coordinator.async_add_device_tracker = async_add_entities

    # Restaurer les trackers déjà connus
    dev_reg = dr.async_get(hass)
    devices = [
        device
        for device in dev_reg.devices.values()
        if any(ident[0] == DOMAIN for ident in device.identifiers)
    ]
    _LOGGER.debug("%d device_tracker to restore", len(devices))

    for device in devices:
        _LOGGER.debug("Restoring %s device_tracker", device.model)
        device_info = DeviceInfo(
            identifiers=device.identifiers,
            manufacturer=device.manufacturer,
            model=device.model,
            name=device.name,
            sw_version=device.sw_version,
        )
        async_add_entities([TorqueDeviceTracker(coordinator, entry, device_info)])


class TorqueDeviceTracker(TorqueEntity, TrackerEntity, RestoreEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: "TorqueLoggerCoordinator", config_entry: ConfigEntry, device: DeviceInfo):
        super().__init__(coordinator, config_entry, ENTITY_GPS, device)
        self._attr_name = self._car_name
        self._attr_icon = GPS_ICON
        self._attr_entity_picture = ENTITY_PICTURE_URL
        self._restored_state: Optional[Dict[str, Any]] = None

    # --- Helpers internes -------------------------------------------------

    def _get_float(self, value) -> Optional[float]:
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _get_for_car(self, key) -> Optional[float]:
        """Récupère et convertit en float la valeur du coordinator pour CE véhicule."""
        val = self.coordinator.get_value(self._car_id, key)
        return self._get_float(val) if val is not None else None

    # --- Propriétés device_tracker ---------------------------------------

    @property
    def source_type(self) -> TrackerSourceType:
        """Return the source type, eg gps or router, of the device."""
        return TrackerSourceType.GPS

    @property
    def battery_level(self) -> Optional[int]:
        """Return the battery level of the device."""
        return None

    @property
    def latitude(self) -> Optional[float]:
        """Return latitude value of the device (spécifique au véhicule)."""
        val = self._get_for_car(TORQUE_GPS_LAT)
        if val is not None:
            return val
        if self._restored_state and self._restored_state.get(ATTR_LATITUDE) is not None:
            return self._get_float(self._restored_state[ATTR_LATITUDE])
        return None

    @property
    def longitude(self) -> Optional[float]:
        """Return longitude value of the device (spécifique au véhicule)."""
        val = self._get_for_car(TORQUE_GPS_LON)
        if val is not None:
            return val
        if self._restored_state and self._restored_state.get(ATTR_LONGITUDE) is not None:
            return self._get_float(self._restored_state[ATTR_LONGITUDE])
        return None

    @property
    def location_accuracy(self) -> int:
        """Return the gps accuracy (meters) — NEVER None (HA >= 2025.x requirement)."""
        # 1/ donnée live pour CE véhicule
        val = self._get_for_car(TORQUE_GPS_ACCURACY)
        if val is not None:
            try:
                return int(float(val))
            except (ValueError, TypeError):
                pass
        # 2/ restauration
        if self._restored_state and self._restored_state.get(ATTR_GPS_ACCURACY) is not None:
            try:
                return int(float(self._restored_state[ATTR_GPS_ACCURACY]))
            except (ValueError, TypeError):
                pass
        # 3/ défaut sûr pour éviter TypeError dans zone.async_active_zone
        return 0

    @property
    def available(self) -> bool:
        """L'entité n'est disponible que si on a au moins une paire lat/lon."""
        return self.latitude is not None and self.longitude is not None

    # --- Cycle de vie -----------------------------------------------------

    async def async_added_to_hass(self) -> None:
        """Call when entity about to be added to Home Assistant."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        if state is None:
            _LOGGER.debug("No previous state for %s", self.entity_id)
            return

        attr = state.attributes
        _LOGGER.debug("Restored state for %s", self.entity_id)
        self._restored_state = {
            ATTR_ALTITUDE: attr.get(ATTR_ALTITUDE),
            ATTR_LATITUDE: attr.get(ATTR_LATITUDE),
            ATTR_LONGITUDE: attr.get(ATTR_LONGITUDE),
            ATTR_GPS_ACCURACY: attr.get(ATTR_GPS_ACCURACY),
        }
