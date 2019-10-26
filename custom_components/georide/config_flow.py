""" Georide config flow """

from homeassistant import config_entries
import voluptuous as vol

from .const import DOMAIN, CONF_EMAIL, CONF_PASSWORD

STEP_ID = 'user'

class GeorideConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Geride config flow """
    
    async def async_step_user(self, user_input=None):
        """ handle info to help to configure georide """
        if user_input is  None:
            return self.async_show_form(step_id=STEP_ID, data_schema=vol.Schema({
                vol.Required(CONF_EMAIL): vol.All(str, vol.Length(min=3)),
                vol.Required(CONF_PASSWORD): vol.All(str)
            }))
            # process info

