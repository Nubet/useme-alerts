from pathlib import Path
from typing import Mapping

from dotenv import load_dotenv
import os

from src.domain.config import AppConfig


class ConfigError(ValueError):
    pass


def load_config() -> AppConfig:
    load_dotenv()

    useme_urls = _parse_useme_urls(os.environ)
    poll_interval_seconds = _parse_poll_interval_seconds(os.environ)
    discord_webhook_url = _require_str(os.environ, "DISCORD_WEBHOOK_URL")
    email_enabled = _parse_bool(os.environ.get("EMAIL_ENABLED", "false"))

    smtp_host = _optional_str(os.environ, "SMTP_HOST")
    smtp_port = _optional_int(os.environ, "SMTP_PORT")
    smtp_username = _optional_str(os.environ, "SMTP_USERNAME")
    smtp_password = _optional_str(os.environ, "SMTP_PASSWORD")
    alert_email_to = _optional_str(os.environ, "ALERT_EMAIL_TO")
    alert_email_from = _optional_str(os.environ, "ALERT_EMAIL_FROM")
    database_path = Path(_require_str(os.environ, "DATABASE_PATH"))

    if email_enabled:
        _validate_email_config(
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_username=smtp_username,
            smtp_password=smtp_password,
            alert_email_to=alert_email_to,
            alert_email_from=alert_email_from,
        )

    return AppConfig(
        useme_urls=useme_urls,
        poll_interval_seconds=poll_interval_seconds,
        discord_webhook_url=discord_webhook_url,
        email_enabled=email_enabled,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_username=smtp_username,
        smtp_password=smtp_password,
        alert_email_to=alert_email_to,
        alert_email_from=alert_email_from,
        database_path=database_path,
    )


def _parse_useme_urls(env: Mapping[str, str]) -> tuple[str, ...]:
    raw_value = _require_str(env, "USEME_URLS")
    urls = tuple(url.strip() for url in raw_value.split(",") if url.strip())
    if not urls:
        raise ConfigError("USEME_URLS must contain at least one URL")

    invalid_urls = [url for url in urls if not url.startswith("https://useme.com/")]
    if invalid_urls:
        invalid = ", ".join(invalid_urls)
        raise ConfigError(f"USEME_URLS contains unsupported URLs: {invalid}")

    return urls


def _parse_poll_interval_seconds(env: Mapping[str, str]) -> int:
    value = _require_str(env, "POLL_INTERVAL_SECONDS")
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ConfigError("POLL_INTERVAL_SECONDS must be an integer") from exc

    if parsed < 30:
        raise ConfigError("POLL_INTERVAL_SECONDS must be at least 30")

    return parsed


def _require_str(env: Mapping[str, str], key: str) -> str:
    value = env.get(key, "").strip()
    if not value:
        raise ConfigError(f"Missing required environment variable: {key}")
    return value


def _optional_str(env: Mapping[str, str], key: str) -> str | None:
    value = env.get(key, "").strip()
    return value or None


def _optional_int(env: Mapping[str, str], key: str) -> int | None:
    value = _optional_str(env, key)
    if value is None:
        return None

    try:
        return int(value)
    except ValueError as exc:
        raise ConfigError(f"{key} must be an integer") from exc


def _parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off", ""}:
        return False
    raise ConfigError("EMAIL_ENABLED must be a boolean value")


def _validate_email_config(
    *,
    smtp_host: str | None,
    smtp_port: int | None,
    smtp_username: str | None,
    smtp_password: str | None,
    alert_email_to: str | None,
    alert_email_from: str | None,
) -> None:
    missing = []
    if smtp_host is None:
        missing.append("SMTP_HOST")
    if smtp_port is None:
        missing.append("SMTP_PORT")
    if smtp_username is None:
        missing.append("SMTP_USERNAME")
    if smtp_password is None:
        missing.append("SMTP_PASSWORD")
    if alert_email_to is None:
        missing.append("ALERT_EMAIL_TO")
    if alert_email_from is None:
        missing.append("ALERT_EMAIL_FROM")

    if missing:
        raise ConfigError(
            "Email delivery is enabled but required variables are missing: "
            + ", ".join(missing)
        )
