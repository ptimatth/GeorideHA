""" georide custom conpennt """
from collections import defaultdict

from georideapilib.objects import GeorideAccount
import georideapilib.api as GeorideApi

import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_WEBHOOK_ID
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant.setup import async_when_setup

from .const import (
    CONF_EMAIL,
    CONF_PASSWORD,
    TRACKER_ID
)

DOMAIN = "georide"

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
            DOMAIN, context={"source": config_entries.SOURCE_IMPORT}, data={}
        )
    )

    _LOGGER.info("Georide-setup ")


    # Return boolean to indicate that initialization was successful.
    return True



async def async_setup_entry(hass, entry):
    """Set up Georide entry."""
    config = hass.data[DOMAIN]["config"]
    email = config.get(CONF_EMAIL) or entry.data[CONF_EMAIL]
    password = config.get(CONF_PASSWORD) or entry.data[CONF_PASSWORD]

    if email is None or password is None:
        return False

    account = GeorideApi.get_authorisation_token(email, password)
    context = GeorideContext(
        hass,
        email,
        password,
        account.auth_token
    )

    hass.data[DOMAIN]["context"] = context
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "device_tracker"))
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(entry, "switch"))



    return True

async def async_unload_entry(hass, entry):
    """Unload an Georide config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "device_tracker")
    await hass.config_entries.async_forward_entry_unload(entry, "switch")

    hass.data[DOMAIN]["unsub"]()

    return True


class GeorideContext:
    """Hold the current Georide context."""

    def __init__(self, hass, email, password, token):
        """Initialize an Georide context."""
        self._hass = hass
        self._email = email
        self._password = password
        self._georide_trackers = defaultdict(set)
        self._token = token

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


    @callback
    def async_get_token(self):
        """ here we return the current valid tocken, TODO: add here token expiration control"""
        return self._token

