""" device tracker for GeoRide object """

import logging


from datetime import timedelta
from typing import Any, Mapping

from homeassistant.core import callback
from homeassistant.components.switch import SwitchEntity
from homeassistant.components.switch import ENTITY_ID_FORMAT

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

import georideapilib.api as GeoRideApi

from .const import DOMAIN as GEORIDE_DOMAIN


_LOGGER = logging.getLogger(__name__) 


async def async_setup_entry(hass, config_entry, async_add_entities): # pylint: disable=W0613
    """Set up GeoRide tracker based off an entry."""
    georide_context = hass.data[GEORIDE_DOMAIN]["context"]
    coordoned_trackers = georide_context.get_coordoned_trackers()

    lock_switch_entities = []
    for coordoned_tracker in coordoned_trackers:
        tracker = coordoned_tracker['tracker']
        coordinator = coordoned_tracker['coordinator']
        entity = GeoRideLockSwitchEntity(coordinator, tracker, hass)
        hass.data[GEORIDE_DOMAIN]["devices"][tracker.tracker_id] = coordinator
        lock_switch_entities.append(entity)

    async_add_entities(lock_switch_entities)

    return True



class GeoRideLockSwitchEntity(CoordinatorEntity, SwitchEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]], tracker, hass):
        """Set up GeoRide entity."""
        super().__init__(coordinator)
        self._tracker = tracker
        self._name = tracker.tracker_name
        self.entity_id = ENTITY_ID_FORMAT.format("lock") +"." + str(tracker.tracker_id)
        self._hass = hass
    

    async def async_turn_on(self, **kwargs):
        """ lock the GeoRide tracker """
        _LOGGER.info('async_turn_on %s', kwargs)
        georide_context = self._hass.data[GEORIDE_DOMAIN]["context"]
        token = await georide_context.get_token()
        success = await self._hass.async_add_executor_job(GeoRideApi.lock_tracker,
                                                      token, self._tracker_id)
        if success:
            self._tracker.is_locked = True
            
    async def async_turn_off(self, **kwargs):
        """ unlock the GeoRide tracker """
        _LOGGER.info('async_turn_off %s', kwargs)
        georide_context = self._hass.data[GEORIDE_DOMAIN]["context"]
        token = await georide_context.get_token()
        success = await self._hass.async_add_executor_job(GeoRideApi.unlock_tracker,
                                                          token, self._tracker_id)
        if success:
            self._tracker.is_locked = False

    async def async_toggle(self, **kwargs):
        """ toggle lock the georide tracker """
        _LOGGER.info('async_toggle %s', kwargs)
        georide_context = self._hass.data[GEORIDE_DOMAIN]["context"]
        token = await georide_context.get_token()
        result = await self._hass.async_add_executor_job(GeoRideApi.toogle_lock_tracker,
                                                         token, self._tracker_id)
        self._tracker.is_locked = result

    @property
    def unique_id(self):
        """Return the unique ID."""
        return self._tracker.tracker_id

    @property
    def name(self):
        """ GeoRide switch name """
        return self._name
    
    @property
    def is_on(self):
        """ GeoRide switch status """
        return self._tracker.is_locked

    @property
    def icon(self):
        """return the entity icon"""
        if self._tracker.tracker_id:
            return "mdi:lock"
        return "mdi:lock-open"
    

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.name,
            "identifiers": {(GEORIDE_DOMAIN, self._tracker.tracker_id)},
            "manufacturer": "GeoRide"
        }


