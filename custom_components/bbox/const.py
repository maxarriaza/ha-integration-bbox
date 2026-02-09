from homeassistant.const import Platform

# Global configuration of integration
DOMAIN="bbox"

PLATFORMS: list[Platform] = [
    Platform.DEVICE_TRACKER
]

# Default entry value
ENTRY_TITLE = "Bbox"

# Device configuration keys
CONF_HOST_TRACKER = "host_tracker"
CONF_HOST_TRACKER_MAC_ADDRESS = 'mac_address'