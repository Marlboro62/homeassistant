"""Adds config flow for Torque Logger."""
from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol

DOMAIN = "torque"
CONF_EMAIL = "email"
CONF_IMPERIAL = "imperial"
PLATFORMS = ["sensor"]


class TorqueLoggerFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Torque Logger."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        # Uncomment the next 2 lines if only a single instance of the integration is allowed:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            valid = await self._test_credentials(user_input[CONF_EMAIL])
            if valid:
                return self.async_create_entry(
                    title="Torque Logger", data=user_input
                )
            else:
                self._errors["base"] = CONF_EMAIL

            return await self._show_config_form(user_input)

        user_input = {}
        # Provide defaults for form
        user_input[CONF_EMAIL] = ""

        return await self._show_config_form(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Create the options flow."""
        return TorqueLoggerOptionsFlowHandler()

    async def _show_config_form(self, user_input: dict):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL, default=user_input.get(CONF_EMAIL, "")): str,
                    vol.Required(CONF_IMPERIAL, default=user_input.get(CONF_IMPERIAL, False)): bool,
                }
            ),
            errors=self._errors,
        )

    async def _test_credentials(self, email: str):
        """Return true if credentials is valid."""
        return email is not None and len(email.strip()) > 0


class TorqueLoggerOptionsFlowHandler(config_entries.OptionsFlow):
    """Torque Logger config flow options handler."""

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            return await self._update_options(user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        x, default=self.config_entry.options.get(x, True)
                    ): bool
                    for x in sorted(PLATFORMS)
                }
            ),
        )

    async def _update_options(self, user_input):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get(CONF_EMAIL),
            data=user_input,
        )
