import logging
from typing import Any

from aiobbox import BboxApi, BboxInvalidCredentialsError, BboxRateLimitError
from homeassistant.core import callback
from voluptuous import Schema, Required
from homeassistant.config_entries import ConfigFlow, ConfigSubentryFlow, ConfigEntry
from homeassistant.const import CONF_PASSWORD

from .coordinator import BboxDataUpdateCoordinator
from .const import DOMAIN, CONF_HOST_TRACKER, CONF_HOST_TRACKER_MAC_ADDRESS

_LOGGER = logging.getLogger(__name__)

class ConfigurationFlowHandler(ConfigFlow, domain=DOMAIN):
    """ Handle a global configuration flow handler for integration """
    VERSION = 1

    @classmethod
    @callback
    def async_get_supported_subentry_types(cls, config_entry: ConfigEntry[BboxDataUpdateCoordinator]) -> dict[str, type[ConfigSubentryFlow]]:
        """Return subentries supported by this integration."""
        return {CONF_HOST_TRACKER: BboxHostTrackerConfigurationFlowHandler}

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """ Handle a user input for configuration flow """
        schema = Schema(
            {
                Required(CONF_PASSWORD): str,
            }
        )
        if user_input is None:
            # Display configuration form
            return self.async_show_form(step_id="user", data_schema=schema)
        else:
            bbox = BboxApi(password=user_input[CONF_PASSWORD])
            try:
                await bbox.authenticate()
                await bbox.close()
                return self.async_create_entry(title='Bbox', data=user_input)
            except BboxInvalidCredentialsError:
                await bbox.close()
                return self.async_show_form(step_id="user", data_schema=schema, errors={
                    "base": "invalid_password_error",
                })
            except BboxRateLimitError:
                await bbox.close()
                return self.async_show_form(step_id="user", data_schema=schema, errors={
                    "base": "rate_limit_error",
                })

class BboxHostTrackerConfigurationFlowHandler(ConfigSubentryFlow):
    """ Handle a host tracker configuration flow for integration """

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """User flow to add a new device."""
        schema = Schema({
            Required(CONF_HOST_TRACKER_MAC_ADDRESS): str,
        })

        if user_input is None:
            # Display configuration form
            return self.async_show_form(step_id="user", data_schema=schema)
        else:
            return self.async_create_entry(title=user_input.get(CONF_HOST_TRACKER_MAC_ADDRESS), data=user_input)

