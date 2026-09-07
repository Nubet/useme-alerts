import logging
import sqlite3
import sys

from src.application.alert_new_offers import AlertNewOffers
from src.application.poll_useme_offers import PollUsemeOffers
from src.application.ports import AlertNotifier
from src.application.run_monitoring_cycle import RunMonitoringCycle
from src.domain.config import AppConfig
from src.entrypoints.scheduler import Scheduler
from src.infrastructure.config_loader import ConfigError, load_config
from src.infrastructure.discord_notifier import DiscordNotifier
from src.infrastructure.email_notifier import EmailNotifier
from src.infrastructure.http_client import HttpClient
from src.infrastructure.logging_setup import configure_logging
from src.infrastructure.repositories import SQLiteAlertRepository, SQLiteOfferRepository
from src.infrastructure.sqlite import create_connection, initialize_database
from src.infrastructure.useme_parser import UsemeParser
from src.infrastructure.useme_source import UsemeOfferSource

logger = logging.getLogger(__name__)


def main() -> None:
    configure_logging()

    try:
        config = load_config()
    except ConfigError as exc:
        raise SystemExit(str(exc)) from exc

    run_once = "--once" in sys.argv
    connection = create_connection(config.database_path)
    http_client: HttpClient | None = None

    try:
        initialize_database(connection)
        http_client = HttpClient()
        run_monitoring_cycle = _build_monitoring_cycle(connection, config, http_client)
        scheduler = Scheduler(interval_seconds=config.poll_interval_seconds)

        def task() -> None:
            _run_cycle(run_monitoring_cycle, config)

        if run_once:
            scheduler.run_once(task)
            return

        scheduler.run_forever(task)
    finally:
        if http_client is not None:
            http_client.close()
        connection.close()


def _build_notifiers(config: AppConfig) -> tuple[AlertNotifier, ...]:
    notifiers: list[AlertNotifier] = [DiscordNotifier(config.discord_webhook_url)]

    if config.email_enabled:
        notifiers.append(
            EmailNotifier(
                smtp_host=config.smtp_host or "",
                smtp_port=config.smtp_port or 0,
                smtp_username=config.smtp_username or "",
                smtp_password=config.smtp_password or "",
                alert_email_to=config.alert_email_to or "",
                alert_email_from=config.alert_email_from or "",
            )
        )

    return tuple(notifiers)


def _run_cycle(run_monitoring_cycle: RunMonitoringCycle, config: AppConfig) -> None:
    try:
        run_monitoring_cycle.execute(config)
    except Exception:
        logger.exception("monitoring cycle crashed")


def _build_monitoring_cycle(
    connection: sqlite3.Connection,
    config: AppConfig,
    http_client: HttpClient,
) -> RunMonitoringCycle:
    offer_repository = SQLiteOfferRepository(connection)
    alert_repository = SQLiteAlertRepository(connection)
    parser = UsemeParser()
    offer_source = UsemeOfferSource(http_client=http_client, parser=parser)
    notifiers = _build_notifiers(config)
    poll_useme_offers = PollUsemeOffers(
        offer_source=offer_source,
        offer_repository=offer_repository,
    )
    alert_new_offers = AlertNewOffers(
        alert_repository=alert_repository,
        notifiers=notifiers,
    )
    return RunMonitoringCycle(
        poll_useme_offers=poll_useme_offers,
        alert_new_offers=alert_new_offers,
    )


if __name__ == "__main__":
    main()
