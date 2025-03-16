from lib.api_client import ApiClientBase


class MochiApiBase(ApiClientBase):
    api_path_prefix = "api/"
    auth_type = "basic_auth"

    def get_all_decks(self) -> dict:
        endpoint = "decks"
        return self.request("GET", endpoint)

    def create_card(self, **params) -> dict:
        endpoint = "cards"
        body = {k.replace("_", "-"): v for k, v in params.items()}
        return self.request("POST", endpoint, body)


class MochiApiHelper(MochiApiBase):
    def __init__(self, base_url, token):
        super().__init__(base_url=base_url, token=token)

    def get_deck_id_by_name(self, name: str) -> str:
        decks = self.get_all_decks()['docs']
        for deck in decks:
            if deck["name"] == name and not deck.get("archived?", None):
                return deck["id"]
        raise ValueError(f"Deck with name '{name}' not found")

    def create_base_card(self, deck_id: str, name: str, value: str) -> dict:
        content = "New card from API"
        fields = {
            "name": {
                "id": "name",
                "value": name,
            },
            "V72yjxYh": {
                "id": "V72yjxYh",
                "value": value,
            },
        }
        return self.create_card(content=content, deck_id=deck_id, fields=fields)
