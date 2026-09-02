from dataclasses import dataclass
from datetime import datetime

from .offers import Offer


@dataclass(slots=True, frozen=True)
class NewOfferDetected:
    offer: Offer
    detected_at: datetime
