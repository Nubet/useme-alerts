from src.infrastructure.config_loader import ConfigError, load_config
from src.infrastructure.sqlite import create_connection, initialize_database


def main() -> None:
    try:
        config = load_config()
    except ConfigError as exc:
        raise SystemExit(str(exc)) from exc

    connection = create_connection(config.database_path)
    try:
        initialize_database(connection)
    finally:
        connection.close()

    raise SystemExit("Configuration and database loaded. Application runtime starts in phase 4.")


if __name__ == "__main__":
    main()
