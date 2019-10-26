from homeassistant import config_entries
from .const import DOMAIN

class GeorideConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, info):
        if info is not None:
            # process info

        return self.async_show_form(
            step_id='user',
            data_schema=vol.Schema({
              vol.Required('password'): str
            })
        )