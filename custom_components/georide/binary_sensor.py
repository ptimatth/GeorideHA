""" binary_sensor for GeoRide object """

import logging

from typing import Any, Mapping

from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.binary_sensor import ENTITY_ID_FORMAT
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator
)


from .const import DOMAIN as GEORIDE_DOMAIN
from .device import Device, DeviceBeacon

_LOGGER = logging.getLogger(__name__)
async def async_setup_entry(hass, config_entry, async_add_entities): # pylint: disable=W0613
    """Set up GeoRide tracker based off an entry."""
    georide_context = hass.data[GEORIDE_DOMAIN]["context"]
    entities = []
    coordoned_trackers = georide_context.georide_trackers_coordoned
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
    
    coordoned_beacons = georide_context.georide_trackers_beacon_coordoned
    for coordoned_beacon in coordoned_beacons:
        tracker_beacon = coordoned_beacon['tracker_beacon']
        coordinator = coordoned_beacon['coordinator']
        entities.append(GeoRideBeaconUpdatedBinarySensorEntity(coordinator, tracker_beacon))
        hass.data[GEORIDE_DOMAIN]["devices"][tracker_beacon.beacon.beacon_id] = coordinator


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

class GeoRideBeaconBinarySensorEntity(CoordinatorEntity, BinarySensorEntity):
    """Represent a tracked device."""
    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 tracker_device_beacon: DeviceBeacon):
        """Set up Georide entity."""
        super().__init__(coordinator)
        self._tracker_device_beacon = tracker_device_beacon
        self._name = tracker_device_beacon.beacon.name
        self.entity_id = f"{ENTITY_ID_FORMAT.format('binary_sensor')}.{tracker_device_beacon.beacon.beacon_id}"# pylint: disable=C0301
        self._is_on = False

    @property
    def entity_category(self):
        return None

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
        return "problem"

    @property
    def is_on(self):
        """state value property"""
        return self._tracker_device.tracker.is_stolen

    @property
    def name(self):
        """ GeoRide odometer name """
        return f"{self._name} is not stolen"


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
        return "problem"

    @property
    def is_on(self):
        """state value property"""
        return self._tracker_device.tracker.is_crashed

    @property
    def name(self):
        """ GeoRide odometer name """
        return f"{self._name} is not crashed"

class GeoRideActiveSubscriptionBinarySensorEntity(GeoRideBinarySensorEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 tracker_device: Device):
        """Set up Georide entity."""
        super().__init__(coordinator, tracker_device)
        self.entity_id = f"{ENTITY_ID_FORMAT.format('is_active_subscription_')}.{tracker_device.tracker.tracker_id}"# pylint: disable=C0301

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"is_active_subscription_{self._tracker_device.tracker.tracker_id}"

    @property
    def is_on(self):
        """state value property"""
        tracker = self._tracker_device.tracker
        if tracker.is_oldsubscription:
            if tracker.subscription_id is not None:
                return True
            return False
        else:
            if tracker.subscription is not None and tracker.subscription.subscription_id is not None:
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
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"have_network_{self._tracker_device.tracker.tracker_id}"

    @property
    def device_class(self):
        """Return the device class."""
        return "connectivity"

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
        return "moving"

    @property
    def is_on(self):
        """state value property"""
        return self._tracker_device.tracker.moving

    @property
    def name(self):
        """ GeoRide name """
        return f"{self._name} is moving"

class GeoRideBeaconUpdatedBinarySensorEntity(GeoRideBeaconBinarySensorEntity):
    """Represent a tracked device."""
    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 tracker_beacon_device: DeviceBeacon):
        """Set up Georide entity."""
        super().__init__(coordinator, tracker_beacon_device)
        self.entity_id = f"{ENTITY_ID_FORMAT.format('update')}.{tracker_beacon_device.beacon.beacon_id}"# pylint: disable=C0301

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"update_{self._tracker_beacon_device.beacon.beacon_id}"

    @property
    def device_class(self):
        """Return the device class."""
        return "update"

    @property
    def is_on(self):
        """state value property"""
        return not self._tracker_beacon_device.beacon.is_updated

    @property
    def name(self):
        """ GeoRide name """
        return f"{self._name} have an update"