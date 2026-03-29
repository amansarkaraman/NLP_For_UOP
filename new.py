import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

BASE_URL = "https://www.trustpilot.com/review/www.amazon.com"


def clean_text(text):
    return " ".join(str(text).split()).strip()


def extract_reviews_from_page(html):
    soup = BeautifulSoup(html, "html.parser")
    reviews = []

    # Try several common selectors because site HTML can change
    selectors = [
        '[data-service-review-text-typography="true"]',
        '[data-review-content="true"]',
        'p.typography_body-l__KUYFJ',
        'article p',
    ]

    seen = set()

    for selector in selectors:
        for tag in soup.select(selector):
            text = clean_text(tag.get_text(" ", strip=True))
            if len(text) >= 80 and text not in seen:
                seen.add(text)
                reviews.append(text)

    return reviews


def scrape_trustpilot_reviews(pages=3):
    all_rows = []

    session = requests.Session()
    session.headers.update(HEADERS)

    for page in range(1, pages + 1):
        url = f"{BASE_URL}?page={page}"
        print(f"Downloading page {page}: {url}")

        response = session.get(url, timeout=20)
        response.raise_for_status()

        page_reviews = extract_reviews_from_page(response.text)
        print(f"  Found {len(page_reviews)} possible reviews on this page")

        for review in page_reviews:
            all_rows.append({
                "website": "Amazon",
                "source": "Trustpilot",
                "page": page,
                "review_text": review
            })

        time.sleep(2)

    df = pd.DataFrame(all_rows)
    df = df.drop_duplicates(subset=["review_text"]).reset_index(drop=True)
    df.insert(0, "review_id", range(1, len(df) + 1))
    return df


if __name__ == "__main__":
    df = scrape_trustpilot_reviews(pages=3)

    output_file = "amazon_reviews_test.xlsx"
    df.to_excel(output_file, index=False)

    print("\nDone.")
    print(f"Saved {len(df)} reviews to {output_file}")
    print(df.head(10))