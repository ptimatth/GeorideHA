""" odometter sensor for Georide object """

import logging

from homeassistant.core import callback
from homeassistant.components.switch import SwitchDevice
from homeassistant.components.switch import ENTITY_ID_FORMAT

import georideapilib.api as GeorideApi

from .const import DOMAIN as GEORIDE_DOMAIN


_LOGGER = logging.getLogger(__name__) 


async def async_setup_entry(hass, config_entry, async_add_entities): # pylint: disable=W0613
    """Set up Georide tracker based off an entry."""
    georide_context = hass.data[GEORIDE_DOMAIN]["context"]      

    if georide_context.get_token() is None:
        return False

    trackers = GeorideApi.get_trackers(georide_context.get_token())

    odometer_switch_entities = []
    for tracker in trackers:
        entity = GeorideOdometerSensorEntity(tracker.tracker_id, georide_context.get_token,
                                             georide_context.get_tracker, data=tracker)
        hass.data[GEORIDE_DOMAIN]["devices"][tracker.tracker_id] = entity
        odometer_switch_entities.append(entity)

    async_add_entities(odometer_switch_entities)

    return True

class GeorideOdometerSensorEntity(SwitchDevice):
    """Represent a tracked device."""

    def __init__(self, tracker_id, get_token_callback, get_tracker_callback, data):
        """Set up Georide entity."""
        self._tracker_id = tracker_id
        self._data = data or {}
        self._get_token_callback = get_token_callback
        self._get_tracker_callback = get_tracker_callback
        self._name = data.tracker_name
        self._unit_of_measurement = "m"

        self.entity_id = ENTITY_ID_FORMAT.format("odometer") + "." + str(tracker_id)
        self._state = 0


    def update(self):
        """ update the current tracker"""
        _LOGGER.info('update')
        self._data = self._get_tracker_callback(self._tracker_id)
        self._name = self._data.tracker_name
        self._state = self._data.odometer

    @property
    def unique_id(self):
        """Return the unique ID."""
        return self._tracker_id

    @property
    def name(self):
        """ Georide switch name """
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement
    
    @property
    def get_token_callback(self):
        """ Georide switch token callback method """
        return self._get_token_callback
    
    @property
    def get_tracker_callback(self):
        """ Georide switch token callback method """
        return self._get_tracker_callback

    @property
    def icon(self):
        return "mdi:counter"
    

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.name,
            "identifiers": {(GEORIDE_DOMAIN, self._tracker_id)},
            "manufacturer": "GeoRide"
        }


