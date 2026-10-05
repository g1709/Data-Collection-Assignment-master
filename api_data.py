"""
API Data Collection Module.
Fetches, processes, and persists user records from the JSONPlaceholder REST API.
"""

from __future__ import annotations

import sys
from typing import Any
import requests
from requests.exceptions import RequestException

from utils import get_logger, save_json, validate_user_record

logger = get_logger("api_data")

DEFAULT_API_URL = "https://jsonplaceholder.typicode.com/users"
DEFAULT_OUTPUT_FILE = "users.json"
DEFAULT_TIMEOUT_SECONDS = 10


def fetch_users_from_api(
    url: str = DEFAULT_API_URL, timeout: int = DEFAULT_TIMEOUT_SECONDS
) -> list[dict[str, Any]]:
    """Retrieves raw user data from the REST API endpoint.

    Args:
        url: API endpoint URL.
        timeout: Network timeout in seconds.

    Returns:
        List of raw user dictionaries.

    Raises:
        RequestException: If the HTTP request fails.
        ValueError: If the response is not valid JSON.
    """
    logger.info("Connecting to REST API: %s", url)
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            raise ValueError(f"Expected list of users, received {type(data).__name__}")
        logger.info("Successfully fetched %d user records from API.", len(data))
        return data
    except RequestException as exc:
        logger.error("HTTP request failed for URL %s: %s", url, exc)
        raise
    except ValueError as exc:
        logger.error("Failed to parse JSON response from %s: %s", url, exc)
        raise


def extract_company_names(raw_users: list[dict[str, Any]]) -> list[str]:
    """Extracts non-empty company names from raw user records."""
    companies: list[str] = []
    for user in raw_users:
        company_obj = user.get("company")
        if isinstance(company_obj, dict):
            cname = company_obj.get("name")
            if cname:
                companies.append(str(cname).strip())
    return companies


def process_user_records(raw_users: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Transforms raw API user records into cleaned dictionary format."""
    processed: list[dict[str, Any]] = []
    for user in raw_users:
        company_name = ""
        company_obj = user.get("company")
        if isinstance(company_obj, dict):
            company_name = company_obj.get("name", "")

        record = {
            "name": user.get("name", "Unknown"),
            "email": user.get("email", ""),
            "company": company_name,
        }
        if validate_user_record(record):
            processed.append(record)
        else:
            logger.warning("Skipping invalid user record: %s", record)
    return processed


def fetch_api_data(
    url: str = DEFAULT_API_URL,
    output_file: str = DEFAULT_OUTPUT_FILE,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> list[dict[str, Any]] | None:
    """Executes Part A tasks: fetching, filtering, printing, and persisting users."""
    print("--- Part A: API Data Collection ---")
    try:
        users = fetch_users_from_api(url=url, timeout=timeout)
    except (RequestException, ValueError) as exc:
        print(f"Failed to fetch data from API: {exc}")
        return None

    # Task A1: Display specific fields for each user
    print("\n[Task A1] User Records:")
    for user in users:
        company_name = user.get("company", {}).get("name", "")
        print(
            f"Name: {user.get('name')}, "
            f"Username: {user.get('username')}, "
            f"Email: {user.get('email')}, "
            f"Company: {company_name}"
        )

    # Task A2: Count total number of users
    total_users = len(users)
    print(f"\n[Task A2] Total Users: {total_users}")

    # Task A3: Extract all company names
    company_names = extract_company_names(users)
    print(f"\n[Task A3] Company Names: {company_names}")

    # Task A4: Process records into cleaned dictionaries
    processed_users = process_user_records(users)
    print(f"\n[Task A4] Created processed user list of dictionaries ({len(processed_users)} records).")

    # Task A5: Save into users.json
    save_json(processed_users, output_file)
    print(f"[Task A5] Saved processed API data to {output_file}.\n")

    return processed_users


if __name__ == "__main__":
    fetch_api_data()
