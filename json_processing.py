"""
JSON Processing and Aggregation Module.
Reads collected datasets, applies filtering logic, and generates a structured summary report.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from utils import (
    calculate_average_price,
    get_logger,
    load_json,
    save_json,
    validate_book_record,
    validate_user_record,
)

logger = get_logger("json_processing")

DEFAULT_USERS_FILE = "users.json"
DEFAULT_BOOKS_FILE = "books.json"
DEFAULT_REPORT_FILE = "report.json"


def filter_books_by_min_rating(
    books: list[dict[str, Any]], min_rating: int = 5
) -> list[str]:
    """Returns book titles having a rating strictly greater than or equal to min_rating."""
    matching_titles: list[str] = []
    for book in books:
        if validate_book_record(book) and book.get("rating", 0) >= min_rating:
            matching_titles.append(book["title"])
    return matching_titles


def filter_users_by_company_keyword(
    users: list[dict[str, Any]], keyword: str = "Group"
) -> list[dict[str, Any]]:
    """Returns user records whose company name contains the specified keyword."""
    matching_users: list[dict[str, Any]] = []
    for user in users:
        if validate_user_record(user):
            company_name = str(user.get("company", ""))
            if keyword.lower() in company_name.lower():
                matching_users.append(user)
    return matching_users


def generate_summary_report(
    users: list[dict[str, Any]], books: list[dict[str, Any]]
) -> dict[str, Any]:
    """Builds a comprehensive aggregated summary report."""
    avg_price = calculate_average_price(books)
    five_star_count = sum(1 for b in books if b.get("rating") == 5)
    group_company_users = sum(
        1 for u in users if "group" in str(u.get("company", "")).lower()
    )

    return {
        "total_users": len(users),
        "total_books": len(books),
        "average_price": avg_price,
        "metrics": {
            "five_star_books_count": five_star_count,
            "users_in_group_companies": group_company_users,
        },
    }


def process_json_data(
    users_file: str = DEFAULT_USERS_FILE,
    books_file: str = DEFAULT_BOOKS_FILE,
    report_file: str = DEFAULT_REPORT_FILE,
) -> dict[str, Any] | None:
    """Executes Part C tasks: reading, filtering, reporting, and validating datasets."""
    print("--- Part C: JSON Processing ---")

    try:
        users = load_json(users_file)
        books = load_json(books_file)
    except FileNotFoundError:
        print("Required JSON files not found. Please run tasks A and B first.")
        return None
    except json.JSONDecodeError as exc:
        print(f"Error parsing JSON files: {exc}")
        return None

    # Validate dataset formats
    if not isinstance(users, list) or not isinstance(books, list):
        print("Invalid data format: JSON files must contain lists of records.")
        return None

    # Task C1: Print total records
    print(f"\n[Task C1] Total Users Records: {len(users)}")
    print(f"[Task C1] Total Books Records: {len(books)}")

    # Task C2: Display all book titles with rating greater than 4 (i.e. rating == 5)
    print("\n[Task C2] Books with rating greater than 4:")
    high_rating_titles = filter_books_by_min_rating(books, min_rating=5)
    for title in high_rating_titles:
        print(f"- {title}")

    # Task C3: Display all users belonging to companies containing "Group"
    print("\n[Task C3] Users in companies containing 'Group':")
    group_users = filter_users_by_company_keyword(users, keyword="Group")
    for user in group_users:
        print(f"- {user.get('name')} ({user.get('company')})")

    # Task C4: Create and save combined JSON report
    report = generate_summary_report(users, books)
    save_json(report, report_file)
    print(f"\n[Task C4] Saved combined report to {report_file}: {report}\n")

    return report


if __name__ == "__main__":
    process_json_data()
