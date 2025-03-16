from urllib.parse import urljoin

from requests import Session
from requests.auth import HTTPBasicAuth


class ApiClientBase:
    api_path_prefix = ""
    auth_type = "basic_auth"
    base_headers = {
        "Content-Type": "application/json",
    }

    def __init__(self, base_url: str, token: str):
        self.base_url = urljoin(base_url, self.api_path_prefix)
        self._session = Session()
        self._session.headers.update(self.base_headers)
        self.auth(token)

    def auth(self, token: str) -> None:
        if self.auth_type == "basic_auth":
            self._session.auth = HTTPBasicAuth(token, '')
        else:
            self._session.headers.update({"Authorization": f"Bearer {token}"})

    def request(self, method: str, endpoint: str, json_body: dict = None) -> dict | None:
        url = urljoin(self.base_url, endpoint)

        response = self._session.request(method=method, url=url, json=json_body)
        response.raise_for_status()

        if not response.text:
            return None
        else:
            return response.json()
