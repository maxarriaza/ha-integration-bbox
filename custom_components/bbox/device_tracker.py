import logging

from homeassistant.components.device_tracker import ScannerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_HOST_TRACKER_MAC_ADDRESS, DOMAIN
from .coordinator import BboxDataUpdateCoordinator
from .helpers import get_host_tracker_subentries

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry[BboxDataUpdateCoordinator], async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    """Setup Bbox device tracker entities"""
    _LOGGER.debug('Setup entry %s', config_entry.entry_id)

    coordinator = config_entry.runtime_data

    # Configure Bbox Host tracker entities
    host_tracker_subentries = get_host_tracker_subentries(config_entry)
    for subentry in host_tracker_subentries:
        host = coordinator.data.get_host(subentry.data.get(CONF_HOST_TRACKER_MAC_ADDRESS))
        if host is not None:
            # Configure device
            current_device_registry = device_registry.async_get(hass)
            current_device_registry.async_get_or_create(
                config_entry_id=config_entry.entry_id,
                config_subentry_id=subentry.subentry_id,
                identifiers={(DOMAIN, host.mac_address)},
                connections={(device_registry.CONNECTION_NETWORK_MAC, host.mac_address)},
                model=host.model_name,
                manufacturer=host.manufacturer,
                name=host.hostname,
            )

            entity = BboxHostTracker(coordinator=coordinator, hostname=host.hostname, mac_address=host.mac_address, ip_address=host.ip_address)
            async_add_entities([entity], update_before_add=True, config_subentry_id=subentry.subentry_id)
        else:
            _LOGGER.warning('No host found with mac address', subentry.subentry_id, subentry.data.get(CONF_HOST_TRACKER_MAC_ADDRESS))

class BboxHostTracker(CoordinatorEntity[BboxDataUpdateCoordinator], ScannerEntity):
    """Representation of a tracked host with bbox"""
    def __init__(self, coordinator: BboxDataUpdateCoordinator, hostname: str, mac_address: str, ip_address: str) -> None:
        super().__init__(coordinator=coordinator)
        self._attr_name = hostname
        self._attr_hostname = hostname
        self._attr_ip_address = ip_address
        self._attr_mac_address = mac_address

    @property
    def is_connected(self) -> bool:
        """Return connecting status."""
        return self.coordinator.data.is_host_connected(self.mac_address)