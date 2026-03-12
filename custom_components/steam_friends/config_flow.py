"""Config flow for Steam Friends integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import aiohttp
import async_timeout

from .const import DOMAIN, CONF_API_KEY, CONF_STEAM_ID

class SteamFriendsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        
        if user_input is not None:
            valid = await self._validate_credentials(
                user_input[CONF_API_KEY],
                user_input[CONF_STEAM_ID]
            )
            if valid:
                return self.async_create_entry(
                    title=f"Steam Friends ({user_input[CONF_STEAM_ID]})",
                    data=user_input
                )
            errors["base"] = "invalid_auth"
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY): str,
                vol.Required(CONF_STEAM_ID): str,
            }),
            errors=errors,
        )

    async def _validate_credentials(self, api_key, steam_id):
        url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={api_key}&steamids={steam_id}"
        try:
            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            return bool(data.get("response", {}).get("players"))
        except:
            return False
        return False

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)

class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional("scan_interval", default=300): vol.All(
                    vol.Coerce(int), vol.Range(min=60, max=3600)
                ),
            })
        )
