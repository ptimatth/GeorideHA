""" Georide config flow file """

from homeassistant import config_entries
import voluptuous as vol

from .const import DOMAIN

class GeorideConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Geride config flow """
    async def async_step_user(self, info):
        return self.async_show_form(
            step_id='user',
            data_schema=vol.Schema({
                vol.Required('password'): str
            }))
        