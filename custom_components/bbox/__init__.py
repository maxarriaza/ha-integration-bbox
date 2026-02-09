import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry

from .const import PLATFORMS, DOMAIN
from .coordinator import BboxDataUpdateCoordinator
from .device_tracker import BboxHostTracker

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry[BboxDataUpdateCoordinator]) -> bool:
    """ Setup integration for configuration entry """
    _LOGGER.debug('Setup integration')
    # Setup coordinator
    coordinator = BboxDataUpdateCoordinator(hass=hass, config_entry=config_entry)
    await coordinator.async_config_entry_first_refresh()

    # Setup device for router
    current_device_registry = device_registry.async_get(hass)
    current_device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers={(DOMAIN, coordinator.data.information.serial_number)},
        manufacturer="Arcadyan",
        serial_number=coordinator.data.information.serial_number,
        model=coordinator.data.information.model_name,
        sw_version=coordinator.data.information.software_version,
        name='Bbox',
    )

    # Add event listener on configuration entry
    config_entry_update_clean = config_entry.add_update_listener(async_update_entry)
    config_entry.async_on_unload(config_entry_update_clean)


    # Register coordinator in configuration entry
    config_entry.runtime_data = coordinator

    # Delegate platforms setup using config entry
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_update_entry(hass: HomeAssistant, config_entry: ConfigEntry[BboxDataUpdateCoordinator]) -> None:
    """ Handler for config entry update """
    _LOGGER.debug('Update entry %s', config_entry.entry_id)
    await hass.config_entries.async_reload(config_entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """ Handler for config entry unload """
    _LOGGER.debug("Unload entry %s", config_entry.entry_id)

    # Unload platforms first
    unload_ok = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)

    if unload_ok:
        # Stop the coordinator
        config_entry.runtime_data = None

    return unload_ok