from src.infrastructure.config_loader import ConfigError, load_config


def main() -> None:
    try:
        load_config()
    except ConfigError as exc:
        raise SystemExit(str(exc)) from exc

    raise SystemExit("Configuration loaded. Application runtime starts in phase 3.")


if __name__ == "__main__":
    main()
