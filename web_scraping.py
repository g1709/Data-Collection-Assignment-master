"""
Web Scraping Module.
Extracts book records (title, price, star ratings) from books.toscrape.com with pagination.
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
import requests
from requests.exceptions import RequestException

from utils import calculate_average_price, get_logger, save_json, validate_book_record

logger = get_logger("web_scraping")

BASE_URL = "https://books.toscrape.com/"
DEFAULT_OUTPUT_FILE = "books.json"
DEFAULT_TIMEOUT_SECONDS = 10
RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


def parse_star_rating(article: Tag) -> int:
    """Safely extracts and converts star rating class to integer."""
    star_elem = article.find("p", class_="star-rating")
    if not star_elem:
        return 0
    classes = star_elem.get("class", [])
    for cls_name in classes:
        if cls_name in RATING_MAP:
            return RATING_MAP[cls_name]
    return 0


def parse_price(article: Tag) -> tuple[str, float]:
    """Safely extracts formatted price string and numeric float value."""
    price_elem = article.find("p", class_="price_color")
    if not price_elem:
        return ("£0.00", 0.0)

    raw_text = price_elem.get_text(strip=True).replace("\u00c2", "")
    match = re.search(r"[\d\.]+", raw_text)
    numeric_price = float(match.group()) if match else 0.0
    formatted_price = f"£{numeric_price:.2f}"
    return (formatted_price, numeric_price)


def parse_title(article: Tag) -> str:
    """Safely extracts full book title from article DOM element."""
    h3_elem = article.find("h3")
    if h3_elem:
        link_elem = h3_elem.find("a")
        if link_elem:
            return link_elem.get("title") or link_elem.get_text(strip=True)
    return "Unknown Title"


def extract_books_from_html(html_content: str) -> list[dict[str, Any]]:
    """Parses HTML content and extracts book records."""
    soup = BeautifulSoup(html_content, "html.parser")
    articles = soup.find_all("article", class_="product_pod")
    books: list[dict[str, Any]] = []

    for article in articles:
        title = parse_title(article)
        price_text, price_num = parse_price(article)
        rating_num = parse_star_rating(article)

        record = {
            "title": title,
            "price": price_text,
            "numeric_price": price_num,
            "rating": rating_num,
        }
        if validate_book_record(record):
            books.append(record)
        else:
            logger.warning("Skipping malformed book record: %s", record)

    return books


def scrape_books_with_pagination(
    start_url: str = BASE_URL,
    max_pages: int = 5,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> list[dict[str, Any]]:
    """Scrapes book records across multiple pages using pagination links."""
    all_books: list[dict[str, Any]] = []
    current_url = start_url
    pages_crawled = 0

    session = requests.Session()
    session.headers.update({"User-Agent": "DataEngineeringStudent/2.0"})

    while current_url and pages_crawled < max_pages:
        logger.info("Scraping page %d: %s", pages_crawled + 1, current_url)
        try:
            response = session.get(current_url, timeout=timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or "utf-8"
        except RequestException as exc:
            logger.error("Failed to retrieve page %s: %s", current_url, exc)
            break

        page_books = extract_books_from_html(response.text)
        all_books.extend(page_books)
        pages_crawled += 1

        soup = BeautifulSoup(response.text, "html.parser")
        next_elem = soup.select_one("li.next a")
        if next_elem and next_elem.get("href"):
            next_href = next_elem["href"]
            current_url = urljoin(current_url, next_href)
        else:
            logger.info("No further pagination links found. Crawl complete.")
            break

    logger.info("Extracted %d total books across %d pages.", len(all_books), pages_crawled)
    return all_books


def scrape_book_data(
    start_url: str = BASE_URL,
    output_file: str = DEFAULT_OUTPUT_FILE,
    max_pages: int = 5,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> list[dict[str, Any]] | None:
    """Executes Part B tasks: scraping, cleaning, summarizing, and persisting books."""
    print("--- Part B: Web Scraping ---")
    try:
        book_list = scrape_books_with_pagination(
            start_url=start_url, max_pages=max_pages, timeout=timeout
        )
    except Exception as exc:
        print(f"Failed to scrape book data: {exc}")
        return None

    if not book_list:
        print("No book data extracted.")
        return None

    # Task B1 & B2 & B3 verification
    print(f"\n[Task B1 & B2 & B3] Extracted {len(book_list)} books across {max_pages} pages.")

    # Task B4: Find most expensive, least expensive, and average price
    most_expensive = max(book_list, key=lambda x: x["numeric_price"])
    least_expensive = min(book_list, key=lambda x: x["numeric_price"])
    avg_price = calculate_average_price(book_list)

    print("\n[Task B4]")
    print(f"Most Expensive Book: {most_expensive['title']} at {most_expensive['price']}")
    print(f"Least Expensive Book: {least_expensive['title']} at {least_expensive['price']}")
    print(f"Average Book Price: £{avg_price:.2f}")

    # Task B5: Save into books.json with UTF-8 encoding
    save_json(book_list, output_file)
    print(f"\n[Task B5] Saved extracted data to {output_file}.\n")

    return book_list


if __name__ == "__main__":
    scrape_book_data()
