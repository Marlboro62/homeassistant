"""The Torque Logger integration with Home Assistant."""
from __future__ import annotations

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry

from .coordinator import TorqueLoggerCoordinator
from .api import TorqueReceiveDataView
from .const import (
    CONF_EMAIL,
    CONF_IMPERIAL,
    CONF_LANGUAGE,
    DEFAULT_LANGUAGE,
    DOMAIN,
    PLATFORMS,
    STARTUP_MESSAGE,
)

_LOGGER: logging.Logger = logging.getLogger(__name__)


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

    # Vue HTTP : la créer UNE fois, puis seulement MAJ de ses paramètres
    if "view" not in domain_store:
        view = TorqueReceiveDataView(data={}, email=email, imperial=imperial, language=language)
        hass.http.register_view(view)
        domain_store["view"] = view
        _LOGGER.debug("Torque view registered at %s", view.url)
    else:
        view: TorqueReceiveDataView = domain_store["view"]
        view.email = email or ""
        view.imperial = bool(imperial)
        view.lang = (language or DEFAULT_LANGUAGE).lower()
        _LOGGER.debug("Torque view updated (email=%s, imperial=%s, lang=%s)", view.email, view.imperial, view.lang)

    # Store par entrée
    store: dict = {"data": {}}  # buffer session si tu veux l’exploiter côté vue
    domain_store[entry.entry_id] = store

    # Si tu veux que la vue partage ce buffer (facultatif, utile en multi-sessions Torque)
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
        *[hass.config_entries.async_forward_entry_unload(entry, platform) for platform in PLATFORMS]
    )
    unloaded = all(results)
    if not unloaded:
        return False

    if DOMAIN not in hass.data:
        return True

    domain_store: dict = hass.data[DOMAIN]

    # Détache et purge le cache de cette entry
    store = domain_store.pop(entry.entry_id, None)

    # S'il ne reste plus aucune entry active, on garde la vue enregistrée
    # mais on la met au neutre pour éviter toute réutilisation de vieux pointeurs.
    still_has_entries = any(k for k in domain_store.keys() if k != "view")
    view: TorqueReceiveDataView | None = domain_store.get("view")

    if view and not still_has_entries:
        view.coordinator = None
        view.data = {}
        _LOGGER.debug("Torque view kept registered but detached (no active entries).")

    # Ne PAS faire: domain_store.pop('view', ...) ni hass.data.pop(DOMAIN, ...)
    # afin d'éviter des ré-enregistrements de route pendant le runtime.

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
    """Autoriser la suppression d’un appareil (véhicule) depuis l’UI.

    - Nettoie le cache du coordinator pour ce véhicule
    - Retourne True pour que HA supprime l’appareil + entités associées
    """
    _LOGGER.debug("Removing device identifiers=%s", device_entry.identifiers)

    try:
        coordinator: TorqueLoggerCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    except KeyError:
        # Rien à nettoyer, mais on autorise la suppression dans l’UI
        return True

    # Identifiants posés dans DeviceInfo.identifiers => (DOMAIN, <vehicle_key>)
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
