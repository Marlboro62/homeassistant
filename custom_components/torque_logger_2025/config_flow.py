# -*- coding: utf-8 -*-
"""Adds config flow for Torque Logger 2025."""
from __future__ import annotations

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
    SUPPORTED_LANGS,   
)


class TorqueLoggerFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Torque Logger 2025."""
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Handle the initial step."""
        # Verrouille l'unicité de l'intégration (une seule instance)
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        # Options (label/value) pour le SelectSelector
        LANG_LABELS = { "ar": "العربية", "de": "Deutsch", "en": "English", "en-AU": "English (AU)", "en-GB": "English (UK)", "es": "Español", "fr": "Français", "fr-CA": "Français (CA)", "hi": "हिन्दी", "id": "Indonesia", "it": "Italiano", "ja": "日本語", "ko": "한국어", "nl": "Nederlands", "pl": "Polski", "pt-BR": "Português (BR)", "pt-PT": "Português (PT)", "ru": "Русский", "th": "ไทย", "tr": "Türkçe", "vi": "Tiếng Việt", "zh-Hans": "简体中文", "bg": "Български", "cs": "Čeština", "da": "Dansk", "el": "Ελληνικά", "fa": "فارسی", "fi": "Suomi", "he": "עברית", "hr": "Hrvatski", "hu": "Magyar", "lt": "Lietuvių", "lv": "Latviešu", "ms": "Bahasa Melayu", "nb": "Norsk (Bokmål)", "ro": "Română", "sk": "Slovenčina", "sl": "Slovenščina", "sv": "Svenska", "uk": "Українська", "zh-Hant": "繁體中文", "ca": "Català", "eu": "Euskara", "gl": "Galego", "sr": "Српски" }
        lang_options = [{"label": LANG_LABELS.get(code, code), "value": code} for code in SUPPORTED_LANGS]


        if user_input is not None:
            data = {
                CONF_EMAIL: user_input[CONF_EMAIL].strip(),
                CONF_IMPERIAL: bool(user_input.get(CONF_IMPERIAL, False)),
                CONF_LANGUAGE: user_input.get(CONF_LANGUAGE, DEFAULT_LANGUAGE),
            }
            return self.async_create_entry(title=NAME, data=data)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_EMAIL): vol.Email(),
                vol.Optional(CONF_IMPERIAL, default=False): bool,
                vol.Optional(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): SelectSelector(
                    SelectSelectorConfig(
                        options=lang_options,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Retourne l’options flow sans passer config_entry (HA l’injectera)."""
        return TorqueLoggerOptionsFlowHandler()


class TorqueLoggerOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow pour Torque Logger 2025.

    NOTE: Ne pas définir __init__ ni assigner self.config_entry — HA le gère.
    """

    async def async_step_init(self, user_input: dict | None = None):
        """Gérer le formulaire d’options."""
        # Prépare les options du sélecteur (label / value)
        LANG_LABELS = {
            "en": "English", "en-GB": "English (UK)", "en-AU": "English (AU)",
            "fr": "Français", "fr-CA": "Français (CA)",
            "de": "Deutsch", "es": "Español", "it": "Italiano", "nl": "Nederlands", "pl": "Polski",
            "pt-PT": "Português (PT)", "pt-BR": "Português (BR)",
            "ru": "Русский", "tr": "Türkçe", "ar": "العربية", "hi": "हिन्दी", "id": "Indonesia",
            "ja": "日本語", "ko": "한국어", "th": "ไทย", "vi": "Tiếng Việt", "zh-Hans": "简体中文"
        }
        lang_options = [{"label": LANG_LABELS.get(code, code), "value": code} for code in SUPPORTED_LANGS]


        if user_input is not None:
            # On stocke uniquement les options (impérial/langue)
            return self.async_create_entry(title="", data=user_input)

        # Valeurs actuelles (fallback sur data si options absentes)
        current_imperial = self.config_entry.options.get(
            CONF_IMPERIAL, self.config_entry.data.get(CONF_IMPERIAL, False)
        )
        current_language = self.config_entry.options.get(
            CONF_LANGUAGE, self.config_entry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)
        )
        # Si la langue enregistrée n'est plus supportée, repartir sur le défaut
        if current_language not in SUPPORTED_LANGS:
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