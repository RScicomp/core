"""Integration for EcoFlow devices."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .client import EcoFlowClient
from .const import CONF_ACCESS_KEY, CONF_DEVICE_SN, CONF_SECRET_KEY, PLATFORMS
from .coordinator import EcoFlowCoordinator

type EcoFlowConfigEntry = ConfigEntry[EcoFlowCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: EcoFlowConfigEntry) -> bool:
    """Set up EcoFlow from a config entry."""
    session = async_get_clientsession(hass)
    client = EcoFlowClient(
        entry.data[CONF_ACCESS_KEY],
        entry.data[CONF_SECRET_KEY],
        entry.data[CONF_DEVICE_SN],
        session,
    )

    coordinator = EcoFlowCoordinator(hass, client, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: EcoFlowConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
