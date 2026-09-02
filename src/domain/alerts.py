from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class AlertChannel(StrEnum):
    DISCORD = "discord"
    EMAIL = "email"


class AlertStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


@dataclass(slots=True, frozen=True)
class AlertAttempt:
    offer_url: str
    channel: AlertChannel
    status: AlertStatus
    created_at: datetime
    sent_at: datetime | None = None
    error_message: str | None = None
