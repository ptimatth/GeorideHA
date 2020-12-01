""" Georide config flow """

import logging
from homeassistant import config_entries
import voluptuous as vol
import georideapilib.api as GeoRideApi
import georideapilib.exception as GeoRideException


from .const import CONF_EMAIL, CONF_PASSWORD, CONF_TOKEN


_LOGGER = logging.getLogger(__name__)

@config_entries.HANDLERS.register("georide")
class GeoRideConfigFlow(config_entries.ConfigFlow):
    """GeoRide config flow """
    
    async def async_step_user(self, user_input=None): #pylint: disable=W0613
        """ handle info to help to configure GeoRide """

        if self._async_current_entries():
            return self.async_abort(reason="one_instance_allowed")

        return self.async_show_form(step_id='georide_login', data_schema=vol.Schema({
            vol.Required(CONF_EMAIL): vol.All(str, vol.Length(min=3)),
            vol.Required(CONF_PASSWORD): vol.All(str)
        }))

    async def async_step_import(self, user_input=None): #pylint: disable=W0613
        """Import a config flow from configuration."""
        if self._async_current_entries():
            return self.async_abort(reason="one_instance_allowed")

        return self.async_show_form(step_id='georide_login', data_schema=vol.Schema({
            vol.Required(CONF_EMAIL): vol.All(str, vol.Length(min=3)),
            vol.Required(CONF_PASSWORD): vol.All(str)
        }))



    async def async_step_georide_login(self, user_input):
        """ try to seupt GeoRide Account """

        schema = vol.Schema({
            vol.Required(CONF_EMAIL): vol.All(str, vol.Length(min=3)),
            vol.Required(CONF_PASSWORD): vol.All(str)
        })
        
        if user_input is None:
            return self.async_show_form(step_id='georide_login', data_schema=schema)
        
        email = user_input[CONF_EMAIL]
        password = user_input[CONF_PASSWORD]
        
        try:
            account = GeoRideApi.get_authorisation_token(email, password)
            data = {
                CONF_EMAIL: email,
                CONF_PASSWORD: password,
                CONF_TOKEN: account.auth_token
            }
            return self.async_create_entry(title=email, data=data)
        except (GeoRideException.SeverException, GeoRideException.LoginException):
            _LOGGER.error("Invalid credentials provided, config not created")
            errors = {"base":  "faulty_credentials"}
            return self.async_show_form(step_id="georide_login", data_schema=schema, errors=errors)
        except: 
            _LOGGER.error("Unknown error")
            errors = {"base": "unkonwn"}
            return self.async_show_form(step_id="georide_login", data_schema=schema, errors=errors)
        