"""Config flow for EcoFlow integration."""

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .client import EcoFlowApiError, EcoFlowClient
from .const import CONF_ACCESS_KEY, CONF_DEVICE_SN, CONF_SECRET_KEY, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ACCESS_KEY): str,
        vol.Required(CONF_SECRET_KEY): str,
        vol.Required(CONF_DEVICE_SN): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    session = async_get_clientsession(hass)
    client = EcoFlowClient(
        data[CONF_ACCESS_KEY],
        data[CONF_SECRET_KEY],
        data[CONF_DEVICE_SN],
        session,
    )

    if not await client.async_test_connection():
        raise EcoFlowApiError("Cannot connect to EcoFlow API")

    return {"title": f"EcoFlow {data[CONF_DEVICE_SN]}"}


class EcoFlowConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EcoFlow."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_DEVICE_SN])
            self._abort_if_unique_id_configured()

            try:
                info = await validate_input(self.hass, user_input)
            except EcoFlowApiError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )