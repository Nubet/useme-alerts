import sqlite3

from src.application.ports import AlertRepository, OfferRepository
from src.domain.alerts import AlertAttempt, AlertStatus
from src.domain.offers import Offer


class SQLiteOfferRepository(OfferRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def exists_by_url(self, url: str) -> bool:
        row = self.connection.execute(
            "SELECT 1 FROM offers WHERE url = ? LIMIT 1",
            (url,),
        ).fetchone()
        return row is not None

    def add(self, offer: Offer) -> None:
        self.connection.execute(
            """
            INSERT INTO offers (
                url,
                title,
                source_category_url,
                author,
                excerpt,
                expires_label,
                first_seen_at,
                last_seen_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                offer.url,
                offer.title,
                offer.source_category_url,
                offer.author,
                offer.excerpt,
                offer.expires_label,
                offer.detected_at.isoformat(),
                offer.detected_at.isoformat(),
            ),
        )
        self.connection.commit()

    def update_last_seen(self, url: str, detected_at: str) -> None:
        self.connection.execute(
            "UPDATE offers SET last_seen_at = ? WHERE url = ?",
            (detected_at, url),
        )
        self.connection.commit()


class SQLiteAlertRepository(AlertRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def add(self, alert_attempt: AlertAttempt) -> int:
        cursor = self.connection.execute(
            """
            INSERT INTO alerts (
                offer_url,
                channel,
                status,
                created_at,
                sent_at,
                error_message
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                alert_attempt.offer_url,
                alert_attempt.channel.value,
                alert_attempt.status.value,
                alert_attempt.created_at.isoformat(),
                alert_attempt.sent_at.isoformat() if alert_attempt.sent_at else None,
                alert_attempt.error_message,
            ),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def update_status(
        self,
        alert_id: int,
        status: AlertStatus,
        sent_at: str | None,
        error_message: str | None,
    ) -> None:
        self.connection.execute(
            "UPDATE alerts SET status = ?, sent_at = ?, error_message = ? WHERE id = ?",
            (status.value, sent_at, error_message, alert_id),
        )
        self.connection.commit()
