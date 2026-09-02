from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class Offer:
    title: str
    url: str
    source_category_url: str
    detected_at: datetime
    author: str | None = None
    excerpt: str | None = None
    expires_label: str | None = None
