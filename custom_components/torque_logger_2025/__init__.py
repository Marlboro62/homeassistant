# -*- coding: utf-8 -*-
"""The Torque Logger 2025 integration with Home Assistant."""
from __future__ import annotations

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry

from .coordinator import TorqueLoggerCoordinator
from .api import TorqueReceiveDataView
from .const import (
    DOMAIN,
    PLATFORMS,
    STARTUP_MESSAGE,
    CONF_EMAIL,
    CONF_IMPERIAL,
    CONF_LANGUAGE,
    DEFAULT_LANGUAGE,
    RUNTIME_LANG_MAP,
)

_LOGGER: logging.Logger = logging.getLogger(__name__)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old entry data to the latest version.

    - v<2 -> v2 : injecte la langue par défaut si absente.
    """
    if entry.version < 2:
        data = dict(entry.data)
        if CONF_LANGUAGE not in data:
            data[CONF_LANGUAGE] = DEFAULT_LANGUAGE
        hass.config_entries.async_update_entry(entry, data=data, version=2)
        _LOGGER.debug("Migrated config entry %s to version 2", entry.entry_id)
    return True


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """YAML setup is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration via the UI."""
    # Espace de stockage du domaine
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
        _LOGGER.info(STARTUP_MESSAGE)

    domain_store: dict = hass.data[DOMAIN]

    # Données + options (fallback sur data)
    email = entry.data.get(CONF_EMAIL, "")
    imperial = entry.options.get(CONF_IMPERIAL, entry.data.get(CONF_IMPERIAL, False))
    language = entry.options.get(CONF_LANGUAGE, entry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE))

    # Normalisation de la langue côté runtime (API ne gère que fr/en pour l’instant)
    sel = (language or DEFAULT_LANGUAGE).lower()
    lang_rt = RUNTIME_LANG_MAP.get(sel, "en")

    # Vue HTTP : la créer UNE fois, puis seulement MAJ de ses paramètres
    if "view" not in domain_store:
        view = TorqueReceiveDataView(data={}, email=email, imperial=imperial, language=lang_rt)
        hass.http.register_view(view)
        domain_store["view"] = view
        _LOGGER.debug("Torque view registered at %s", view.url)
    else:
        view: TorqueReceiveDataView = domain_store["view"]
        view.email = email or ""
        view.imperial = bool(imperial)
        view.lang = lang_rt
        _LOGGER.debug(
            "Torque view updated (email=%s, imperial=%s, lang=%s)",
            view.email, view.imperial, view.lang,
        )

    # Store par entrée
    store: dict = {"data": {}}
    domain_store[entry.entry_id] = store

    # Partage du buffer de session avec la vue
    domain_store["view"].data = store["data"]

    # Coordinator
    coordinator = TorqueLoggerCoordinator(hass, domain_store["view"], entry)
    domain_store["view"].coordinator = coordinator
    store["coordinator"] = coordinator

    # Charger les plateformes
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Reload si options changent
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload platforms and detach this entry from the view/coordinator."""
    results = await asyncio.gather(
        *[
            hass.config_entries.async_forward_entry_unload(entry, platform)
            for platform in PLATFORMS
        ]
    )
    if not all(results):
        return False

    if DOMAIN not in hass.data:
        return True

    domain_store: dict = hass.data[DOMAIN]
    domain_store.pop(entry.entry_id, None)

    still_has_entries = any(k for k in domain_store.keys() if k != "view")
    view: TorqueReceiveDataView | None = domain_store.get("view")

    if view and not still_has_entries:
        view.coordinator = None
        view.data = {}
        _LOGGER.debug("Torque view kept registered but detached (no active entries).")

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_remove_config_entry_device(
    hass: HomeAssistant,
    entry: ConfigEntry,
    device_entry: DeviceEntry,
) -> bool:
    """Autoriser la suppression d’un appareil (véhicule) depuis l’UI."""
    _LOGGER.debug("Removing device identifiers=%s", device_entry.identifiers)

    try:
        coordinator: TorqueLoggerCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    except KeyError:
        return True

    vehicle_keys = [id2 for (dom, id2) in device_entry.identifiers if dom == DOMAIN]

    for vkey in vehicle_keys:
        forget = getattr(coordinator, "forget_vehicle", None)
        if callable(forget):
            try:
                forget(vkey)
                _LOGGER.debug("Vehicle %s forgotten in coordinator", vkey)
            except Exception as err:
                _LOGGER.debug("forget_vehicle(%s) failed: %s", vkey, err)

    return True
