# -*- coding: utf-8 -*-
"""Torque Entity class for Torque Logger 2025."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Tuple, Optional
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN, ATTRIBUTION

if TYPE_CHECKING:
    from .coordinator import TorqueLoggerCoordinator


def _extract_car_id(device: DeviceInfo) -> str:
    """Find our (DOMAIN, car_id) tuple inside device.identifiers."""
    identifiers: Optional[Iterable[Tuple[str, str]]] = getattr(device, "identifiers", None)
    if not identifiers:
        return "unknown"

    # identifiers est un set de tuples (domain, id)
    for ident in identifiers:
        if isinstance(ident, tuple) and len(ident) >= 2 and ident[0] == DOMAIN:
            return ident[1]

    # Fallback: premier tuple s'il existe
    first = next(iter(identifiers), None)
    if isinstance(first, tuple) and len(first) >= 2:
        return first[1]
    return "unknown"


class TorqueEntity(CoordinatorEntity):
    """Base Entity"""

    _attr_should_poll = False
    # IMPORTANT : on laisse HA préfixer visuellement par le nom de l'appareil
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: "TorqueLoggerCoordinator",
        config_entry: ConfigEntry,
        sensor_key: str,
        device: DeviceInfo,
    ):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.sensor_key = sensor_key

        # DeviceInfo est un objet (dataclass-like)
        self._car_id = _extract_car_id(device)
        self._car_name = getattr(device, "name", None) or getattr(device, "model", None) or "Vehicle"

        # Expose DeviceInfo tel quel à Home Assistant
        self._attr_device_info = device
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}_{self._car_id}_{sensor_key}"
        self._attr_attribution = ATTRIBUTION
        self._attr_extra_state_attributes = {"car": self._car_name}

        # Laisser le nom None ici : les sous-classes définiront un libellé “pur”
        self._attr_name = None
