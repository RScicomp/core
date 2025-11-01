"""Coordinator for EcoFlow integration."""

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import EcoFlowApiError, EcoFlowClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class EcoFlowCoordinator(DataUpdateCoordinator[dict]):
    """EcoFlow data update coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: EcoFlowClient,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=60),
            config_entry=config_entry,
        )
        self.client = client

    async def _async_update_data(self) -> dict:
        """Fetch data from EcoFlow API."""
        try:
            return await self.client.async_get_device_quota()
        except EcoFlowApiError as err:
            raise UpdateFailed(f"Error communicating with EcoFlow API: {err}") from err