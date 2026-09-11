# Useme Scraper Execution Flow

1. **Trigger**
   - `Scheduler` executes `PollUsemeOffers` every `POLL_INTERVAL_SECONDS`.
   - Input: Target URLs (`USEME_URLS`), max pages limit (`MAX_PAGES_PER_CATEGORY`).

2. **HTTP Fetching (`UsemeOfferSource`)**
   - Executes an HTTP GET request on the target URL.
   - Output: Raw HTML string.

3. **HTML Parsing (`UsemeParser`)**
   - Parses the HTML string using `BeautifulSoup`.
   - Locates job containers using `JOB_ARTICLE_SELECTOR`.
   - Extracts data fields using specific CSS selectors:
     - Title
     - Job URL
     - Author (`AUTHOR_CANDIDATE_SELECTORS`)
     - Excerpt (`EXCERPT_CANDIDATE_SELECTORS`)
     - Expiration Label (`EXPIRES_CANDIDATE_SELECTORS`)
   - Normalizes text (removes newlines and extra spaces).
   - Locates the "Next Page" URL.
   - Output: List of `Offer` objects.

4. **Pagination**
   - Repeats steps 2 and 3 using the "Next Page" URL.
   - Stops when the "Next Page" URL is missing or the page limit is reached.

5. **Database Sync (`SQLiteOfferRepository`)**
   - Iterates through the list of parsed `Offer` objects.
   - Queries the database to check if `Offer.url` exists.
   - **If the URL exists:** Updates the `last_seen` timestamp in the database.
   - **If the URL does not exist:**
     - Inserts the `Offer` into the database.
     - Generates a `NewOfferDetected` event.

6. **Notification (`AlertNewOffers`)**
   - Receives the generated `NewOfferDetected` events.
   - Sends the offer data to active channels (`DiscordNotifier`, `EmailNotifier`).
