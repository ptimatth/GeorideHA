""" odometter sensor for GeoRide object """

import logging
from typing import Any, Mapping

from homeassistant.core import callback
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor import ENTITY_ID_FORMAT
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN as GEORIDE_DOMAIN
from .device import Device


_LOGGER = logging.getLogger(__name__) 


async def async_setup_entry(hass, config_entry, async_add_entities): # pylint: disable=W0613
    """Set up GeoRide tracker based off an entry."""
    georide_context = hass.data[GEORIDE_DOMAIN]["context"]
    coordoned_trackers = georide_context.get_coordoned_trackers()

    entities = []
    for coordoned_tracker in coordoned_trackers:
        tracker_device = coordoned_tracker['tracker_device']
        coordinator = coordoned_tracker['coordinator']
        entity = GeoRideOdometerSensorEntity(coordinator, tracker_device, hass)
        hass.data[GEORIDE_DOMAIN]["devices"][tracker_device.tracker.tracker_id] = coordinator
        entities.append(entity)

    async_add_entities(entities)

    return True

class GeoRideOdometerSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 tracker_device:Device, hass):
        """Set up GeoRide entity."""
        super().__init__(coordinator)
        self._tracker_device = tracker_device
        self._name = tracker_device.tracker.tracker_name
        self._unit_of_measurement = "m"
        self.entity_id = f"{ENTITY_ID_FORMAT.format('odometer')}.{tracker_device.tracker.tracker_id}"# pylint: disable=C0301

        self._state = 0
        self._hass = hass

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"odometer_{self._tracker_device.tracker.tracker_id}"

    @property
    def state(self):
        """state property"""
        return self._tracker_device.tracker.odometer

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ GeoRide odometer name """
        return f"{self._name} odometer"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:counter"

    @property
    def device_info(self):
        """Return the device info."""
        return self._tracker_device.device_info
