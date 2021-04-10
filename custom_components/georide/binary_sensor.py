""" odometter sensor for GeoRide object """

import logging

from homeassistant.core import callback
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.binary_sensor import ENTITY_ID_FORMAT

import georideapilib.api as GeoRideApi
import georideapilib.objects as GeoRideTracker

from .const import DOMAIN as GEORIDE_DOMAIN


_LOGGER = logging.getLogger(__name__) 
async def async_setup_entry(hass, config_entry, async_add_entities): # pylint: disable=W0613
    """Set up GeoRide tracker based off an entry."""
    georide_context = hass.data[GEORIDE_DOMAIN]["context"]      
    token = await georide_context.get_token()
    if token is None:
        return False

    trackers = await hass.async_add_executor_job(GeoRideApi.get_trackers,token)
    entities = []
    for tracker in trackers:
        coordinator = DataUpdateCoordinator[Mapping[str, Any]](
            hass,
            _LOGGER,
            name=tracker.tracker_name,
            update_method=georide_context.get_tracker,
            update_interval=update_interval,
        )
        stolen_entity = GeoRideStolenBinarySensorEntity(coordinator,
                                                        coordinator)
        crashed_entity = GeoRideCrashedBinarySensorEntity(hass,
                                                          tracker)
        entities.append(stolen_entity)
        entities.append(crashed_entity)
        hass.data[GEORIDE_DOMAIN]["devices"][tracker.tracker_id] = coordinator

    async_add_entities(entities, True)

    return True


class GeoRideBinarySensorEntity( CoordinatorEntity,B inarySensorEntity):
    """Represent a tracked device."""
    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]], tracker: GeoRideTracker,  get_token_callback, get_tracker_callback):
        """Set up Georide entity."""
        super().__init__(coordinator)
        self._tracker = tracker
        self._get_token_callback = get_token_callback
        self._get_tracker_callback = get_tracker_callback
        self._name = tracker.tracker_name

        self.entity_id = ENTITY_ID_FORMAT.format("is_stolen") + "." + str(tracker.tracker_id)
        self._state = 0

    @property
    def unique_id(self):
        """Return the unique ID."""
        return self._tracker_id

    @property
    def name(self):
        """ GeoRide odometer name """
        return self._name

    @property
    def state(self):
        return self._state
    
    @property
    def get_token_callback(self):
        """ GeoRide switch token callback method """
        return self._get_token_callback
    
    @property
    def get_tracker_callback(self):
        """ GeoRide switch token callback method """
        return self._get_tracker_callback
    

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "name": self.name,
            "identifiers": {(GEORIDE_DOMAIN, self._tracker_id)},
            "manufacturer": "GeoRide"
        }

class GeoRideStolenBinarySensorEntity(GeoRideBinarySensorEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]], tracker: GeoRideTracker):
        """Set up Georide entity."""
        super().__init__(coordinator, tracker, hass, get_tracker_callback,get_tracker_callback)

        self.entity_id = ENTITY_ID_FORMAT.format("is_stolen") + "." + str(tracker_id)

     async def async_update(self):
        """ update the current tracker"""
        _LOGGER.info('update')
        self._name = self._tracker.tracker_name
        self._state = self._tracker.is_stolen

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"is_stolen_{self._tracker_id}"


class GeoRideCrashedBinarySensorEntity(GeoRideBinarySensorEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]], tracker: GeoRideTracker):
        """Set up Georide entity."""
        super().__init__(coordinator, tracker)
        self.entity_id = ENTITY_ID_FORMAT.format("is_crashed") + "." + str(tracker_id)

    async def async_update(self):
        """ update the current tracker"""
        _LOGGER.info('update')
        self._name = self._tracker.tracker_name
        self._state = self._tracker.is_crashed

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"is_crashed_{self._tracker_id}"
