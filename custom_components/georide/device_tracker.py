""" device tracker for Georide object """

import logging

from homeassistant.core import callback
from homeassistant.components.device_tracker.const import ENTITY_ID_FORMAT, SOURCE_TYPE_GPS
from homeassistant.components.device_tracker.config_entry import TrackerEntity

import georideapilib.api as GeorideApi

from . import DOMAIN as GEORIDE_DOMAIN


_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities): # pylint: disable=W0613
    """Set up Georide tracker based off an entry."""

    georide_context = hass.data[GEORIDE_DOMAIN]["context"]
        
    if georide_context.token is None:
        return False

    _LOGGER.info('Current georide token: %s', georide_context.async_get_token())

        
    trackers = GeorideApi.get_trackers(georide_context.async_get_token())

    
    tracker_entities = []
    for tracker in trackers:
        entity = GeorideTrackerEntity(tracker.tracker_id, tracker.tracker_name, data=tracker)
        hass.data[GEORIDE_DOMAIN]["devices"][tracker.tracker_id] = entity
        tracker_entities.append(entity)

    async_add_entities(tracker_entities)

    return True


class GeorideTrackerEntity(TrackerEntity):
    """Represent a tracked device."""

    def __init__(self, tracker_id, name, data=None):
        """Set up Georide entity."""
        self._tracker_id = tracker_id
        self._name = name
        self._data = data or {}
        self.entity_id = ENTITY_ID_FORMAT.format(tracker_id)

    @property
    def unique_id(self):
        """Return the unique ID."""
        return self._tracker_id

    @property
    def name(self):
        return self._name
    
    @property
    def latitude(self):
        """Return latitude value of the device."""
        if self._data.latitude:
            return self._data.latitude

        return None

    @property
    def longitude(self):
        """Return longitude value of the device."""
        if self._data.longitude:
            return self._data.longitude

        return None

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return SOURCE_TYPE_GPS
      
    @property
    def location_accuracy(self):
        """ return the gps accuracy of georide (could not be aquired, then 10) """
        return 20

    @property
    def icon(self):
        return "mdi:map-marker"
    

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.name,
            "identifiers": {(GEORIDE_DOMAIN, self._tracker_id)},
            "manufacturer": "GeoRide"
        }


    @callback
    def update_data(self, data):
        """Mark the device as seen."""
        self._data = data
        self.async_write_ha_state()

