"""
Data Analysis Module.
Performs statistical summaries and business insights on collected user and book datasets.
"""

from __future__ import annotations

from collections import Counter
import json
import statistics
from typing import Any

from utils import calculate_average_price, get_logger, load_json, validate_book_record

logger = get_logger("analysis")

DEFAULT_USERS_FILE = "users.json"
DEFAULT_BOOKS_FILE = "books.json"


def analyze_user_data(users: list[dict[str, Any]]) -> dict[str, Any]:
    """Generates analytical metrics on user and organization records."""
    total_users = len(users)
    companies = [
        str(u.get("company")).strip()
        for u in users
        if u.get("company") and str(u.get("company")).strip()
    ]
    unique_companies = sorted(set(companies))
    company_counts = Counter(companies)

    # Top companies by user count or alphabetic representation
    most_common_companies = company_counts.most_common(5)

    return {
        "total_users": total_users,
        "unique_companies_count": len(unique_companies),
        "unique_companies": unique_companies,
        "most_common_companies": most_common_companies,
    }


def analyze_book_data(books: list[dict[str, Any]]) -> dict[str, Any]:
    """Generates descriptive statistics on scraped book records."""
    if not books:
        return {
            "total_books": 0,
            "average_price": 0.0,
            "median_price": 0.0,
            "highest_rated_books": [],
            "rating_distribution": {},
        }

    prices = [
        b["numeric_price"]
        for b in books
        if validate_book_record(b) and "numeric_price" in b
    ]
    ratings = [b["rating"] for b in books if validate_book_record(b)]

    avg_price = calculate_average_price(books)
    med_price = round(statistics.median(prices), 2) if prices else 0.0

    max_rating = max(ratings) if ratings else 0
    highest_rated = [b["title"] for b in books if b.get("rating") == max_rating]

    rating_distribution = dict(sorted(Counter(ratings).items(), reverse=True))

    return {
        "total_books": len(books),
        "average_price": avg_price,
        "median_price": med_price,
        "max_rating": max_rating,
        "highest_rated_books": highest_rated,
        "rating_distribution": rating_distribution,
    }


def analyze_data(
    users_file: str = DEFAULT_USERS_FILE,
    books_file: str = DEFAULT_BOOKS_FILE,
) -> dict[str, Any] | None:
    """Executes Part D tasks: computes and displays statistical insights."""
    print("--- Part D: Data Analysis ---")

    try:
        users = load_json(users_file)
        books = load_json(books_file)
    except FileNotFoundError:
        print("Required JSON files not found. Please run tasks A and B first.")
        return None
    except json.JSONDecodeError as exc:
        print(f"Failed to read data files for analysis: {exc}")
        return None

    user_stats = analyze_user_data(users)
    book_stats = analyze_book_data(books)

    print("\n[User Analysis]")
    print(f"- Total Users: {user_stats['total_users']}")
    print(f"- Unique Companies: {user_stats['unique_companies_count']}")
    top_5_companies = user_stats["unique_companies"][:5]
    print(f"- Top 5 Companies (Alphabetically): {', '.join(top_5_companies)}")

    print("\n[Book Analysis]")
    print(f"- Average Price: £{book_stats['average_price']:.2f}")
    print(f"- Median Price:  £{book_stats['median_price']:.2f}")
    print(f"- Highest Rated Books (Rating {book_stats['max_rating']}):")
    for title in book_stats["highest_rated_books"]:
        print(f"  * {title}")

    print("- Number of Books in Each Rating Category:")
    for rating, count in book_stats["rating_distribution"].items():
        print(f"  * Rating {rating}: {count} books")
    print()

    return {"user_analysis": user_stats, "book_analysis": book_stats}


if __name__ == "__main__":
    analyze_data()
