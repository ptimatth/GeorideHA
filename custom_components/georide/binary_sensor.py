""" binary_sensor for GeoRide object """

import logging

from datetime import timedelta
from typing import Any, Mapping

from homeassistant.core import callback
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.binary_sensor import ENTITY_ID_FORMAT

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

import georideapilib.api as GeoRideApi
import georideapilib.objects as GeoRideTracker

from .const import DOMAIN as GEORIDE_DOMAIN
from .const import MIN_UNTIL_REFRESH


_LOGGER = logging.getLogger(__name__) 
async def async_setup_entry(hass, config_entry, async_add_entities): # pylint: disable=W0613
    """Set up GeoRide tracker based off an entry."""
    georide_context = hass.data[GEORIDE_DOMAIN]["context"]      
    token = await georide_context.get_token()
    if token is None:
        return False

    update_interval = timedelta(seconds=1)
    trackers = await hass.async_add_executor_job(GeoRideApi.get_trackers,token)
    entities = []
    for tracker in trackers:
        coordinator = DataUpdateCoordinator[Mapping[str, Any]](
            hass,
            _LOGGER,
            name=tracker.tracker_name,
            update_method=georide_context.refresh_trackers,
            update_interval=update_interval
        )
        stolen_entity = GeoRideStolenBinarySensorEntity(coordinator, tracker)
        crashed_entity = GeoRideCrashedBinarySensorEntity(coordinator, tracker)
        entities.append(stolen_entity)
        entities.append(crashed_entity)
        hass.data[GEORIDE_DOMAIN]["devices"][tracker.tracker_id] = coordinator

    async_add_entities(entities, True)

    return True


class GeoRideBinarySensorEntity(CoordinatorEntity, BinarySensorEntity):
    """Represent a tracked device."""
    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]], tracker: GeoRideTracker):
        """Set up Georide entity."""
        super().__init__(coordinator)
        self._tracker = tracker
        self._name = tracker.tracker_name

        self.entity_id = ENTITY_ID_FORMAT.format("is_stolen") + "." + str(tracker.tracker_id)
        self._state = None
        self._data = False

    @property
    def unique_id(self):
        """Return the unique ID."""
        return self._tracker.tracker_id

    @property
    def name(self):
        """ GeoRide odometer name """
        return self._name

    @property
    def is_on(self):
        """state value property"""
        return self._data

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.name,
            "identifiers": {(GEORIDE_DOMAIN, self._tracker.tracker_id)},
            "manufacturer": "GeoRide"
        }

class GeoRideStolenBinarySensorEntity(GeoRideBinarySensorEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]], tracker: GeoRideTracker):
        """Set up Georide entity."""
        super().__init__(coordinator, tracker)
        self.entity_id = ENTITY_ID_FORMAT.format("is_stolen") + "." + str(tracker.tracker_id)

    async def async_update(self):
        """ update the current tracker"""
        _LOGGER.debug('update')
        self._name = self._tracker.tracker_name
        self._data = self._tracker.is_stolen

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"is_stolen_{self._tracker.tracker_id}"

  



class GeoRideCrashedBinarySensorEntity(GeoRideBinarySensorEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]], tracker: GeoRideTracker):
        """Set up Georide entity."""
        super().__init__(coordinator, tracker)
        self.entity_id = ENTITY_ID_FORMAT.format("is_crashed") + "." + str(tracker.tracker_id)

    async def async_update(self):
        """ update the current tracker"""
        _LOGGER.debug('update')
        self._name = self._tracker.tracker_name
        self._data = self._tracker.is_crashed

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"is_crashed_{self._tracker.tracker_id}"
