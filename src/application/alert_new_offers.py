from dataclasses import dataclass

from src.application.ports import AlertNotifier, AlertRepository
from src.domain.alerts import AlertAttempt, AlertChannel, AlertStatus
from src.domain.events import NewOfferDetected


@dataclass(slots=True, frozen=True)
class AlertNewOffersResult:
    delivered_count: int
    failed_count: int


class AlertNewOffers:
    def __init__(
        self,
        alert_repository: AlertRepository,
        notifiers: tuple[AlertNotifier, ...],
    ):
        self._alert_repository = alert_repository
        self._notifiers = notifiers

    def execute(self, events: tuple[NewOfferDetected, ...]) -> AlertNewOffersResult:
        delivered_count = 0
        failed_count = 0

        for event in events:
            for notifier in self._notifiers:
                alert_id = self._alert_repository.add(
                    AlertAttempt(
                        offer_url=event.offer.url,
                        channel=AlertChannel(notifier.channel),
                        status=AlertStatus.PENDING,
                        created_at=event.detected_at,
                    )
                )

                try:
                    notifier.send(event)
                except Exception as exc:
                    failed_count += 1
                    self._alert_repository.update_status(
                        alert_id=alert_id,
                        status=AlertStatus.FAILED,
                        sent_at=None,
                        error_message=str(exc),
                    )
                    continue

                delivered_count += 1
                self._alert_repository.update_status(
                    alert_id=alert_id,
                    status=AlertStatus.SENT,
                    sent_at=event.detected_at.isoformat(),
                    error_message=None,
                )

        return AlertNewOffersResult(
            delivered_count=delivered_count,
            failed_count=failed_count,
        )
