from datetime import datetime
from typing import Protocol

from src.domain.alerts import AlertAttempt, AlertChannel, AlertStatus
from src.domain.events import NewOfferDetected
from src.domain.offers import Offer


class OfferRepository(Protocol):
    def exists_by_url(self, url: str) -> bool:
        ...

    def add(self, offer: Offer) -> bool:
        ...

    def update_last_seen(self, url: str, detected_at: datetime) -> None:
        ...


class AlertRepository(Protocol):
    def add(self, alert_attempt: AlertAttempt) -> int:
        ...

    def update_status(
        self,
        alert_id: int,
        status: AlertStatus,
        sent_at: datetime | None,
        error_message: str | None,
    ) -> None:
        ...


class OfferSource(Protocol):
    def fetch_offers(self, source_category_url: str, max_pages: int) -> list[Offer]:
        ...


class AlertNotifier(Protocol):
    channel: AlertChannel

    def send(self, event: NewOfferDetected) -> None:
        ...
