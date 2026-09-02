from dataclasses import dataclass
import logging

from src.application.ports import OfferRepository, OfferSource
from src.domain.events import NewOfferDetected


logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class PollUsemeOffersResult:
    fetched_offers_count: int
    new_offers_count: int
    source_errors_count: int
    new_offers: tuple[NewOfferDetected, ...]


class PollUsemeOffers:
    def __init__(
        self,
        offer_source: OfferSource,
        offer_repository: OfferRepository,
    ):
        self._offer_source = offer_source
        self._offer_repository = offer_repository

    def execute(
        self,
        source_category_urls: tuple[str, ...],
        max_pages_per_category: int,
    ) -> PollUsemeOffersResult:
        fetched_offers_count = 0
        source_errors_count = 0
        new_offers: list[NewOfferDetected] = []

        for source_category_url in source_category_urls:
            try:
                offers = self._offer_source.fetch_offers(
                    source_category_url=source_category_url,
                    max_pages=max_pages_per_category,
                )
            except Exception:
                source_errors_count += 1
                logger.exception("failed to fetch offers for %s", source_category_url)
                continue

            fetched_offers_count += len(offers)

            for offer in offers:
                if self._offer_repository.exists_by_url(offer.url):
                    self._offer_repository.update_last_seen(
                        url=offer.url,
                        detected_at=offer.detected_at,
                    )
                    continue

                inserted = self._offer_repository.add(offer)
                if not inserted:
                    self._offer_repository.update_last_seen(
                        url=offer.url,
                        detected_at=offer.detected_at,
                    )
                    continue

                new_offers.append(
                    NewOfferDetected(
                        offer=offer,
                        detected_at=offer.detected_at,
                    )
                )

        return PollUsemeOffersResult(
            fetched_offers_count=fetched_offers_count,
            new_offers_count=len(new_offers),
            source_errors_count=source_errors_count,
            new_offers=tuple(new_offers),
        )
