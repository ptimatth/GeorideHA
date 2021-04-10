""" georide custom conpennt """
from collections import defaultdict

import logging
from datetime import timedelta
import math
import time
import json
from threading import Thread
import voluptuous as vol
import jwt

from aiohttp.web import json_response
from georideapilib.objects import GeorideAccount as GeoRideAccount
import georideapilib.api as GeoRideApi

from georideapilib.socket import GeorideSocket as GeoRideSocket

from homeassistant import config_entries
from homeassistant.const import CONF_WEBHOOK_ID
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
import homeassistant.helpers.event as ha_event

from homeassistant.setup import async_when_setup

from .const import (
    CONF_EMAIL,
    CONF_PASSWORD,
    CONF_TOKEN,
    TRACKER_ID,
    TOKEN_SAFE_DAY,
    MIN_UNTIL_REFRESH,
    DOMAIN
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
    await context.refresh_trackers()

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "device_tracker"))
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "switch"))
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor"))

    return True


async def async_unload_entry(hass, entry):
    """Unload an GeoRide config entry."""

    await hass.config_entries.async_forward_entry_unload(entry, "device_tracker")
    await hass.config_entries.async_forward_entry_unload(entry, "switch")
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")

    context = hass.data[DOMAIN]["context"]
    context.socket.disconnect()

    hass.data[DOMAIN]["unsub"]()

    return True

async def connect_socket(context):
    """subscribe to GeoRide socket"""
    _LOGGER.info("GeoRide socket connexion")
    socket = GeoRideSocket()
    socket.subscribe_locked(context.on_lock_callback)
    socket.subscribe_device(context.on_device_callback)
    socket.subscribe_position(context.on_position_callback)
    socket.subscribe_alarm(context.on_alarm_callback)

    context.socket = socket

    socket.init()
    socket.connect(await context.get_token())


class GeoRideContext:
    """Hold the current GeoRide context."""

    def __init__(self, hass, email, password, token):
        """Initialize an GeoRide context."""
        self._hass = hass
        self._email = email
        self._password = password
        self._georide_trackers = defaultdict(set)
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

    async def get_token(self):
        """ here we return the current valid tocken """
        jwt_data = jwt.decode(self._token, verify=False)
        exp_timestamp = jwt_data['exp']

        epoch = math.ceil(time.time())
        if (exp_timestamp - TOKEN_SAFE_DAY) < epoch:
            _LOGGER.info("Time reached, renew token")

            account = await self._hass.async_add_executor_job(GeoRideApi.get_authorisation_token, self._email, self._password)
            config = self._hass.data[DOMAIN]["config"]
            config[CONF_TOKEN] = account.auth_token
            self._token = account.auth_token


        _LOGGER.info("Token exp data: %s", exp_timestamp)
        return self._token

    async def get_tracker(self, tracker_id):
        """ here we return last tracker by id"""
        epoch_min = math.floor(time.time()/60)
        if (epoch_min % MIN_UNTIL_REFRESH) == 0:
            if epoch_min != self._previous_refresh:
                self._previous_refresh = epoch_min
                await self.refresh_trackers()

        if not self._thread_started:
            _LOGGER.info("Start the thread")
            self._hass.async_add_executor_job(connect_socket, self)
            # We refresh the tracker list each hours
            self._thread_started = True

        for tracker in self._georide_trackers:
            if tracker.tracker_id == tracker_id:
                return tracker
        return None

    async def refresh_trackers(self):
        """Used to refresh the tracker list"""
        _LOGGER.info("Tracker list refresh")
        self._georide_trackers = await GeoRideApi.get_trackers(await self.get_token())

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
        for tracker in self._georide_trackers:
            if tracker.tracker_id == data['trackerId']:
                tracker.locked_latitude = data['lockedLatitude']
                tracker.locked_longitude = data['lockedLongitude']
                tracker.is_locked = data['isLocked']
                return

    @callback
    def on_device_callback(self, data):
        """on device callback"""
        _LOGGER.info("On device received")
        for tracker in self._georide_trackers:
            if tracker.tracker_id == data['trackerId']:
                tracker.status = data['status']
                return
    @callback
    def on_alarm_callback(self, data):
        """on device callback"""
        _LOGGER.info("On alarm received")
        for tracker in self._georide_trackers:
            if tracker.tracker_id == data['trackerId']:
                if data.name == 'vibration':
                    _LOGGER.info("Vibration detected")
                elif data.name == 'exitZone':
                    _LOGGER.info("Exit zone detected")
                elif data.name == 'crash':
                    _LOGGER.info("Crash detected")
                elif data.name == 'crashParking':
                    _LOGGER.info("Crash parking detected")
                elif data.name == 'deviceOffline':
                    _LOGGER.info("Device offline detected")
                elif data.name == 'deviceOnline':
                    _LOGGER.info("Device online detected")
                elif data.name == 'powerCut':
                    _LOGGER.info("powerCut detected")
                else:
                    _LOGGER.warning("Unamanged alarm: ", data.name)

                return

    @callback
    def on_position_callback(self, data):
        """on position callback"""
        _LOGGER.info("On position received")
        for tracker in self._georide_trackers:
            if tracker.tracker_id == data['trackerId']:
                tracker.latitude = data['latitude']
                tracker.longitude = data['longitude']
                tracker.moving = data['moving']
                tracker.speed = data['speed']
                tracker.fixtime = data['fixtime']
                return

