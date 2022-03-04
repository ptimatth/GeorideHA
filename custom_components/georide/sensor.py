""" odometter sensor for GeoRide object """

import logging
from typing import Any, Mapping

from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor import ENTITY_ID_FORMAT
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN as GEORIDE_DOMAIN
from .device import Device, DeviceBeacon    


_LOGGER = logging.getLogger(__name__) 


async def async_setup_entry(hass, config_entry, async_add_entities): # pylint: disable=W0613
    """Set up GeoRide tracker based off an entry."""
    georide_context = hass.data[GEORIDE_DOMAIN]["context"]
    coordoned_trackers = georide_context.georide_trackers_coordoned

    entities = []
    for coordoned_tracker in coordoned_trackers:
        tracker_device = coordoned_tracker['tracker_device']
        coordinator = coordoned_tracker['coordinator']
        hass.data[GEORIDE_DOMAIN]["devices"][tracker_device.tracker.tracker_id] = coordinator
        entities.append(GeoRideOdometerSensorEntity(coordinator, tracker_device, hass))
        entities.append(GeoRideOdometerKmSensorEntity(coordinator, tracker_device, hass))
        entities.append(GeoRideFixtimeSensorEntity(coordinator, tracker_device))
        if tracker_device.tracker.version > 2:
            entities.append(GeoRideInternalBatterySensorEntity(coordinator, tracker_device))
            entities.append(GeoRideExternalBatterySensorEntity(coordinator, tracker_device))
    
    coordoned_beacons = georide_context.georide_trackers_beacon_coordoned
    for coordoned_beacon in coordoned_beacons:
        tracker_beacon = coordoned_tracker['tracker_beacon']
        coordinator = coordoned_tracker['coordinator']
        entities.append(GeoRideBeaconUpdatedBinarySensorEntity(coordinator, tracker_beacon))
        hass.data[GEORIDE_DOMAIN]["devices"][tracker_device.beacon.beacon_id] = coordinator

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
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"odometer_{self._tracker_device.tracker.tracker_id}"

    @property
    def state(self):
        """state property"""
        odometer = self._tracker_device.tracker.odometer
        return odometer

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
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._tracker_device.device_info

class GeoRideOdometerKmSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 tracker_device:Device, hass):
        """Set up GeoRide entity."""
        super().__init__(coordinator)
        self._tracker_device = tracker_device
        self._name = tracker_device.tracker.tracker_name
        self._unit_of_measurement = "km"
        self.entity_id = f"{ENTITY_ID_FORMAT.format('odometer_km')}.{tracker_device.tracker.tracker_id}"# pylint: disable=C0301

        self._state = 0
        self._hass = hass
        
    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"odometer_km_{self._tracker_device.tracker.tracker_id}"

    @property
    def state(self):
        """state property"""
        odometer = self._tracker_device.tracker.odometer // 1000
        return odometer

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ GeoRide odometer name """
        return f"{self._name} odometer km"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:counter"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._tracker_device.device_info

class GeoRideInternalBatterySensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a tracked device."""
    entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 tracker_device:Device):
        """Set up GeoRide entity."""
        super().__init__(coordinator)
        self._tracker_device = tracker_device
        self._name = tracker_device.tracker.tracker_name
        self._unit_of_measurement = "V"
        self.entity_id = f"{ENTITY_ID_FORMAT.format('internal_battery_voltage')}.{tracker_device.tracker.tracker_id}"# pylint: disable=C0301

        self._state = 0

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"internal_battery_voltage_{self._tracker_device.tracker.tracker_id}"

    @property
    def state(self):
        """state property"""
        return self._tracker_device.tracker.internal_battery_voltage

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ GeoRide internal_battery_voltage name """
        return f"{self._name} internal_battery_voltage"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:battery"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._tracker_device.device_info

class GeoRideExternalBatterySensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 tracker_device:Device):
        """Set up GeoRide entity."""
        super().__init__(coordinator)
        self._tracker_device = tracker_device
        self._name = tracker_device.tracker.tracker_name
        self._unit_of_measurement = "V"
        self.entity_id = f"{ENTITY_ID_FORMAT.format('external_battery_voltage')}.{tracker_device.tracker.tracker_id}"# pylint: disable=C0301
        self._state = 0

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"external_battery_voltage_{self._tracker_device.tracker.tracker_id}"

    @property
    def state(self):
        """state property"""
        return self._tracker_device.tracker.external_battery_voltage

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ GeoRide internal_battery_voltage name """
        return f"{self._name} external_battery_voltage"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:battery"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._tracker_device.device_info

class GeoRideFixtimeSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 tracker_device:Device):
        """Set up GeoRide entity."""
        super().__init__(coordinator)
        self._tracker_device = tracker_device
        self._name = tracker_device.tracker.tracker_name
        self.entity_id = f"{ENTITY_ID_FORMAT.format('fixtime')}.{tracker_device.tracker.tracker_id}"# pylint: disable=C0301

        self._state = 0
        self._device_class = "timestamp"

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"fixtime_{self._tracker_device.tracker.tracker_id}"

    @property
    def state(self):
        """state property"""
        return self._tracker_device.tracker.fixtime

    @property
    def name(self):
        """ GeoRide fixtime name """
        return f"{self._name} last fixed position"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:map-clock"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._tracker_device.device_info

class GeoRideBeaconBatterySensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 tracker_beacon:DeviceBeacon):
        """Set up GeoRide entity."""
        super().__init__(coordinator)
        self._tracker_device = tracker_device
        self._name = tracker_device.tracker.tracker_name
        self._unit_of_measurement = "%"
        self.entity_id = f"{ENTITY_ID_FORMAT.format('battery_percent')}.{tracker_beacon.beacon.beacon_id}"# pylint: disable=C0301
        self._state = 0

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"battery_percent_{self._tracker_device.beacon.beacon_id}"

    @property
    def state(self):
        """state property"""
        return self._tracker_device.beacon.battery_level

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ GeoRide internal_battery_voltage name """
        return f"{self._name} battery percent"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:battery"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._tracker_device.device_info