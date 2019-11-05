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
from georideapilib.objects import GeorideAccount
import georideapilib.api as GeorideApi

from georideapilib.socket import GeorideSocket


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
    """Setup  Georide component."""
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
    """Set up Georide entry."""
    config = hass.data[DOMAIN]["config"]
    email = config.get(CONF_EMAIL) or entry.data[CONF_EMAIL]
    password = config.get(CONF_PASSWORD) or entry.data[CONF_PASSWORD]
    token = config.get(CONF_TOKEN) or entry.data[CONF_TOKEN]
    context = GeorideContext(
        hass,
        email,
        password,
        token
    )
    
    _LOGGER.info("Context-setup and start the thread")
    _LOGGER.info("Thread started")

    hass.data[DOMAIN]["context"] = context

    # We add trackers to the context
    trackers = GeorideApi.get_trackers(token)
    context.georide_trackers = trackers

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "device_tracker"))
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "switch"))
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor"))

    return True


async def async_unload_entry(hass, entry):
    """Unload an Georide config entry."""

    await hass.config_entries.async_forward_entry_unload(entry, "device_tracker")
    await hass.config_entries.async_forward_entry_unload(entry, "switch")
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")

    context = hass.data[DOMAIN]["context"]
    context.socket.disconnect()

    hass.data[DOMAIN]["unsub"]()

    return True

def connect_socket(context):
    """subscribe to georide socket"""
    _LOGGER.info("Georide socket connexion")
    socket = GeorideSocket()
    socket.subscribe_locked(context.on_lock_callback)
    socket.subscribe_device(context.on_device_callback)
    socket.subscribe_position(context.on_position_callback)

    context.socket = socket

    socket.init()
    socket.connect(context.get_token())


class GeorideContext:
    """Hold the current Georide context."""

    def __init__(self, hass, email, password, token):
        """Initialize an Georide context."""
        self._hass = hass
        self._email = email
        self._password = password
        self._georide_trackers = defaultdict(set)
        self._token = token
        self._socket = None
        self._thread_started = False

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
        """ georide tracker list """
        return self._georide_trackers

    @georide_trackers.setter
    def georide_trackers(self, trackers):
        """ georide tracker list """
        self._georide_trackers = trackers    

    def get_token(self):
        """ here we return the current valid tocken """
        jwt_data = jwt.decode(self._token, verify=False)
        exp_timestamp = jwt_data['exp']

        epoch = math.ceil(time.time())

        if (exp_timestamp - TOKEN_SAFE_DAY) < epoch:
            _LOGGER.info("Time reached, renew token")
            account = GeorideApi.get_authorisation_token(self._email, self._password)
            config = self._hass.data[DOMAIN]["config"]
            config[CONF_TOKEN] = account.auth_token
            self._token = account.auth_token


        _LOGGER.info("Token exp data: %s", exp_timestamp)
        return self._token

    def get_tracker(self, tracker_id):
        """ here we return last tracker by id"""
        if not self._thread_started:
            _LOGGER.info("Satr the thread")
            self._hass.async_add_executor_job(connect_socket, self)
            self._thread_started = True

        for tracker in self._georide_trackers:
            if tracker.tracker_id == tracker_id:
                return tracker
        return None

    @property
    def socket(self):
        """ hold the georide socket """
        return self._socket
    
    @socket.setter
    def socket(self, socket):
        """set the georide socket"""
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



