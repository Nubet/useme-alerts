from email.message import EmailMessage
import smtplib

from src.application.ports import AlertNotifier
from src.domain.alerts import AlertChannel
from src.domain.events import NewOfferDetected


class EmailNotifier(AlertNotifier):
    channel = AlertChannel.EMAIL

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_username: str,
        smtp_password: str,
        alert_email_to: str,
        alert_email_from: str,
    ):
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._smtp_username = smtp_username
        self._smtp_password = smtp_password
        self._alert_email_to = alert_email_to
        self._alert_email_from = alert_email_from

    def send(self, event: NewOfferDetected) -> None:
        message = EmailMessage()
        message["Subject"] = f"[USEME] New offer: {event.offer.title}"
        message["From"] = self._alert_email_from
        message["To"] = self._alert_email_to
        message.set_content(self._format_body(event))

        with smtplib.SMTP(self._smtp_host, self._smtp_port, timeout=20) as smtp:
            smtp.starttls()
            smtp.login(self._smtp_username, self._smtp_password)
            smtp.send_message(message)

    def _format_body(self, event: NewOfferDetected) -> str:
        expires_label = event.offer.expires_label or "n/a"
        author = event.offer.author or "n/a"
        excerpt = event.offer.excerpt or "n/a"
        return (
            "New Useme offer detected.\n\n"
            f"Title: {event.offer.title}\n"
            f"Author: {author}\n"
            f"Category URL: {event.offer.source_category_url}\n"
            f"Detected at: {event.detected_at.isoformat()}\n"
            f"Expires: {expires_label}\n"
            f"Excerpt: {excerpt}\n\n"
            f"Link:\n{event.offer.url}\n"
        )
