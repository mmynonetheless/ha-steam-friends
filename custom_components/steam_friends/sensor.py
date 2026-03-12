"""Sensor platform for Steam Friends integration."""
import logging
from datetime import timedelta, datetime
import async_timeout
import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed, CoordinatorEntity
from homeassistant.components.sensor import SensorEntity
from .const import (
    DOMAIN, CONF_API_KEY, CONF_STEAM_ID,
    STEAM_GET_FRIENDS, STEAM_GET_PLAYER_SUMMARIES
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    api_key = entry.data[CONF_API_KEY]
    steam_id = entry.data[CONF_STEAM_ID]
    
    coordinator = SteamFriendsCoordinator(hass, api_key, steam_id, entry)
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([SteamFriendsSensor(coordinator, steam_id)], True)

class SteamFriendsCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api_key, steam_id, entry):
        update_interval = entry.options.get("scan_interval", 300)
        super().__init__(
            hass,
            _LOGGER,
            name="Steam Friends",
            update_interval=timedelta(seconds=update_interval),
        )
        self.api_key = api_key
        self.steam_id = steam_id

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(10):
                return await self._fetch_all_data()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error: {err}")

    async def _fetch_all_data(self):
        async with aiohttp.ClientSession() as session:
            # Get friends list
            friends_url = f"{STEAM_GET_FRIENDS}?key={self.api_key}&steamid={self.steam_id}"
            async with session.get(friends_url) as response:
                if response.status != 200:
                    return {"friends": [], "total_friends": 0}
                
                data = await response.json()
                if "friendslist" not in data:
                    return {"friends": [], "total_friends": 0}
                
                friends = data["friendslist"]["friends"]
                friend_ids = [f["steamid"] for f in friends]
                
                friends_data = {f["steamid"]: f for f in friends}
            
            # Get details for all friends
            if friend_ids:
                ids_param = ",".join(friend_ids[:100])
                details_url = f"{STEAM_GET_PLAYER_SUMMARIES}?key={self.api_key}&steamids={ids_param}"
                async with session.get(details_url) as details_response:
                    if details_response.status == 200:
                        details_data = await details_response.json()
                        if "response" in details_data and "players" in details_data["response"]:
                            for player in details_data["response"]["players"]:
                                if player["steamid"] in friends_data:
                                    friends_data[player["steamid"]].update(player)
            
            return {
                "friends": list(friends_data.values()),
                "total_friends": len(friends_data),
                "last_update": datetime.now().isoformat()
            }

class SteamFriendsSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, steam_id):
        super().__init__(coordinator)
        self._steam_id = steam_id
        self._attr_name = "Steam Friends"
        self._attr_unique_id = f"steam_friends_{steam_id}"
        self._attr_icon = "mdi:steam"

    @property
    def native_value(self):
        if not self.coordinator.data:
            return 0
        return self.coordinator.data.get("total_friends", 0)

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        return {
            "friends": self.coordinator.data.get("friends", []),
            "total_friends": self.coordinator.data.get("total_friends", 0),
            "last_update": self.coordinator.data.get("last_update", "")
        }
