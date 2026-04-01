import time
import random
import pandas as pd
from bs4 import BeautifulSoup
import cloudscraper

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive",
}

BASE_URL = "https://www.trustpilot.com/review/www.amazon.com"


def clean_text(text):
    return " ".join(str(text).split()).strip()


def extract_reviews_from_page(html):
    soup = BeautifulSoup(html, "html.parser")
    reviews = []
    seen = set()

    selectors = [
        '[data-service-review-text-typography="true"]',
        '[data-review-content="true"]',
        'p.typography_body-l__KUYFJ',
        'article p',
    ]

    for selector in selectors:
        for tag in soup.select(selector):
            text = clean_text(tag.get_text(" ", strip=True))
            if len(text) >= 80 and text not in seen:
                seen.add(text)
                reviews.append(text)

    return reviews


def scrape_trustpilot_reviews(max_pages=50, stop_after_empty=3):
    scraper = cloudscraper.create_scraper(
        browser={
            "browser": "chrome",
            "platform": "darwin",
            "mobile": False
        }
    )
    scraper.headers.update(HEADERS)

    all_rows = []
    seen_reviews = set()
    empty_count = 0

    for page in range(1, max_pages + 1):
        url = f"{BASE_URL}?page={page}"
        print(f"\nDownloading page {page}: {url}")

        try:
            response = scraper.get(url, timeout=20)
        except Exception as e:
            print(f"Request failed: {e}")
            break

        print("Status:", response.status_code)

        if response.status_code == 403:
            print("Blocked by Trustpilot (403 Forbidden).")
            print(response.text[:300])
            break

        if response.status_code != 200:
            print(f"Unexpected status code: {response.status_code}")
            break

        page_reviews = extract_reviews_from_page(response.text)
        print(f"Found {len(page_reviews)} possible reviews")

        added = 0
        for review in page_reviews:
            if review not in seen_reviews:
                seen_reviews.add(review)
                all_rows.append({
                    "website": "Amazon",
                    "source": "Trustpilot",
                    "page": page,
                    "review_text": review
                })
                added += 1

        print(f"Added {added} new reviews")

        if added == 0:
            empty_count += 1
        else:
            empty_count = 0

        if empty_count >= stop_after_empty:
            print("Stopping: several pages returned no new reviews.")
            break

        time.sleep(random.uniform(3, 6))

    df = pd.DataFrame(all_rows)
    if not df.empty:
        df.insert(0, "review_id", range(1, len(df) + 1))
    return df


if __name__ == "__main__":
    df = scrape_trustpilot_reviews(max_pages=50)
    df.to_excel("amazon_reviews.xlsx", index=False)
    print(f"\nSaved {len(df)} reviews.")
    print(df.head())