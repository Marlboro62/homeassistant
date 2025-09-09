# -*- coding: utf-8 -*-
"""Torque Entity class for Torque Logger 2025."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Iterable, Tuple, Mapping, Any

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo  # TypedDict (annotation)

from .const import DOMAIN, ATTRIBUTION

if TYPE_CHECKING:
    from .coordinator import TorqueLoggerCoordinator


def _get_attr_or_key(obj: Any, attr: str, key: str):
    """Retourne obj.attr si dispo, sinon obj[key] si obj est mapping."""
    if hasattr(obj, attr):
        return getattr(obj, attr)
    if isinstance(obj, Mapping):
        return obj.get(key)
    return None


def _extract_identifiers(device: Any) -> Optional[Iterable[Tuple[str, str]]]:
    """Récupère la collection identifiers (objet avec attributs ou dict)."""
    ids = _get_attr_or_key(device, "identifiers", "identifiers")
    return ids  # attendu: set[tuple[str,str]] (ou équivalent itérable)


def _extract_car_id(device: Any) -> str:
    """Trouve (DOMAIN, car_id) dans identifiers, avec fallback rétro-compatible."""
    identifiers = _extract_identifiers(device)
    if identifiers:
        for ident in identifiers:
            if isinstance(ident, tuple) and len(ident) >= 2 and ident[0] == DOMAIN and ident[1]:
                return ident[1]
        # Fallback: 2e élément du 1er tuple rencontré (ancienne logique)
        first = next(iter(identifiers), None)
        if isinstance(first, tuple) and len(first) >= 2 and first[1]:
            return first[1]
    return "unknown"


def _coerce_device_info(device: Any, car_id: str) -> DeviceInfo:
    """Renvoie un DeviceInfo (TypedDict) prêt pour HA.
    - Si device est déjà un Mapping → on copie et on s'assure que 'identifiers' existe
    - Sinon on reconstruit depuis les attributs
    """
    if isinstance(device, Mapping):
        out = dict(device)  # shallow copy
        out.setdefault("identifiers", {(DOMAIN, car_id)})
        # clefs optionnelles: manufacturer/model/name/sw_version — on laisse telles quelles si absentes
        return out  # type: ignore[return-value]

    # Cas objet: reconstruit en dict DeviceInfo
    identifiers = _extract_identifiers(device) or {(DOMAIN, car_id)}
    manufacturer = _get_attr_or_key(device, "manufacturer", "manufacturer")
    model = _get_attr_or_key(device, "model", "model")
    name = _get_attr_or_key(device, "name", "name")
    sw_version = _get_attr_or_key(device, "sw_version", "sw_version")
    return {
        "identifiers": identifiers,
        "manufacturer": manufacturer,
        "model": model,
        "name": name,
        "sw_version": sw_version,
    }  # type: ignore[return-value]


class TorqueEntity(CoordinatorEntity):
    """Base entity for Torque Logger."""

    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: "TorqueLoggerCoordinator",
        config_entry: ConfigEntry,
        sensor_key: str,
        device: DeviceInfo | Mapping[str, Any] | Any,
    ) -> None:
        super().__init__(coordinator)

        self.config_entry = config_entry
        self.sensor_key = sensor_key

        # ID & nom véhicule (fonctionnent pour dict ou objet)
        self._car_id = _extract_car_id(device)
        model = _get_attr_or_key(device, "model", "model")
        name = _get_attr_or_key(device, "name", "name")
        self._car_name = model or name or "Vehicle"

        # Fournir à HA un vrai DeviceInfo (dict)
        self._attr_device_info = _coerce_device_info(device, self._car_id)

        # Unique ID stable (entrée + véhicule + capteur)
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}_{self._car_id}_{sensor_key}"

        # Attribution + attributs additionnels
        self._attr_attribution = ATTRIBUTION
        self._attr_extra_state_attributes = {"car": self._car_name}
