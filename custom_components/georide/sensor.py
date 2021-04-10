""" odometter sensor for GeoRide object """

import logging
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

    entities = []
    for coordoned_tracker in coordoned_trackers:
        tracker = coordoned_tracker['tracker']
        coordinator = coordoned_tracker['coordinator']
        entity = GeoRideOdometerSensorEntity(coordinator, tracker, hass)
        hass.data[GEORIDE_DOMAIN]["devices"][tracker.tracker_id] = coordinator
        entities.append(entity)

    async_add_entities(entities)

    return True

class GeoRideOdometerSensorEntity(CoordinatorEntity, SwitchEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]], tracker, hass):
        """Set up GeoRide entity."""
        super().__init__(coordinator)
        self._tracker = tracker
        self._name = tracker.tracker_name
        self._unit_of_measurement = "m"
        self.entity_id = ENTITY_ID_FORMAT.format("odometer") + "." + str(tracker.tracker_id)
        self._state = 0
        self._hass = hass


    async def async_update(self):
        """ update the current tracker"""
        _LOGGER.debug('update')
        self._name = self._tracker.tracker_name
        self._state = self._tracker.odometer

    @property
    def unique_id(self):
        """Return the unique ID."""
        return self._tracker.tracker_id

    @property
    def name(self):
        """ GeoRide odometer name """
        return self._name

    @property
    def state(self):
        """state property"""
        return self._state

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement
    
    @property
    def icon(self):
        """icon getter"""
        return "mdi:counter"
    
    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.name,
            "identifiers": {(GEORIDE_DOMAIN, self._tracker.tracker_id)},
            "manufacturer": "GeoRide"
        }


