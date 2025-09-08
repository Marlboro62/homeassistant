# -*- coding: utf-8 -*-
"""Sensor platform for Torque Logger."""
from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, List

from homeassistant.components.sensor import RestoreSensor
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er, device_registry as dr
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify

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

    ent_reg = er.async_get(hass)
    dev_reg = dr.async_get(hass)

    # --- Migration: corriger les anciens entity_id avec double préfixe <car>_<car>_ ---
    migrated = 0
    for er_ent in list(ent_reg.entities.values()):
        if er_ent.domain != SENSOR or not er_ent.entity_id.startswith("sensor."):
            continue
        device = dev_reg.async_get(er_ent.device_id) if er_ent.device_id else None
        if not device:
            continue
        car_slug = slugify(device.name or device.model or "")
        if not car_slug:
            continue
        dup_prefix = f"sensor.{car_slug}_{car_slug}_"
        if er_ent.entity_id.startswith(dup_prefix):
            new_entity_id = er_ent.entity_id.replace(f"{car_slug}_{car_slug}_", f"{car_slug}_", 1)
            try:
                ent_reg.async_update_entity(er_ent.entity_id, new_entity_id=new_entity_id)
                migrated += 1
                _LOGGER.info("Migrated entity_id %s -> %s", er_ent.entity_id, new_entity_id)
            except Exception as err:
                _LOGGER.debug("Migration failed for %s: %s", er_ent.entity_id, err)
    if migrated:
        _LOGGER.info("Torque Logger: %d entity_id migrated to remove double car prefix", migrated)
    # -------------------------------------------------------------------------------

    # Restauration des capteurs connus (basée sur unique_id stable)
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
                er_ent.unique_id[len(prefix):],
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

        # Métadonnées propres à la voiture
        meta_all = self.coordinator.get_meta(self._car_id)
        meta = meta_all.get(self.sensor_key, {}) if meta_all else {}

        # Libellé et unité toujours sûrs
        label = str(meta.get("name") or self.sensor_key or "value").strip()
        unit = (meta.get("unit") or "").strip() or None

        # Nom visible SANS préfix voiture (HA l'ajoute via has_entity_name=True)
        self._attr_name = label
        # Unité native
        self._attr_native_unit_of_measurement = unit

        # ID unique STABLE (ne dépend pas du libellé ni de la langue)
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}_{self._car_id}_{self.sensor_key}"

        # Icône
        self._set_icon()

        # Valeur restaurée éventuelle
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

        # Si pas de meta encore reçue pour cette voiture, restaure nom/unité
        if not self._attr_name:
            # Pas de préfixe voiture ici (évite les doublons), HA le fera via has_entity_name
            self._attr_name = state.name or self.sensor_key

        if self._attr_native_unit_of_measurement is None:
            self._attr_native_unit_of_measurement = native_state.native_unit_of_measurement

        self._set_icon()

    # ----------------- Helpers -----------------

    def _set_icon(self) -> None:
        """Choisit une icône cohérente selon le nom/sensor_key (FR/EN)."""
        name = (self._attr_name or "").lower()
        key = (self.sensor_key or "").lower()

        self._attr_icon = DEFAULT_ICON

        # Distance
        if re.search(r"\b(distance|kilometers?|miles?)\b", name) or "distance" in key:
            self._attr_icon = DISTANCE_ICON

        # Carburant
        if re.search(r"\b(fuel|carburant|litre|gallon)\b", name) or "fuel" in key:
            self._attr_icon = FUEL_ICON

        # Temps
        if re.search(r"\b(time|temps|idle)\b", name):
            self._attr_icon = TIME_ICON

        # Ville/route
        if re.search(r"\b(highway|autoroute)\b", name):
            self._attr_icon = HIGHWAY_ICON
        if re.search(r"\b(city|ville)\b", name):
            self._attr_icon = CITY_ICON

        # Vitesse (FR + EN + clé technique)
        if re.search(r"\b(speed|vitesse)\b", name) or key in ("speed", "gps_spd"):
            self._attr_icon = SPEED_ICON
