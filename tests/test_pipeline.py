"""
Automated Test Suite for Data Collection and Processing Pipeline.
Covers API integration, web scraping, JSON processing, data analysis, and utilities.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch
import pytest

from analysis import analyze_book_data, analyze_user_data
from api_data import (
    extract_company_names,
    fetch_users_from_api,
    process_user_records,
)
from json_processing import (
    filter_books_by_min_rating,
    filter_users_by_company_keyword,
    generate_summary_report,
)
from utils import (
    calculate_average_price,
    load_json,
    save_json,
    validate_book_record,
    validate_user_record,
)
from web_scraping import (
    extract_books_from_html,
    parse_price,
    parse_star_rating,
)


# --- 1. Utilities Tests ---

def test_calculate_average_price_valid() -> None:
    items = [
        {"numeric_price": 10.00},
        {"numeric_price": 20.00},
        {"numeric_price": 30.00},
    ]
    assert calculate_average_price(items) == 20.00


def test_calculate_average_price_empty() -> None:
    assert calculate_average_price([]) == 0.0


def test_save_and_load_json_roundtrip(tmp_path) -> None:
    test_file = tmp_path / "test.json"
    sample_data = {"key": "value", "currency": "£50.00", "rating": 5}
    save_json(sample_data, test_file)

    loaded = load_json(test_file)
    assert loaded == sample_data
    assert loaded["currency"] == "£50.00"  # Verify clean UTF-8 encoding


def test_validation_helpers() -> None:
    valid_user = {"name": "Alice", "email": "alice@example.com", "company": "Tech Corp"}
    invalid_user = {"name": "Bob"}
    assert validate_user_record(valid_user) is True
    assert validate_user_record(invalid_user) is False

    valid_book = {
        "title": "Clean Code",
        "price": "£30.00",
        "numeric_price": 30.0,
        "rating": 5,
    }
    invalid_book = {"title": "Unknown", "price": "free"}
    assert validate_book_record(valid_book) is True
    assert validate_book_record(invalid_book) is False


# --- 2. API Integration Tests ---

@patch("api_data.requests.get")
def test_fetch_users_from_api_success(mock_get) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "name": "Jane Doe",
            "username": "jdoe",
            "email": "jane@example.com",
            "company": {"name": "Alpha Group"},
        }
    ]
    mock_get.return_value = mock_response

    users = fetch_users_from_api("https://fake-url.com")
    assert len(users) == 1
    assert users[0]["name"] == "Jane Doe"


@patch("api_data.requests.get")
def test_fetch_users_from_api_http_error(mock_get) -> None:
    import requests
    mock_get.side_effect = requests.exceptions.HTTPError("404 Not Found")

    with pytest.raises(requests.exceptions.RequestException):
        fetch_users_from_api("https://fake-url.com")


def test_process_user_records() -> None:
    raw = [
        {
            "name": "John Doe",
            "username": "johnd",
            "email": "john@test.com",
            "company": {"name": "Beta LLC"},
        }
    ]
    processed = process_user_records(raw)
    assert len(processed) == 1
    assert processed[0]["company"] == "Beta LLC"
    assert "username" not in processed[0]


def test_extract_company_names() -> None:
    raw = [
        {"company": {"name": "Acme Inc"}},
        {"company": {"name": "Globex"}},
        {"company": None},
    ]
    names = extract_company_names(raw)
    assert names == ["Acme Inc", "Globex"]


# --- 3. Web Scraping Tests ---

SAMPLE_HTML = """
<article class="product_pod">
    <h3><a title="A Light in the Attic" href="catalogue/a-light.html">A Light...</a></h3>
    <p class="star-rating Three"></p>
    <div class="product_price">
        <p class="price_color">£51.77</p>
    </div>
</article>
<article class="product_pod">
    <h3><a title="Sharp Objects" href="catalogue/sharp.html">Sharp Objects</a></h3>
    <p class="star-rating Five"></p>
    <div class="product_price">
        <p class="price_color">£47.82</p>
    </div>
</article>
"""

def test_extract_books_from_html() -> None:
    books = extract_books_from_html(SAMPLE_HTML)
    assert len(books) == 2
    assert books[0]["title"] == "A Light in the Attic"
    assert books[0]["numeric_price"] == 51.77
    assert books[0]["rating"] == 3
    assert books[0]["price"] == "£51.77"

    assert books[1]["title"] == "Sharp Objects"
    assert books[1]["numeric_price"] == 47.82
    assert books[1]["rating"] == 5


# --- 4. JSON Processing Tests ---

def test_json_processing_filters() -> None:
    sample_books = [
        {"title": "Book 1", "price": "£10.00", "numeric_price": 10.0, "rating": 5},
        {"title": "Book 2", "price": "£20.00", "numeric_price": 20.0, "rating": 3},
    ]
    high_rated = filter_books_by_min_rating(sample_books, min_rating=5)
    assert high_rated == ["Book 1"]

    sample_users = [
        {"name": "Alice", "email": "a@test.com", "company": "Omega Group"},
        {"name": "Bob", "email": "b@test.com", "company": "Solaris Ltd"},
    ]
    group_users = filter_users_by_company_keyword(sample_users, keyword="Group")
    assert len(group_users) == 1
    assert group_users[0]["name"] == "Alice"


def test_generate_summary_report() -> None:
    users = [{"name": "A", "email": "a@b.com", "company": "Apex Group"}]
    books = [{"title": "B1", "price": "£10", "numeric_price": 10.0, "rating": 5}]
    report = generate_summary_report(users, books)

    assert report["total_users"] == 1
    assert report["total_books"] == 1
    assert report["average_price"] == 10.0
    assert report["metrics"]["five_star_books_count"] == 1


# --- 5. Data Analysis Tests ---

def test_data_analysis_metrics() -> None:
    users = [
        {"name": "Alice", "company": "Apple"},
        {"name": "Bob", "company": "Google"},
        {"name": "Charlie", "company": "Apple"},
    ]
    user_analysis = analyze_user_data(users)
    assert user_analysis["total_users"] == 3
    assert user_analysis["unique_companies_count"] == 2

    books = [
        {"title": "B1", "price": "£10", "numeric_price": 10.0, "rating": 3},
        {"title": "B2", "price": "£20", "numeric_price": 20.0, "rating": 5},
        {"title": "B3", "price": "£30", "numeric_price": 30.0, "rating": 5},
    ]
    book_analysis = analyze_book_data(books)
    assert book_analysis["total_books"] == 3
    assert book_analysis["average_price"] == 20.0
    assert book_analysis["median_price"] == 20.0
    assert book_analysis["max_rating"] == 5
    assert len(book_analysis["highest_rated_books"]) == 2
    assert book_analysis["rating_distribution"][5] == 2
    assert book_analysis["rating_distribution"][3] == 1
