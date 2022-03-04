""" georide custom conpennt """
from collections import defaultdict

import asyncio
import logging
from typing import Any, Mapping
from datetime import timedelta
import math
import time
import json
from threading import Thread
import voluptuous as vol
import jwt

from aiohttp.web import json_response
from georideapilib.objects import GeoRideAccount
import georideapilib.api as GeoRideApi

from georideapilib.socket import GeoRideSocket

from homeassistant import config_entries
from homeassistant.const import CONF_WEBHOOK_ID
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
import homeassistant.helpers.event as ha_event

from homeassistant.setup import async_when_setup
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)


from .device import Device
from .const import (
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_TOKEN,
    TRACKER_ID,
    TOKEN_SAFE_DAY,
    MIN_UNTIL_REFRESH,
    DOMAIN,
    SIREN_ACTIVATION_DELAY
)



_LOGGER = logging.getLogger(__name__)


CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(DOMAIN, default={}): {
            vol.Optional(CONF_EMAIL): vol.All(str, vol.Length(min=3)),
            vol.Optional(CONF_PASSWORD): vol.All(str)
        }
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Setup  GeoRide component."""
    hass.data[DOMAIN] = {"config": config[DOMAIN], "devices": {}, "unsub": None}
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_IMPORT
            },
            data={}
        )
    )

    # Return boolean to indicate that initialization was successful.
    return True


async def async_setup_entry(hass, entry):
    """Set up GeoRide entry."""
    config = hass.data[DOMAIN]["config"]
    email = config.get(CONF_EMAIL) or entry.data[CONF_EMAIL]
    password = config.get(CONF_PASSWORD) or entry.data[CONF_PASSWORD]
    token = config.get(CONF_TOKEN) or entry.data[CONF_TOKEN]
    context = GeoRideContext(
        hass,
        email,
        password,
        token
    )

    _LOGGER.info("Context-setup and start the thread")
    _LOGGER.info("Thread started")

    hass.data[DOMAIN]["context"] = context

    # We add trackers to the context
    await context.init_context(hass)

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "device_tracker"))
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "switch"))
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor"))
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "binary_sensor"))
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "siren"))
    return True


async def async_unload_entry(hass, entry):
    """Unload an GeoRide config entry."""

    await hass.config_entries.async_forward_entry_unload(entry, "device_tracker")
    await hass.config_entries.async_forward_entry_unload(entry, "switch")
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    await hass.config_entries.async_forward_entry_unload(entry, "binary_sensor")
    await hass.config_entries.async_forward_entry_unload(entry, "siren")


    context = hass.data[DOMAIN]["context"]
    context.socket.disconnect()

    return True



class GeoRideContext:
    """Hold the current GeoRide context."""

    def __init__(self, hass, email, password, token):
        """Initialize an GeoRide context."""
        self._hass = hass
        self._email = email
        self._password = password
        self._georide_trackers_coordoned = []
        self._georide_trackers_beacon_coordoned = []
        self._georide_trackers_beacon = []
        self._georide_trackers = []
        self._token = token
        self._socket = None
        self._thread_started = False
        self._previous_refresh = math.floor(time.time()/60)
    @property
    def hass(self):
        """ hass """
        return self._hass

    @property
    def email(self):
        """ current email """
        return self._email

    @property
    def password(self):
        """ password """
        return self._password

    @property
    def token(self):
        """ current jwt token """
        return self._token

    @property
    def georide_trackers(self):
        """ GeoRide tracker list """
        return self._georide_trackers

    @georide_trackers.setter
    def georide_trackers(self, trackers):
        """ GeoRide tracker list """
        self._georide_trackers = trackers

    async def connect_socket(self):
        """subscribe to GeoRide socket"""
        _LOGGER.info("GeoRide socket connexion")
        socket = GeoRideSocket()
        socket.subscribe_locked(self.on_lock_callback)
        socket.subscribe_device(self.on_device_callback)
        socket.subscribe_position(self.on_position_callback)
        socket.subscribe_alarm(self.on_alarm_callback)
        self._socket = socket

        socket.init()
        self._hass.async_add_executor_job(socket.connect, await self.get_token())

    async def get_token(self):
        """ here we return the current valid tocken """
        jwt_data = jwt.decode(self._token, options={"verify_signature": False})
        exp_timestamp = jwt_data['exp']

        epoch = math.ceil(time.time())
        if (exp_timestamp - TOKEN_SAFE_DAY) < epoch:
            _LOGGER.info("Time reached, renew token")
            account = await self._hass.async_add_executor_job(GeoRideApi.get_authorisation_token,
                                                              self._email, self._password)
            config = self._hass.data[DOMAIN]["config"]
            config[CONF_TOKEN] = account.auth_token
            self._token = account.auth_token


        _LOGGER.info("Token exp data: %s", exp_timestamp)
        return self._token

    async def get_tracker(self, tracker_id):
        """ here we return last tracker by id"""
        await self.refresh_trackers()
        for tracker in self._georide_trackers:
            if tracker.tracker_id == tracker_id:
                return tracker
        return {}

    async def get_tracker_beacon(self, beacon_id):
        """ here we return last tracker_beacon by id"""
        for tracker_beacon in self._georide_trackers_beacon:
            if tracker_beacon.beacon_id == beacon_id:
                return tracker_beacon
        return {}
    
    async def get_tracker_beacons_by_tracker_id(self, tracker_id):
        """ here we return last tracker_beacon by id"""
        filtered_beacon = []
        for tracker_beacon in self._georide_trackers_beacon:
            if tracker_beacon.linked_tracker_id == tracker_id:
                filtered_beacon.append(tracker_beacon)
        return filtered_beacon

    async def refresh_trackers(self):
        """ here we return last tracker by id"""
        _LOGGER.debug("Call refresh tracker")
        epoch_min = math.floor(time.time()/60)
        if epoch_min != self._previous_refresh:
            self._previous_refresh = epoch_min
            await self.force_refresh_trackers()
        for tracker in self._georide_trackers:
            if tracker.is_siren_on:
                if time.time() - SIREN_ACTIVATION_DELAY > tracker.siren_last_on_date:
                    tracker.is_siren_on = False

    async def force_refresh_trackers(self):
        """Used to refresh the tracker list"""
        _LOGGER.info("Tracker list refresh")
        new_georide_trackers = await self._hass.async_add_executor_job(GeoRideApi.get_trackers,
                                                                       await self.get_token())
        for refreshed_tracker in new_georide_trackers:
            found = False
            for tracker in self._georide_trackers:
                if tracker.tracker_id == refreshed_tracker.tracker_id:
                    tracker.update_all_data(refreshed_tracker)
                    if tracker.version > 2:
                        await self.force_refresh_trackers_beacon(tracker.tracker_id)
                    found = True
            if not found:
                self._georide_trackers.append(refreshed_tracker)
                if refreshed_tracker.version > 2:
                    await self.force_refresh_trackers_beacon(refreshed_tracker.tracker_id)
        if not self._thread_started:
            _LOGGER.info("Start the thread")
            # We refresh the tracker list each hours
            self._thread_started = True
            await self.connect_socket()

    async def force_refresh_trackers_beacon(self, tracker_id):
        """Used to refresh the tracker list"""
        _LOGGER.info("Tracker beacon refresh")
        new_georide_tracker_beacons = await self._hass.async_add_executor_job(GeoRideApi.get_tracker_beacon,
                                                                       await self.get_token(), tracker_id)
        for new_georide_tracker_beacon in new_georide_tracker_beacons:
            found = False
            for tracker_beacon in self._georide_trackers_beacon:
                if tracker_beacon.tracker_id == new_georide_tracker_beacon.beacon_id:
                    tracker_beacon.update_all_data(new_georide_tracker_beacon)
                    found = True
            if not found:
                self._georide_trackers_beacon.append(new_georide_tracker_beacon)
        if not self._thread_started:
            _LOGGER.info("Start the thread")
            # We refresh the tracker list each hours
            self._thread_started = True
            await self.connect_socket()

    async def init_context(self, hass):
        """Used to refresh the tracker list"""
        _LOGGER.info("Init_context")
        await self.force_refresh_trackers()
        update_interval = timedelta(minutes=MIN_UNTIL_REFRESH)

        for tracker in self._georide_trackers:
            coordinator = DataUpdateCoordinator[Mapping[str, Any]](
                hass,
                _LOGGER,
                name=tracker.tracker_name,
                update_method=self.refresh_trackers,
                update_interval=update_interval
            )

            coordoned_tracker = {
                "tracker_device": Device(tracker),
                "coordinator": coordinator
            }
            if tracker.version > 2:
                tracker_beacons = await self.get_tracker_beacon_by_tracker_id(tracker.tracker_id)
                for tracker_beacon in tracker_beacons:
                    beacon_coordinator = DataUpdateCoordinator[Mapping[str, Any]](
                        hass,
                        _LOGGER,
                        name= tracker_beacon.name
                    )
                    coordoned_beacon = {
                        "beacon_device": DeviceBeacon(tracker_beacon),
                        "coordinator": coordinator
                    }
                    self._georide_trackers_beacon_coordoned.append(coordoned_beacon)
            self._georide_trackers_coordoned.append(coordoned_tracker)


    @property
    def georide_trackers_coordoned(self):
        """Return coordoned trackers"""

        return self._georide_trackers_coordoned

    @property
    def georide_trackers_beacon_coordoned(self):
        """Return coordoned trackers"""

        return self._georide_trackers_beacon_coordoned

    @property
    def socket(self):
        """ hold the GeoRide socket """
        return self._socket

    @socket.setter
    def socket(self, socket):
        """set the GeoRide socket"""
        self._socket = socket

    @callback
    def on_lock_callback(self, data):
        """on lock callback"""
        _LOGGER.info("On lock received")
        for coordoned_tracker in self._georide_trackers_coordoned:
            tracker_device = coordoned_tracker['tracker_device']
            tracker = tracker_device.tracker
            coordinator = coordoned_tracker['coordinator']
            if tracker.tracker_id == data['trackerId']:
                tracker.locked_latitude = data['lockedLatitude']
                tracker.locked_longitude = data['lockedLongitude']
                tracker.is_locked = data['isLocked']

                event_data = {
                    "device_id": tracker_device.unique_id,
                    "device_name": tracker_device.name,
                }
                self._hass.bus.async_fire(f"{DOMAIN}_lock_event", event_data)

                asyncio.run_coroutine_threadsafe(
                    coordinator.async_request_refresh(), self._hass.loop
                ).result()
                break

    @callback
    def on_device_callback(self, data):
        """on device callback"""
        _LOGGER.info("On device received")
        for coordoned_tracker in self._georide_trackers_coordoned:
            tracker_device = coordoned_tracker['tracker_device']
            tracker = tracker_device.tracker
            coordinator = coordoned_tracker['coordinator']
            if tracker.tracker_id == data['trackerId']:
                tracker.status = data['status']
                event_data = {
                    "device_id": tracker_device.unique_id,
                    "device_name": tracker_device.name,
                }
                self._hass.bus.async_fire(f"{DOMAIN}_device_event", event_data)
                asyncio.run_coroutine_threadsafe(
                    coordinator.async_request_refresh(), self._hass.loop
                ).result()
                break

    @callback
    def on_alarm_callback(self, data):
        """on device callback"""
        _LOGGER.info("On alarm received")
        for coordoned_tracker in self._georide_trackers_coordoned:
            tracker_device = coordoned_tracker['tracker_device']
            tracker = tracker_device.tracker

            coordinator = coordoned_tracker['coordinator']
            if tracker.tracker_id == data['trackerId']:
                if data['name'] == 'vibration':
                    _LOGGER.info("Vibration detected")
                elif data['name'] == 'exitZone':
                    _LOGGER.info("Exit zone detected")
                elif data['name'] == 'crash':
                    _LOGGER.info("Crash detected")
                elif data['name'] == 'crashParking':
                    _LOGGER.info("Crash parking detected")
                elif data['name'] == 'deviceOffline':
                    _LOGGER.info("Device offline detected")
                elif data['name'] == 'deviceOnline':
                    _LOGGER.info("Device online detected")
                elif data['name'] == 'powerCut':
                    _LOGGER.info("powerCut detected")
                elif data['name'] == 'powerUncut':
                    _LOGGER.info("powerUncut detected")
                elif data['name'] == 'batteryWarning':
                    _LOGGER.info("batteryWarning detected")
                elif data['name'] == 'temperatureWarning':
                    _LOGGER.info("temperatureWarning detected")
                elif data['name'] == 'magnetOn':
                    _LOGGER.info("magnetOn detected")
                elif data['name'] == 'magnetOff':
                    _LOGGER.info("magnetOff detected")
                elif data['name'] == 'sonorAlarmOn':
                    _LOGGER.info("sonorAlarmOn detected")
                    tracker.is_siren_on = True
                else:
                    _LOGGER.warning("Unmanaged alarm: %s", data["name"])

                event_data = {
                    "device_id": tracker_device.unique_id,
                    "device_name": tracker_device.name,
                    "type": f"alarm_{data['name']}"
                }
                self._hass.bus.async_fire(f"{DOMAIN}_alarm_event", event_data)
                asyncio.run_coroutine_threadsafe(
                    coordinator.async_request_refresh(), self._hass.loop
                ).result()
                break

    @callback 
    def on_position_callback(self, data):
        """on position callback"""
        _LOGGER.info("On position received")
        for coordoned_tracker in self._georide_trackers_coordoned:
            tracker = coordoned_tracker['tracker_device'].tracker
            coordinator = coordoned_tracker['coordinator']
            if tracker.tracker_id == data['trackerId']:
                tracker.latitude = data['latitude']
                tracker.longitude = data['longitude']
                tracker.moving = data['moving']
                tracker.speed = data['speed']
                tracker.fixtime = data['fixtime']

                event_data = {
                    "device_id": tracker_device.unique_id,
                    "device_name": tracker_device.name,
                }
                self._hass.bus.async_fire(f"{DOMAIN}_position_event", event_data)
                asyncio.run_coroutine_threadsafe(
                    coordinator.async_request_refresh(), self._hass.loop
                ).result()
                break

