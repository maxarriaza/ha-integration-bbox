from homeassistant.config_entries import ConfigEntry

from custom_components.bbox.const import CONF_HOST_TRACKER


def get_host_tracker_subentries(config_entry: ConfigEntry):
    """ Function to return host tracker subentries """
    return [subentry for subentry in config_entry.subentries.values() if subentry.subentry_type == CONF_HOST_TRACKER]