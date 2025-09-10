# -*- coding: utf-8 -*-
"""Device tracker for Torque Logger 2025."""

from typing import TYPE_CHECKING, Optional, Dict, Any
import logging

# Recommandé (docs 2025) :
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.components.device_tracker.const import SourceType as TrackerSourceType

from homeassistant.const import (
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    ATTR_GPS_ACCURACY,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
    # noqa
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers import device_registry as dr

from .entity import TorqueEntity
from .const import (
    ATTR_ALTITUDE,
    ATTR_SPEED,
    ATTR_GPS_TIME,
    DOMAIN,
    ENTITY_GPS,
    GPS_ICON,
    TORQUE_GPS_ACCURACY,
    TORQUE_GPS_LAT,
    TORQUE_GPS_LON,
    TORQUE_GPS_ALTITUDE,  # altitude
)

if TYPE_CHECKING:
    from .coordinator import TorqueLoggerCoordinator

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup device_tracker platform."""
    coordinator: "TorqueLoggerCoordinator" = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    coordinator.async_add_device_tracker = async_add_entities

    # Restore previously loaded trackers
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
        # Plus d'image personnalisée : on laisse Home Assistant afficher l'icône
        self._restored_state: Optional[Dict[str, Any]] = None

    @property
    def battery_level(self) -> Optional[int]:
        """Return the battery level of the device."""
        return None

    @property
    def location_accuracy(self) -> float:
        """Return GPS accuracy in meters (float)."""
        val = self.coordinator.get_value(self._car_id, TORQUE_GPS_ACCURACY)
        if val is not None:
            try:
                return float(val)
            except (ValueError, TypeError):
                pass

        # fallback sur l'état restauré
        if self._restored_state and self._restored_state.get(ATTR_GPS_ACCURACY) is not None:
            try:
                return float(self._restored_state[ATTR_GPS_ACCURACY])
            except (ValueError, TypeError):
                pass

        return 0.0  # défaut attendu en 2025

    @property
    def latitude(self) -> Optional[float]:
        """Return latitude value of the device."""
        val = self.coordinator.get_value(self._car_id, TORQUE_GPS_LAT)
        if val is not None:
            try:
                return float(val)
            except (ValueError, TypeError):
                return None

        if self._restored_state and self._restored_state.get(ATTR_LATITUDE) is not None:
            try:
                return float(self._restored_state[ATTR_LATITUDE])
            except (ValueError, TypeError):
                return None
        return None

    @property
    def longitude(self) -> Optional[float]:
        """Return longitude value of the device."""
        val = self.coordinator.get_value(self._car_id, TORQUE_GPS_LON)
        if val is not None:
            try:
                return float(val)
            except (ValueError, TypeError):
                return None

        if self._restored_state and self._restored_state.get(ATTR_LONGITUDE) is not None:
            try:
                return float(self._restored_state[ATTR_LONGITUDE])
            except (ValueError, TypeError):
                return None
        return None

    @property
    def source_type(self) -> TrackerSourceType:
        """Return the source type, eg gps or router, of the device."""
        return TrackerSourceType.GPS

    @property
    def extra_state_attributes(self) -> Dict[str, Any] | None:
        """Expose altitude, vitesse et horaire GPS en attributs supplémentaires."""
        attrs: Dict[str, Any] = {}

        # Altitude
        alt = self.coordinator.get_value(self._car_id, TORQUE_GPS_ALTITUDE)
        if alt is not None:
            try:
                attrs[ATTR_ALTITUDE] = float(alt)
            except (ValueError, TypeError):
                pass
        elif self._restored_state and self._restored_state.get(ATTR_ALTITUDE) is not None:
            try:
                attrs[ATTR_ALTITUDE] = float(self._restored_state[ATTR_ALTITUDE])
            except (ValueError, TypeError):
                pass

        # Vitesse (si disponible côté payload, ex. shortName "speed")
        spd = self.coordinator.get_value(self._car_id, ATTR_SPEED)
        if spd is not None:
            try:
                attrs[ATTR_SPEED] = float(spd)
            except (ValueError, TypeError):
                pass
        elif self._restored_state and self._restored_state.get(ATTR_SPEED) is not None:
            try:
                attrs[ATTR_SPEED] = float(self._restored_state[ATTR_SPEED])
            except (ValueError, TypeError):
                pass

        # Horodatage GPS : la vue met "time" au niveau racine → map vers ATTR_GPS_TIME
        gps_time = self.coordinator.get_value(self._car_id, "time")
        if gps_time is not None:
            try:
                attrs[ATTR_GPS_TIME] = int(gps_time)
            except (ValueError, TypeError):
                pass
        elif self._restored_state and self._restored_state.get(ATTR_GPS_TIME) is not None:
            try:
                attrs[ATTR_GPS_TIME] = int(self._restored_state[ATTR_GPS_TIME])
            except (ValueError, TypeError):
                pass

        return attrs or None

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
            ATTR_SPEED: attr.get(ATTR_SPEED),
            ATTR_GPS_TIME: attr.get(ATTR_GPS_TIME),
        }
