""" device tracker for GeoRide object """

import logging

from homeassistant.components.device_tracker.const import DOMAIN, SOURCE_TYPE_GPS
from homeassistant.components.device_tracker.config_entry import TrackerEntity

import georideapilib.api as GeoRideApi

from .const import DOMAIN as GEORIDE_DOMAIN


_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities): # pylint: disable=W0613
    """Set up Georide tracker based off an entry."""

    georide_context = hass.data[GEORIDE_DOMAIN]["context"]        
    trackers = georide_context.get_trackers()    
    tracker_entities = []
    for tracker in trackers:
        entity = GeoRideTrackerEntity(hass, tracker.tracker_id, georide_context.get_token,
                                      georide_context.get_tracker, tracker)


        hass.data[GEORIDE_DOMAIN]["devices"][tracker.tracker_id] = entity
        tracker_entities.append(entity)

    async_add_entities(tracker_entities)

    return True


class GeoRideTrackerEntity(TrackerEntity):
    """Represent a tracked device."""

    def __init__(self, hass, tracker_id, get_token_callback, get_tracker_callback, tracker):
        """Set up GeoRide entity."""
        self._tracker_id = tracker_id
        self._get_token_callback = get_token_callback
        self._get_tracker_callback = get_tracker_callback
        self._name = tracker.tracker_name
        self._tracker = tracker
        self.entity_id = DOMAIN + ".{}".format(tracker_id)
        self._hass = hass

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
        """return the entity icon"""
        return "mdi:map-marker"
    

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.name,
            "identifiers": {(GEORIDE_DOMAIN, self._tracker_id)},
            "manufacturer": "GeoRide",
            "odometer": "{} km".format(self.tracker.odometer)
        }

    @property
    def get_tracker_callback(self):
        """ get tracker callaback"""
        return self._get_tracker_callback
    
    @property
    def get_token_callback(self):
        """ get token callaback"""
        return self._get_token_callback
    

    @property
    def should_poll(self):
        """No polling needed."""
        return True

    async def async_update(self):
        """ update the current tracker"""
        _LOGGER.debug('update')
        self._data = await self._get_tracker_callback(self._tracker_id)
        self._name = self.tracker.tracker_name
        
