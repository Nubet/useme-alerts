from dataclasses import dataclass

from src.application.alert_new_offers import AlertNewOffers
from src.application.poll_useme_offers import PollUsemeOffers
from src.domain.config import AppConfig


@dataclass(slots=True, frozen=True)
class MonitoringCycleResult:
    fetched_offers_count: int
    new_offers_count: int
    delivered_alerts_count: int
    failed_alerts_count: int


class RunMonitoringCycle:
    def __init__(
        self,
        poll_useme_offers: PollUsemeOffers,
        alert_new_offers: AlertNewOffers,
    ):
        self._poll_useme_offers = poll_useme_offers
        self._alert_new_offers = alert_new_offers

    def execute(self, config: AppConfig) -> MonitoringCycleResult:
        poll_result = self._poll_useme_offers.execute(
            source_category_urls=config.useme_urls,
            max_pages_per_category=config.max_pages_per_category,
        )
        alert_result = self._alert_new_offers.execute(poll_result.new_offers)

        return MonitoringCycleResult(
            fetched_offers_count=poll_result.fetched_offers_count,
            new_offers_count=poll_result.new_offers_count,
            delivered_alerts_count=alert_result.delivered_count,
            failed_alerts_count=alert_result.failed_count,
        )
