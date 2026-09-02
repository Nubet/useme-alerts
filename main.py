from src.application.poll_useme_offers import PollUsemeOffers
from src.infrastructure.config_loader import ConfigError, load_config
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
        poll_useme_offers = PollUsemeOffers(
            offer_source=offer_source,
            offer_repository=offer_repository,
        )
        result = poll_useme_offers.execute(
            source_category_urls=config.useme_urls,
            max_pages_per_category=config.max_pages_per_category,
        )

        _ = alert_repository
        _ = result
    finally:
        if http_client is not None:
            http_client.close()
        connection.close()

    raise SystemExit("Configuration, database, and Useme source loaded. Application runtime starts in phase 5.")


if __name__ == "__main__":
    main()
