# -*- coding: utf-8 -*-
"""Adds config flow for Torque Logger 2025."""
from __future__ import annotations

from typing import Iterable

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)
import voluptuous as vol

from .const import (
    NAME,
    DOMAIN,
    CONF_EMAIL,
    CONF_IMPERIAL,
    CONF_LANGUAGE,
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGS,  # e.g. ("en","fr","fr-CA","en-GB",...)
)


def _codes_from_supported_langs(supported) -> list[str]:
    """Return a list of language codes from SUPPORTED_LANGS whatever its type."""
    if isinstance(supported, (list, tuple, set)):
        return list(supported)
    if isinstance(supported, dict):
        # if someone made it a mapping, keep keys
        return list(supported.keys())
    # last resort
    return [str(supported)]


# Lightweight labels (pas de dépendance i18n ici)
_LANG_LABELS = {
    "ar": "العربية", "de": "Deutsch", "en": "English", "en-AU": "English (AU)",
    "en-GB": "English (UK)", "es": "Español", "fr": "Français",
    "fr-CA": "Français (CA)", "hi": "हिन्दी", "id": "Indonesia", "it": "Italiano",
    "ja": "日本語", "ko": "한국어", "nl": "Nederlands", "pl": "Polski",
    "pt-BR": "Português (BR)", "pt-PT": "Português (PT)", "ru": "Русский",
    "th": "ไทย", "tr": "Türkçe", "vi": "Tiếng Việt", "zh-Hans": "简体中文",
    "bg": "Български", "cs": "Čeština", "da": "Dansk", "el": "Ελληνικά",
    "fa": "فارسی", "fi": "Suomi", "he": "עברית", "hr": "Hrvatski", "hu": "Magyar",
    "lt": "Lietuvių", "lv": "Latviešu", "ms": "Bahasa Melayu",
    "nb": "Norsk (Bokmål)", "ro": "Română", "sk": "Slovenčina",
    "sl": "Slovenščina", "sv": "Svenska", "uk": "Українська",
    "zh-Hant": "繁體中文", "ca": "Català", "eu": "Euskara", "gl": "Galego",
    "sr": "Српски",
}


class TorqueLoggerFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Torque Logger 2025."""
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Handle the initial step."""
        # Une seule instance
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        # Construit les options de langue
        codes = _codes_from_supported_langs(SUPPORTED_LANGS)
        lang_options = [{"label": _LANG_LABELS.get(c, c), "value": c} for c in codes]

        errors: dict[str, str] = {}

        if user_input is not None:
            email = str(user_input.get(CONF_EMAIL, "")).strip()
            imperial = bool(user_input.get(CONF_IMPERIAL, False))
            language = user_input.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)

            # Validation minimale (évite Email() qui peut casser si lib absente)
            if not email:
                errors["base"] = "email_required"
            elif "@" not in email or "." not in email:
                errors["base"] = "invalid_email"

            if not errors:
                data = {
                    CONF_EMAIL: email,
                    CONF_IMPERIAL: imperial,
                    CONF_LANGUAGE: language if language in codes else DEFAULT_LANGUAGE,
                }
                return self.async_create_entry(title=NAME, data=data)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_EMAIL): str,  # simple & sûr
                vol.Optional(CONF_IMPERIAL, default=False): bool,
                vol.Optional(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): SelectSelector(
                    SelectSelectorConfig(
                        options=lang_options,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Return the options flow."""
        return TorqueLoggerOptionsFlowHandler()


class TorqueLoggerOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for Torque Logger 2025."""

    async def async_step_init(self, user_input: dict | None = None):
        """Handle options."""
        # Construit les options de langue
        codes = _codes_from_supported_langs(SUPPORTED_LANGS)
        lang_options = [{"label": _LANG_LABELS.get(c, c), "value": c} for c in codes]

        if user_input is not None:
            # On enregistre tel quel : Home Assistant gère le merge options/data
            lang = user_input.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)
            user_input[CONF_LANGUAGE] = lang if lang in codes else DEFAULT_LANGUAGE
            return self.async_create_entry(title="", data=user_input)

        current_imperial = self.config_entry.options.get(
            CONF_IMPERIAL, self.config_entry.data.get(CONF_IMPERIAL, False)
        )
        current_language = self.config_entry.options.get(
            CONF_LANGUAGE, self.config_entry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)
        )
        if current_language not in codes:
            current_language = DEFAULT_LANGUAGE

        data_schema = vol.Schema(
            {
                vol.Optional(CONF_IMPERIAL, default=current_imperial): bool,
                vol.Optional(CONF_LANGUAGE, default=current_language): SelectSelector(
                    SelectSelectorConfig(
                        options=lang_options,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=data_schema)
