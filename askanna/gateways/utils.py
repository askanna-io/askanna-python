from typing import Optional
from urllib.parse import parse_qs, urlsplit


class ListResponse:
    def __init__(self, data: dict):
        self.total_count: int = data["count"]
        self.next_url: Optional[str] = data["next"]
        self.previous_url: Optional[str] = data["previous"]
        self.results: dict = data["results"]

    def get_cursor(self, url: str) -> str:
        query_params = parse_qs(urlsplit(url).query)
        return query_params["cursor"][0]

    @property
    def next_url_cursor(self) -> Optional[str]:
        return self.get_cursor(self.next_url) if self.next_url else None

    @property
    def previous_url_cursor(self) -> Optional[str]:
        return self.get_cursor(self.previous_url) if self.previous_url else None
