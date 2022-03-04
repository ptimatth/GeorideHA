""" device tracker for GeoRide object """

import logging
from typing import Any, Mapping

from homeassistant.components.device_tracker.const import DOMAIN, SOURCE_TYPE_GPS
from homeassistant.components.device_tracker.config_entry import TrackerEntity

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .device import Device
from .const import DOMAIN as GEORIDE_DOMAIN


_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities): # pylint: disable=W0613
    """Set up Georide tracker based off an entry."""
    georide_context = hass.data[GEORIDE_DOMAIN]["context"]
    coordoned_trackers = georide_context.georide_trackers_coordoned

    entities = []
    for coordoned_tracker in coordoned_trackers:
        tracker_device = coordoned_tracker['tracker_device']
        coordinator = coordoned_tracker['coordinator']
        entity = GeoRideTrackerEntity(coordinator, tracker_device, hass)
        hass.data[GEORIDE_DOMAIN]["devices"][tracker_device.unique_id] = coordinator
        entities.append(entity)

    async_add_entities(entities)

    return True


class GeoRideTrackerEntity(CoordinatorEntity, TrackerEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 tracker_device: Device, hass):
        """Set up GeoRide entity."""
        super().__init__(coordinator)
        self._name = tracker_device.tracker.tracker_name
        self._tracker_device = tracker_device
        self.entity_id = DOMAIN + ".{}".format(tracker_device.tracker.tracker_id)
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"georide_tracker_{self._tracker_device.tracker.tracker_id}"

    @property
    def name(self):
        """ GeoRide odometer name """
        return f"{self._name} position"

    @property
    def latitude(self):
        """Return latitude value of the device."""
        if self._tracker_device.tracker.latitude:
            return self._tracker_device.tracker.latitude
        return None

    @property
    def longitude(self):
        """Return longitude value of the device."""
        if self._tracker_device.tracker.longitude:
            return self._tracker_device.tracker.longitude
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
        return self._tracker_device.device_info
