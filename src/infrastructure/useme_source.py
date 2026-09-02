from src.application.ports import OfferSource
from src.domain.offers import Offer
from src.infrastructure.http_client import HttpClient
from src.infrastructure.useme_parser import UsemeParser


class UsemeOfferSource(OfferSource):
    def __init__(self, http_client: HttpClient, parser: UsemeParser):
        self._http_client = http_client
        self._parser = parser

    def fetch_offers(self, source_category_url: str, max_pages: int) -> list[Offer]:
        offers: list[Offer] = []
        current_url: str | None = source_category_url
        page_count = 0

        while current_url is not None and page_count < max_pages:
            html = self._http_client.get_text(current_url)
            offers.extend(self._parser.parse_offers(html, source_category_url))
            current_url = self._parser.get_next_page_url(html, current_url)
            page_count += 1

        return offers
