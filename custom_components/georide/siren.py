""" device tracker for GeoRide object """

import logging


from typing import Any, Mapping

from homeassistant.components.siren import SirenEntity
from homeassistant.components.siren import ENTITY_ID_FORMAT

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

import georideapilib.api as GeoRideApi

from .const import DOMAIN as GEORIDE_DOMAIN
from .device import Device

_LOGGER = logging.getLogger(__name__) 


async def async_setup_entry(hass, config_entry, async_add_entities): # pylint: disable=W0613
    """Set up GeoRide tracker based off an entry."""
    georide_context = hass.data[GEORIDE_DOMAIN]["context"]
    coordoned_trackers = georide_context.georide_trackers_coordoned

    entities = []
    for coordoned_tracker in coordoned_trackers:
        tracker_device = coordoned_tracker['tracker_device']
        coordinator = coordoned_tracker['coordinator']
        hass.data[GEORIDE_DOMAIN]["devices"][tracker_device.unique_id] = coordinator
        if tracker_device.tracker.version > 2:
            entities.append(GeoRideSirenEntity(coordinator, tracker_device, hass))

    await async_add_entities(entities)

    return True

class GeoRideSirenEntity(CoordinatorEntity, SirenEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 tracker_device:Device, hass):
        """Set up GeoRide entity."""
        super().__init__(coordinator)
        self._tracker_device = tracker_device
        self._name = tracker_device.tracker.tracker_name
        self.entity_id = f"{ENTITY_ID_FORMAT.format('eco_mode')}.{tracker_device.tracker.tracker_id}"# pylint: disable=C0301
        self._hass = hass

    async def async_turn_on(self, **kwargs):
        """ lock the GeoRide tracker """
        _LOGGER.info('async_turn_on eco %s', kwargs)
        georide_context = self._hass.data[GEORIDE_DOMAIN]["context"]
        token = await georide_context.get_token()
        success = await self._hass.async_add_executor_job(GeoRideApi.change_tracker_siren_state,
                                                          token, self._tracker_device.tracker.tracker_id, True)
        if success:
            self._tracker_device.tracker.is_siren_on = True

    async def async_turn_off(self, **kwargs):
        """ unlock the GeoRide tracker """
        _LOGGER.info('async_turn_off eco %s', kwargs)
        georide_context = self._hass.data[GEORIDE_DOMAIN]["context"]
        token = await georide_context.get_token()
        success = await self._hass.async_add_executor_job(GeoRideApi.change_tracker_siren_state,
                                                          token, self._tracker_device.tracker.tracker_id, False)
        if success:
            self._tracker_device.tracker.is_siren_on = False

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"siren_{self._tracker_device.tracker.tracker_id}"

    @property
    def name(self):
        """ GeoRide odometer name """
        return f"{self._name} siren"

    @property
    def is_on(self):
        """ GeoRide switch status """
        return self._tracker_device.tracker.is_siren_on

    @property
    def device_info(self):
        """Return the device info."""
        return self._tracker_device.device_info