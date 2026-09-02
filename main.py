from src.application.alert_new_offers import AlertNewOffers
from src.application.ports import AlertNotifier
from src.application.poll_useme_offers import PollUsemeOffers
from src.infrastructure.config_loader import ConfigError, load_config
from src.infrastructure.discord_notifier import DiscordNotifier
from src.infrastructure.email_notifier import EmailNotifier
from src.infrastructure.http_client import HttpClient
from src.infrastructure.repositories import SQLiteAlertRepository, SQLiteOfferRepository
from src.infrastructure.sqlite import create_connection, initialize_database
from src.infrastructure.useme_parser import UsemeParser
from src.infrastructure.useme_source import UsemeOfferSource


def main() -> None:
    try:
        config = load_config()
    except ConfigError as exc:
        raise SystemExit(str(exc)) from exc

    connection = create_connection(config.database_path)
    http_client: HttpClient | None = None

    try:
        initialize_database(connection)
        offer_repository = SQLiteOfferRepository(connection)
        alert_repository = SQLiteAlertRepository(connection)
        http_client = HttpClient()
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
        result = poll_useme_offers.execute(
            source_category_urls=config.useme_urls,
            max_pages_per_category=config.max_pages_per_category,
        )
        alert_result = alert_new_offers.execute(result.new_offers)

        _ = alert_result
    finally:
        if http_client is not None:
            http_client.close()
        connection.close()

    raise SystemExit("Configuration, storage, source, and alert channels loaded. Application runtime starts in phase 8.")


def _build_notifiers(config) -> tuple[AlertNotifier, ...]:
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


if __name__ == "__main__":
    main()
