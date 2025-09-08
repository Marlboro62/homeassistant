"""Sensor platform for Torque Logger."""

import logging
import re
from typing import TYPE_CHECKING, List
from homeassistant.components.sensor import RestoreSensor
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers import entity_registry as er, device_registry as dr

from .const import (
    CITY_ICON,
    DISTANCE_ICON,
    DOMAIN,
    DEFAULT_ICON,
    FUEL_ICON,
    HIGHWAY_ICON,
    SENSOR,
    SPEED_ICON,
    TIME_ICON,
)
from .entity import TorqueEntity

if TYPE_CHECKING:
    from .coordinator import TorqueLoggerCoordinator


_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup sensor platform."""
    coordinator: "TorqueLoggerCoordinator" = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    coordinator.async_add_sensor = async_add_entities

    # Restore previously loaded sensors
    ent_reg = er.async_get(hass)
    dev_reg = dr.async_get(hass)

    devices = [
        device
        for device in dev_reg.devices.values()
        if any(ident[0] == DOMAIN for ident in device.identifiers)
    ]
    _LOGGER.debug("%d devices found for restore", len(devices))

    to_add: List[TorqueEntity] = []

    for device in devices:
        # car_id depuis l'identifier (DOMAIN, car_id)
        try:
            car_id = next(ident[1] for ident in device.identifiers if ident[0] == DOMAIN)
        except StopIteration:
            _LOGGER.debug("Skipping device without %s identifier: %s", DOMAIN, device.id)
            continue

        device_info = DeviceInfo(
            identifiers=device.identifiers,
            manufacturer=device.manufacturer,
            model=device.model,
            name=device.name,
            sw_version=device.sw_version,
        )

        # Reconstitue sensor_key depuis le unique_id stable
        prefix = f"{DOMAIN}_{entry.entry_id}_{car_id}_"
        restore_entities = [
            TorqueSensor(
                coordinator,
                entry,
                er_ent.unique_id[len(prefix) :],
                device_info,
            )
            for er_ent in ent_reg.entities.values()
            if er_ent.device_id == device.id
            and er_ent.domain == SENSOR
            and er_ent.unique_id
            and er_ent.unique_id.startswith(prefix)
        ]

        if restore_entities:
            _LOGGER.debug(
                "Restoring sensors for %s: %s",
                device.model,
                ", ".join(e.sensor_key for e in restore_entities),
            )
            to_add.extend(restore_entities)

    if to_add:
        async_add_entities(to_add)


class TorqueSensor(TorqueEntity, RestoreSensor):
    """Torque Sensor class."""

    def __init__(
        self,
        coordinator: "TorqueLoggerCoordinator",
        config_entry: ConfigEntry,
        sensor_key: str,
        device: DeviceInfo,
    ):
        super().__init__(coordinator, config_entry, sensor_key, device)

        # Lis les meta de TA voiture (pas la derniÃ¨re trame globale)
        meta = self.coordinator.get_meta(self._car_id)
        if meta and self.sensor_key in meta:
            self._attr_native_unit_of_measurement = meta[self.sensor_key].get("unit")
            self._attr_name = meta[self.sensor_key].get("name")
            self._set_icon()

        # Ne pas forcer entity_id : unique_id + nom suffisent
        self._restored_state = None

    @property
    def native_value(self):
        """Return the native value of the sensor (per car)."""
        value = self.coordinator.get_value(self._car_id, self.sensor_key)
        if value is not None:
            try:
                return round(float(value), 2)
            except (ValueError, TypeError):
                return None
        elif self._restored_state is not None:
            try:
                return round(float(self._restored_state), 2)
            except (ValueError, TypeError):
                return None
        else:
            return None

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        native_state = await self.async_get_last_sensor_data()
        if not state or not native_state:
            return

        _LOGGER.debug("Restore state of %s to %s", self.entity_id, native_state)
        self._restored_state = native_state.native_value

        # Si pas de meta encore reÃ§ue pour cette voiture, restaure nom/unitÃ©
        if self._attr_name is None:
            self._attr_name = state.name
        if self._attr_native_unit_of_measurement is None:
            self._attr_native_unit_of_measurement = native_state.native_unit_of_measurement

        self._set_icon()

    def _set_icon(self) -> None:
        name = self._attr_name or ""
        self._attr_icon = DEFAULT_ICON
        if re.search(r"kilometers|miles", name, re.IGNORECASE):
            self._attr_icon = DISTANCE_ICON
        if re.search(r"litre|gallon", name, re.IGNORECASE):
            self._attr_icon = FUEL_ICON
        if re.search(r"distance", name, re.IGNORECASE):
            self._attr_icon = DISTANCE_ICON
        if re.search(r"time|idle", name, re.IGNORECASE):
            self._attr_icon = TIME_ICON
        if re.search(r"highway", name, re.IGNORECASE):
            self._attr_icon = HIGHWAY_ICON
        if re.search(r"city", name, re.IGNORECASE):
            self._attr_icon = CITY_ICON
        if re.search(r"speed", name, re.IGNORECASE):
            self._attr_icon = SPEED_ICON

