""" device tracker for Georide object """

import logging

from homeassistant.components.switch import SwitchDevice
from homeassistant.components.switch import ENTITY_ID_FORMAT

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

    
    lock_switch_entities = []
    for tracker in trackers:
        entity = GeorideLockSwitchEntity(tracker.tracker_id, tracker.tracker_name,
                                         georide_context.async_get_token, data=tracker)
        hass.data[GEORIDE_DOMAIN]["devices"][tracker.tracker_id] = entity
        lock_switch_entities.append(entity)

    async_add_entities(lock_switch_entities)

    return True


class GeorideLockSwitchEntity(SwitchDevice):
    """Represent a tracked device."""

    def __init__(self, tracker_id, name, token_callback, data):
        """Set up Georide entity."""
        self._tracker_id = tracker_id
        self._name = name
        self._data = data or {}
        self._token_callback = token_callback
        self._is_on = data.is_locked
        self.entity_id = ENTITY_ID_FORMAT.format("lock."+str(tracker_id))


    async def async_turn_on(self, **kwargs):
        """ lock the georide tracker """
        _LOGGER.info('async_turn_on %s', kwargs)
        success = GeorideApi.lock_tracker(self.token_callback(), self._tracker_id)
        if success:
            self._is_on = True
            
    async def async_turn_off(self, **kwargs):
        """ unlock the georide tracker """
        _LOGGER.info('async_turn_off %s', kwargs)
        success = GeorideApi.unlock_tracker(self.token_callback(), self._tracker_id)
        if success:
            self._is_on = False

    async def async_toggle(self, **kwargs):
        """ toggle lock the georide tracker """
        _LOGGER.info('async_toggle %s', kwargs)
        self._is_on = GeorideApi.toogle_lock_tracker(self.token_callback(), self._tracker_id)

    async def async_update(self):
        """ update the current tracker"""
        _LOGGER.info('async_update ')


    @property
    def unique_id(self):
        """Return the unique ID."""
        return self._tracker_id

    @property
    def name(self):
        """ Georide switch name """
        return self._name

    @property
    def is_on(self):
        """ Georide switch status """
        return self._is_on
    
    @property
    def token_callback(self):
        """ Georide switch token callback method """
        return self._token_callback
    

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.name,
            "identifiers": {(GEORIDE_DOMAIN, self._tracker_id)},
            "manufacturer": "GeoRide"
        }
