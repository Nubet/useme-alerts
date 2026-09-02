from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class AppConfig:
    useme_urls: tuple[str, ...]
    poll_interval_seconds: int
    discord_webhook_url: str
    email_enabled: bool
    smtp_host: str | None
    smtp_port: int | None
    smtp_username: str | None
    smtp_password: str | None
    alert_email_to: str | None
    alert_email_from: str | None
    database_path: Path
