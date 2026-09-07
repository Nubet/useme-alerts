import requests


class HttpClient:
    def __init__(self, timeout_seconds: float = 20.0):
        self._timeout_seconds = timeout_seconds
        self._client = requests.Session()
        self._client.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            }
        )

    def get_text(self, url: str) -> str:
        response = self._client.get(url, timeout=self._timeout_seconds, allow_redirects=True)
        response.raise_for_status()
        return response.text

    def close(self) -> None:
        self._client.close()
