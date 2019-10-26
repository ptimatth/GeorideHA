""" device tracker for Georide object """
import logging

from homeassistant.core import callback
from homeassistant.const import (
    ATTR_GPS_ACCURACY,
    ATTR_LATITUDE,
    ATTR_LONGITUDE,
    ATTR_BATTERY_LEVEL,
)

from homeassistant.components.device_tracker.const import (
    ENTITY_ID_FORMAT,
    ATTR_SOURCE_TYPE,
    SOURCE_TYPE_GPS,
)
