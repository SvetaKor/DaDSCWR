from steam_openid import SteamOpenID

class SteamOpenIDAdapter:
    def __init__(self, realm: str, return_to: str) -> None:
        self._client = SteamOpenID(realm=realm, return_to=return_to)

    def get_redirect_url(self) -> str:
        return self._client.get_redirect_url()

    def validate_and_get_steam_id(self, query_params: dict) -> str | None:
        return self._client.validate_results(query_params)
    