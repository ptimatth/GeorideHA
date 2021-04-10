""" device tracker for GeoRide object """

import logging
from typing import Any, Mapping

from homeassistant.components.device_tracker.const import DOMAIN, SOURCE_TYPE_GPS
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

import georideapilib.api as GeoRideApi

from .const import DOMAIN as GEORIDE_DOMAIN


_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities): # pylint: disable=W0613
    """Set up Georide tracker based off an entry."""
    georide_context = hass.data[GEORIDE_DOMAIN]["context"]
    coordoned_trackers = georide_context.get_coordoned_trackers()

    entities = []
    for coordoned_tracker in coordoned_trackers:
        tracker = coordoned_tracker['tracker']
        coordinator = coordoned_tracker['coordinator']
        entity = GeoRideTrackerEntity(coordinator, tracker, hass)
        hass.data[GEORIDE_DOMAIN]["devices"][tracker.tracker_id] = coordinator
        entities.append(entity)

    async_add_entities(entities)

    return True


class GeoRideTrackerEntity(CoordinatorEntity, TrackerEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]], tracker, hass):
        """Set up GeoRide entity."""
        super().__init__(coordinator)
        self._name = tracker.tracker_name
        self._tracker = tracker
        self.entity_id = DOMAIN + ".{}".format(tracker.tracker_id)
        self._hass = hass

    @property
    def unique_id(self):
        """Return the unique ID."""
        return self._tracker.tracker_id

    @property
    def name(self):
        """ame property"""
        return self._name
    
    @property
    def latitude(self):
        """Return latitude value of the device."""
        if self._tracker.latitude:
            return self._tracker.latitude
        return None

    @property
    def longitude(self):
        """Return longitude value of the device."""
        if self._tracker.longitude:
            return self._tracker.longitude

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
    
    async def async_update(self):
        """ update the current tracker"""
        _LOGGER.debug('update')

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.name,
            "identifiers": {(GEORIDE_DOMAIN, self._tracker.tracker_id)},
            "manufacturer": "GeoRide",
            "odometer": "{} km".format(self._tracker.odometer)
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
        
