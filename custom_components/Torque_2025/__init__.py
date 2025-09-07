"""The torque component."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

DOMAIN = "torque"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Torque integration."""
    # Ici on ne fait rien de particulier à la config.yaml
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Torque from a config entry."""
    # On demande de charger la plateforme sensor via la config entry
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")
