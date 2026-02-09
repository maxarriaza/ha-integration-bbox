import json
import logging
from datetime import timedelta

from aiobbox import BboxApi, BboxInvalidCredentialsError, BboxTimeoutError, BboxApiError
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pydantic.v1 import ValidationError
from pyric.utils.hardware import manufacturer

from .const import DOMAIN
from .model import BboxData, BboxHost, BboxInformation

_LOGGER = logging.getLogger(__name__)

class BboxDataUpdateCoordinator(DataUpdateCoordinator[BboxData]):
    """ Coordinator for bbox api """
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        super().__init__(hass=hass, logger=_LOGGER, config_entry=config_entry, name=DOMAIN, update_interval=timedelta(seconds=30))

    async def _async_setup(self):
        """Set up the coordinator

        This is the place to set up your coordinator,
        or to load data, that only needs to be loaded once.

        This method will be called automatically during
        coordinator.async_config_entry_first_refresh.
        """
        self.logger.debug("Setup coordinator")
        self._client = BboxApi(password=self.config_entry.data[CONF_PASSWORD], timeout=1)

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            self.logger.debug("Update coordinator data")

            # Check if authenticated
            if not self._client._authenticated:
                self.logger.debug("Client authentication")
                await self._client.authenticate()

            # Get router information
            router_info = await self._client.get_router_info()

            # Get router hosts
            hosts = await self._client.get_hosts()

            # Return data transfer object
            return BboxData(
                information=BboxInformation(
                    serial_number=router_info.serialnumber,
                    model_name=router_info.modelname,
                    software_version=router_info.running.version,
                ),
                hosts=[
                    BboxHost(
                        hostname=host.hostname,
                        mac_address=host.macaddress,
                        ip_address=host.ipaddress,
                        is_connected=host.active,
                        manufacturer=host.informations.manufacturer,
                        model_name=host.informations.model,
                        software_version=host.informations.version
                    ) for host in hosts
                ]
            )

        except BboxTimeoutError as err:
            await self._client.close()
            raise UpdateFailed("Request timeout") from err

        except BboxInvalidCredentialsError as err:
            await self._client.close()
            raise UpdateFailed(f"Invalid credentials") from err

        except BboxApiError as err:
            await self._client.close()
            raise UpdateFailed(f"Client error") from err

    async def async_shutdown(self) -> None:
        """Cancel any scheduled call, and ignore new runs."""
        self.logger.debug("Shutdown coordinator")
        await self._client.close()
        return await super().async_shutdown()