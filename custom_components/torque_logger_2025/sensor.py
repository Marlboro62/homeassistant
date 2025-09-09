# -*- coding: utf-8 -*-
"""Sensor platform for Torque Logger 2025."""

from __future__ import annotations

import logging
import re
import math
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

    to_add: List["TorqueSensor"] = []

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


# --- Helpers -----------------------------------------------------------------

def _to_finite_float(val):
    """Retourne un float fini ou None (filtre NaN/±inf et erreurs de cast)."""
    try:
        f = float(val)
    except (ValueError, TypeError):
        return None
    return f if math.isfinite(f) else None


def _title_from_key(key: str) -> str:
    """Nom lisible par défaut à partir d'une clé slug (fallback si pas de meta)."""
    s = key.replace("_", " ").strip()
    # petites normalisations usuelles
    s = re.sub(r"\bkmh\b", "km/h", s, flags=re.I)
    s = re.sub(r"\bkph\b", "km/h", s, flags=re.I)
    return s[:1].upper() + s[1:]


# --- Entity ------------------------------------------------------------------

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

        # Toujours initialiser pour éviter AttributeError
        self._attr_name = None
        self._attr_native_unit_of_measurement = None
        self._attr_icon = DEFAULT_ICON
        self._restored_state = None

        # 1) Essaye d'abord les métadonnées de la voiture
        meta = self.coordinator.get_meta(self._car_id)
        if meta and self.sensor_key in meta:
            self._attr_native_unit_of_measurement = meta[self.sensor_key].get("unit")
            self._attr_name = meta[self.sensor_key].get("name")

        # 2) Sinon, nom de secours depuis la clé
        if self._attr_name is None:
            self._attr_name = _title_from_key(self.sensor_key)

        self._set_icon()

    # --- Rafraîchissement dynamique des métadonnées quand le coordinator bouge

    def _maybe_refresh_metadata(self) -> None:
        """Si meta fournit name/unit pour ce capteur, mets à jour et pousse l'état."""
        meta = self.coordinator.get_meta(self._car_id)
        if not meta or self.sensor_key not in meta:
            return
        m = meta[self.sensor_key]
        changed = False

        new_name = m.get("name")
        if new_name and new_name != self._attr_name:
            self._attr_name = new_name
            changed = True

        new_unit = m.get("unit")
        if new_unit and new_unit != self._attr_native_unit_of_measurement:
            self._attr_native_unit_of_measurement = new_unit
            changed = True

        if changed:
            self._set_icon()
            self.async_write_ha_state()

    def _handle_coordinator_update(self) -> None:
        """Appelé à chaque update du CoordinatorEntity."""
        self._maybe_refresh_metadata()
        super()._handle_coordinator_update()

    # --- Valeur native (avec filtre inf/NaN)

    @property
    def native_value(self):
        """Return the native value of the sensor (per car)."""
        value = self.coordinator.get_value(self._car_id, self.sensor_key)

        f = _to_finite_float(value)
        if f is not None:
            return round(f, 2)

        # fallback sur l'état restauré (si c'est numérique et fini)
        if self._restored_state is not None:
            f = _to_finite_float(self._restored_state)
            if f is not None:
                return round(f, 2)

        # Sinon, pas de valeur exploitable → état indisponible
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

        # Si pas de meta encore reçue pour cette voiture, restaure nom/unité
        if self._attr_name is None:
            self._attr_name = state.name or _title_from_key(self.sensor_key)
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
