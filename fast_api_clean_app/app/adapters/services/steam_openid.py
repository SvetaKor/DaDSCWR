# from steam_openid import SteamOpenID

# class SteamOpenIDAdapter:
#     def __init__(self, realm: str, return_to: str) -> None:
#         self._client = SteamOpenID(realm=realm, return_to=return_to)

#     def get_redirect_url(self) -> str:
#         return self._client.get_redirect_url()

#     def validate_and_get_steam_id(self, query_params: dict) -> str | None:
#         # Проверяем, что Steam вернул успешный ответ
#         if query_params.get("openid.mode") != "id_res":
#             return None

#         claimed_id = query_params.get("openid.claimed_id", "")
#         prefix = "https://steamcommunity.com/openid/id/"
#         if not claimed_id.startswith(prefix):
#             return None

#         steam_id = claimed_id[len(prefix):]
#         if not steam_id.isdigit():
#             return None
#         return steam_id
