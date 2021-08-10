""" binary_sensor for GeoRide object """

import logging

from typing import Any, Mapping

from homeassistant.core import callback
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.binary_sensor import ENTITY_ID_FORMAT
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator
)


from .const import DOMAIN as GEORIDE_DOMAIN
from .device import Device

_LOGGER = logging.getLogger(__name__)
async def async_setup_entry(hass, config_entry, async_add_entities): # pylint: disable=W0613
    """Set up GeoRide tracker based off an entry."""
    georide_context = hass.data[GEORIDE_DOMAIN]["context"]
    entities = []
    coordoned_trackers = georide_context.get_coordoned_trackers()
    for coordoned_tracker in coordoned_trackers:
        tracker_device = coordoned_tracker['tracker_device']
        coordinator = coordoned_tracker['coordinator']

        entities.append(GeoRideStolenBinarySensorEntity(coordinator, tracker_device))
        entities.append(GeoRideCrashedBinarySensorEntity(coordinator, tracker_device))
        entities.append(GeoRideOwnerBinarySensorEntity(coordinator, tracker_device))
        entities.append(GeoRideActiveSubscriptionBinarySensorEntity(coordinator, tracker_device))
        entities.append(GeoRideNetworkBinarySensorEntity(coordinator, tracker_device))
        entities.append(GeoRideMovingBinarySensorEntity(coordinator, tracker_device))

        hass.data[GEORIDE_DOMAIN]["devices"][tracker_device.tracker.tracker_id] = coordinator

    async_add_entities(entities, True)

    return True


class GeoRideBinarySensorEntity(CoordinatorEntity, BinarySensorEntity):
    """Represent a tracked device."""
    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 tracker_device: Device):
        """Set up Georide entity."""
        super().__init__(coordinator)
        self._tracker_device = tracker_device
        self._name = tracker_device.tracker.tracker_name

        self.entity_id = f"{ENTITY_ID_FORMAT.format('binary_sensor')}.{tracker_device.tracker.tracker_id}"# pylint: disable=C0301
        self._is_on = False

    @property
    def device_info(self):
        """Return the device info."""
        return self._tracker_device.device_info

class GeoRideStolenBinarySensorEntity(GeoRideBinarySensorEntity):
    """Represent a tracked device."""
    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 tracker_device: Device):
        """Set up Georide entity."""
        super().__init__(coordinator, tracker_device)
        self.entity_id = f"{ENTITY_ID_FORMAT.format('is_stolen')}.{tracker_device.tracker.tracker_id}"# pylint: disable=C0301

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"is_stolen_{self._tracker_device.tracker.tracker_id}"
    
    @property
    def device_class(self):
        """Return the device class."""
        return f"problem"

    @property
    def is_on(self):
        """state value property"""
        return self._tracker_device.tracker.is_stolen

    @property
    def name(self):
        """ GeoRide odometer name """
        return f"{self._name} is stolen"


class GeoRideCrashedBinarySensorEntity(GeoRideBinarySensorEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 tracker_device: Device):
        """Set up Georide entity."""
        super().__init__(coordinator, tracker_device)
        self.entity_id = f"{ENTITY_ID_FORMAT.format('is_crashed')}.{tracker_device.tracker.tracker_id}"# pylint: disable=C0301

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"is_crashed_{self._tracker_device.tracker.tracker_id}"
    
    @property
    def device_class(self):
        """Return the device class."""
        return f"problem"

    @property
    def is_on(self):
        """state value property"""
        return self._tracker_device.tracker.is_crashed

    @property
    def name(self):
        """ GeoRide odometer name """
        return f"{self._name} is crashed"

class GeoRideActiveSubscriptionBinarySensorEntity(GeoRideBinarySensorEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 tracker_device: Device):
        """Set up Georide entity."""
        super().__init__(coordinator, tracker_device)
        self.entity_id = f"{ENTITY_ID_FORMAT.format('is_active_subscription_')}.{tracker_device.tracker.tracker_id}"# pylint: disable=C0301

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"is_active_subscription_{self._tracker_device.tracker.tracker_id}"

    @property
    def is_on(self):
        """state value property"""
        if self._tracker_device.tracker.subscription_id is not None:
            return True
        return False

    @property
    def name(self):
        """ GeoRide odometer name """
        return f"{self._name} has an active subscription"

class GeoRideOwnerBinarySensorEntity(GeoRideBinarySensorEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 tracker_device: Device):
        """Set up Georide entity."""
        super().__init__(coordinator, tracker_device)
        self.entity_id = f"{ENTITY_ID_FORMAT.format('is_owner')}.{tracker_device.tracker.tracker_id}"# pylint: disable=C0301

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"is_owner_{self._tracker_device.tracker.tracker_id}"

    @property
    def is_on(self):
        """state value property"""
        if self._tracker_device.tracker.role == "owner":
            return True
        return False

    @property
    def name(self):
        """ GeoRide odometer name """
        return f"{self._name} is own tracker"
  
class GeoRideNetworkBinarySensorEntity(GeoRideBinarySensorEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 tracker_device: Device):
        """Set up Georide entity."""
        super().__init__(coordinator, tracker_device)
        self.entity_id = f"{ENTITY_ID_FORMAT.format('have_network')}.{tracker_device.tracker.tracker_id}"# pylint: disable=C0301

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"have_network_{self._tracker_device.tracker.tracker_id}"

    @property
    def device_class(self):
        """Return the device class."""
        return f"connectivity"

    @property
    def is_on(self):
        """state value property"""
        if self._tracker_device.tracker.status == "online":
            return True
        return False

    @property
    def name(self):
        """ GeoRide name """
        return f"{self._name} have network"
  
class GeoRideMovingBinarySensorEntity(GeoRideBinarySensorEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 tracker_device: Device):
        """Set up Georide entity."""
        super().__init__(coordinator, tracker_device)
        self.entity_id = f"{ENTITY_ID_FORMAT.format('moving')}.{tracker_device.tracker.tracker_id}"# pylint: disable=C0301

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"moving_{self._tracker_device.tracker.tracker_id}"

    @property
    def device_class(self):
        """Return the device class."""
        return f"moving"

    @property
    def is_on(self):
        """state value property"""
        return self._tracker_device.tracker.moving

    @property
    def name(self):
        """ GeoRide name """
        return f"{self._name} is moving"
