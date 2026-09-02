from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from src.domain.clock import utc_now
from src.domain.offers import Offer
from src.infrastructure.useme_selectors import (
    AUTHOR_CANDIDATE_SELECTORS,
    EXCERPT_CANDIDATE_SELECTORS,
    EXPIRES_CANDIDATE_SELECTORS,
    JOB_ARTICLE_SELECTOR,
    JOB_CONTENT_SELECTOR,
    NEXT_PAGE_SELECTOR,
)


class UsemeParser:
    def parse_offers(self, html: str, source_category_url: str) -> list[Offer]:
        soup = BeautifulSoup(html, "html.parser")
        offers: list[Offer] = []

        for job_article in soup.select(JOB_ARTICLE_SELECTOR):
            offer = self._parse_offer(job_article, source_category_url)
            if offer is not None:
                offers.append(offer)

        return offers

    def get_next_page_url(self, html: str, current_url: str) -> str | None:
        soup = BeautifulSoup(html, "html.parser")
        next_link = soup.select_one(NEXT_PAGE_SELECTOR)
        if next_link is None:
            return None

        href = next_link.get("href", "").strip()
        if not href:
            return None

        return urljoin(current_url, href)

    def _parse_offer(self, job_article: Tag, source_category_url: str) -> Offer | None:
        content = job_article.select_one(JOB_CONTENT_SELECTOR)
        if content is None:
            return None

        link = content.find("a", href=True)
        if link is None:
            return None

        title = self._normalize_text(link.get_text(" ", strip=True))
        if not title:
            return None

        offer_url = urljoin("https://useme.com", link.get("href", ""))
        if not offer_url.startswith("https://useme.com/"):
            return None

        return Offer(
            title=title,
            url=offer_url,
            source_category_url=source_category_url,
            detected_at=utc_now(),
            author=self._extract_author(job_article),
            excerpt=self._extract_excerpt(job_article),
            expires_label=self._extract_expires_label(job_article),
        )

    def _extract_author(self, job_article: Tag) -> str | None:
        for selector in AUTHOR_CANDIDATE_SELECTORS:
            element = job_article.select_one(selector)
            if element is None:
                continue

            value = self._normalize_text(element.get_text(" ", strip=True))
            if value:
                return value

        return None

    def _extract_excerpt(self, job_article: Tag) -> str | None:
        for selector in EXCERPT_CANDIDATE_SELECTORS:
            element = job_article.select_one(selector)
            if element is None:
                continue

            value = self._normalize_text(element.get_text(" ", strip=True))
            if value:
                return value

        return None

    def _extract_expires_label(self, job_article: Tag) -> str | None:
        for selector in EXPIRES_CANDIDATE_SELECTORS:
            element = job_article.select_one(selector)
            if element is None:
                continue

            value = self._normalize_text(element.get_text(" ", strip=True))
            if value and "znika" in value.lower():
                return value

        return None

    @staticmethod
    def _normalize_text(value: str) -> str:
        return " ".join(value.split())
