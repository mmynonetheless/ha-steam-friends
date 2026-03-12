"""Constants for Steam Friends integration."""
DOMAIN = "steam_friends"
CONF_API_KEY = "api_key"
CONF_STEAM_ID = "steam_id"
DEFAULT_SCAN_INTERVAL = 300
ATTRIBUTION = "Data provided by Steam Web API"

STEAM_API_BASE = "https://api.steampowered.com"
STEAM_GET_FRIENDS = f"{STEAM_API_BASE}/ISteamUser/GetFriendList/v1/"
STEAM_GET_PLAYER_SUMMARIES = f"{STEAM_API_BASE}/ISteamUser/GetPlayerSummaries/v2/"
