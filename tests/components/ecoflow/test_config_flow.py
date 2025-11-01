"""Tests for the EcoFlow config flow."""

from unittest.mock import patch

import pytest

from homeassistant import config_entries
from homeassistant.components.ecoflow.const import DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


async def test_config_flow_user_success(hass: HomeAssistant) -> None:
    """Test successful user flow."""
    with patch(
        "homeassistant.components.ecoflow.config_flow.validate_input",
        return_value={"title": "EcoFlow Device"},
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": config_entries.SOURCE_USER}
        )
        assert result["type"] == FlowResultType.FORM

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "access_key": "test_key",
                "secret_key": "test_secret",
                "device_sn": "test_serial",
            },
        )
        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == "EcoFlow Device"