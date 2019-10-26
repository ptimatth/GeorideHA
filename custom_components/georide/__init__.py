from georideapilib.objects import GeorideAccount
import georideapilib.api as GeorideApi
import voluptuous as vol

from homeassistant import config_entries



DOMAIN = "georide"
CONF_EMAIL = "email"
CONF_PASSWORD = "password"


CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(DOMAIN, default={}): {
            vol.Required(CONF_EMAIL): vol.All(str, Length(min=3)),
            vol.Required(CONF_PASSWORD): vol.All(str)
        }
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass, config):
    """Initialize OwnTracks component."""
    hass.data[DOMAIN] = {"config": config[DOMAIN], "devices": {}, "unsub": None}
    if not hass.config_entries.async_entries(DOMAIN):
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": config_entries.SOURCE_IMPORT}, data={}
            )
        )

    return True

async def async_setup_entry(hass, entry):
    """Set up Georide entry."""
    config = hass.data[DOMAIN]["config"]
    email = config.get(CONF_EMAIL)
    password = config.get(CONF_PASSWORD)
    trackerId = config.get(CONF_TRACKER_ID)
    token = config.get(CONF_TOKEN)

    context = GeorideContext(
        hass,
        email,
        password,
        trackerId, 
        token
    )

    webhook_id = config.get(CONF_WEBHOOK_ID) or entry.data[CONF_WEBHOOK_ID]

    return True

class GeorideContext:
    """Hold the current Georide context."""

    def __init__(
        hass,
        email,
        password,
        trackerId,
        token
    ):
        """Initialize an Georide context."""
        self.hass = hass
        self.email = email
        self.password = password
        self.trackerId = trackerId
        self.token = token

