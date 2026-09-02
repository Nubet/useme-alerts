import requests

from src.application.ports import AlertNotifier
from src.domain.events import NewOfferDetected


class DiscordNotifier(AlertNotifier):
    channel = "discord"

    def __init__(self, webhook_url: str):
        self._webhook_url = webhook_url

    def send(self, event: NewOfferDetected) -> None:
        response = requests.post(
            self._webhook_url,
            json={"content": self._format_message(event)},
            timeout=20,
        )
        response.raise_for_status()

    def _format_message(self, event: NewOfferDetected) -> str:
        expires_label = event.offer.expires_label or "n/a"
        author = event.offer.author or "n/a"
        excerpt = event.offer.excerpt or "n/a"
        return (
            "NOWE USEME\n\n"
            f"Title: {event.offer.title}\n"
            f"Author: {author}\n"
            f"Category URL: {event.offer.source_category_url}\n"
            f"Detected at: {event.detected_at.isoformat()}\n"
            f"Expires: {expires_label}\n"
            f"Excerpt: {excerpt}\n\n"
            f"Link:\n{event.offer.url}"
        )
