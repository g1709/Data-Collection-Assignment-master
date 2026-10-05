"""
Shared utility functions for the Data Collection and Processing Pipeline.
Provides centralized logging, safe JSON I/O, calculations, and schema validations.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Sequence


def get_logger(name: str = "pipeline") -> logging.Logger:
    """Configures and returns a standardized logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


logger = get_logger("utils")


def load_json(file_path: str | Path) -> Any:
    """Safely loads and parses a JSON file with explicit UTF-8 encoding.

    Args:
        file_path: Path to the JSON file.

    Returns:
        Parsed JSON data (dict or list).

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    path = Path(file_path)
    if not path.is_file():
        logger.error("Target file does not exist: %s", path)
        raise FileNotFoundError(f"File not found: {path}")

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as exc:
        logger.error("Failed to decode JSON from %s: %s", path, exc)
        raise
    except OSError as exc:
        logger.error("I/O error accessing %s: %s", path, exc)
        raise


def save_json(data: Any, file_path: str | Path, indent: int = 4) -> None:
    """Safely serializes and saves data to a JSON file with explicit UTF-8 encoding.

    Args:
        data: Python object to serialize.
        file_path: Output file destination.
        indent: JSON indentation level (default 4).
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=indent, ensure_ascii=False)
        logger.info("Successfully saved JSON data to %s", path)
    except (OSError, TypeError) as exc:
        logger.error("Failed to write JSON data to %s: %s", path, exc)
        raise


def calculate_average_price(
    records: Sequence[dict[str, Any]], price_key: str = "numeric_price"
) -> float:
    """Calculates the average numeric price from a list of records.

    Centralized calculation function to adhere to DRY principles.

    Args:
        records: Collection of item dictionaries.
        price_key: Key name holding the numeric float price.

    Returns:
        Mean price rounded to 2 decimal places, or 0.0 if empty.
    """
    if not records:
        return 0.0
    valid_prices = [
        float(item[price_key])
        for item in records
        if isinstance(item, dict) and price_key in item and item[price_key] is not None
    ]
    if not valid_prices:
        return 0.0
    return round(sum(valid_prices) / len(valid_prices), 2)


def validate_user_record(record: dict[str, Any]) -> bool:
    """Validates the schema of a processed user record."""
    required_keys = {"name", "email", "company"}
    return isinstance(record, dict) and required_keys.issubset(record.keys())


def validate_book_record(record: dict[str, Any]) -> bool:
    """Validates the schema of a scraped book record."""
    required_keys = {"title", "price", "numeric_price", "rating"}
    if not (isinstance(record, dict) and required_keys.issubset(record.keys())):
        return False
    return isinstance(record["numeric_price"], (int, float)) and isinstance(
        record["rating"], int
    )
