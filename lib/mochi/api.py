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

    def get_cards(self, **filters) -> dict:
        endpoint = "cards"
        if filters:
            filters = {k.replace("_", "-"): v for k, v in filters.items()}
            endpoint += "?"
            endpoint += "&".join([f"{k}={v}" for k, v in filters.items()])
        return self.request("GET", endpoint)


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

    def get_cards_in_deck(self, deck_id: str) -> list[dict]:
        cards = []
        cards_left = True

        _cards = self.get_cards(deck_id=deck_id, limit=100)
        if _cards.get("docs", None):
            cards.extend(_cards["docs"])

            while cards_left:
                _cards = self.get_cards(bookmark=_cards["bookmark"], limit=100)
                if len(_cards["docs"]) > 0:
                    cards.extend(_cards["docs"])
                else:
                    cards_left = False

        return cards
