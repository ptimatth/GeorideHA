""" Georide config flow """

import logging
from homeassistant import config_entries
import voluptuous as vol


from .const import CONF_EMAIL, CONF_PASSWORD


_LOGGER = logging.getLogger(__name__)

@config_entries.HANDLERS.register("georide")
class GeorideConfigFlow(config_entries.ConfigFlow):
    """Georide config flow """
    
    async def async_step_user(self, user_input=None):
        """ handle info to help to configure georide """

        if self._async_current_entries():
            return self.async_abort(reason="one_instance_allowed")

        if user_input is None:
            return self.async_show_form(step_id='user', data_schema=vol.Schema({
                vol.Required(CONF_EMAIL): vol.All(str, vol.Length(min=3)),
                vol.Required(CONF_PASSWORD): vol.All(str)
            }))

        return self.async_create_entry(
            title=user_input[CONF_EMAIL],
            data={
                CONF_EMAIL: user_input[CONF_EMAIL],
                CONF_PASSWORD: user_input[CONF_PASSWORD]            
            }
        )



    async def async_step_import(self, user_input):
        """Import a config flow from configuration."""

        _LOGGER.info("user email: %", str(user_input))

        if self._async_current_entries():
            return self.async_abort(reason="one_instance_allowed")

        if user_input is None:
            return self.async_show_form(step_id='user', data_schema=vol.Schema({
                vol.Required(CONF_EMAIL): vol.All(str, vol.Length(min=3)),
                vol.Required(CONF_PASSWORD): vol.All(str)
            }))

        return self.async_create_entry(
            title=user_input,
            data={
                CONF_EMAIL: user_input[CONF_EMAIL],
                CONF_PASSWORD: user_input[CONF_PASSWORD]            
            }
        )
        