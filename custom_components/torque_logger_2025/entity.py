"""Torque Entity class"""

from typing import TYPE_CHECKING, Iterable, Tuple, Optional
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN, ATTRIBUTION

if TYPE_CHECKING:
    from .coordinator import TorqueLoggerCoordinator


def _extract_car_id(device: DeviceInfo) -> str:
    """Find our (DOMAIN, car_id) tuple inside device['identifiers']."""
    identifiers: Optional[Iterable[Tuple[str, str]]] = device.get("identifiers")  # type: ignore[assignment]
    if not identifiers:
        return "unknown"
    for ident in identifiers:
        # ident is typically a tuple like (DOMAIN, car_id)
        if isinstance(ident, tuple) and len(ident) >= 2 and ident[0] == DOMAIN:
            return ident[1]
    # Fallback: take first tuple's second element if present
    first = next(iter(identifiers), None)
    if isinstance(first, tuple) and len(first) >= 2:
        return first[1]
    return "unknown"


class TorqueEntity(CoordinatorEntity):
    """Base Entity"""

    _attr_should_poll = False
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

        # DeviceInfo est un dict (TypedDict), pas un objet
        self._car_id = _extract_car_id(device)
        self._car_name = device.get("model") or "Vehicle"  # type: ignore[assignment]

        # Expose DeviceInfo tel quel (dict) Ã  Home Assistant
        self._attr_device_info = device
        self._attr_unique_id = f"{DOMAIN}_{config_entry.entry_id}_{self._car_id}_{sensor_key}"
        self._attr_attribution = ATTRIBUTION
        self._attr_extra_state_attributes = {"car": self._car_name}

