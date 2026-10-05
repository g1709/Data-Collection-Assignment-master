"""
Main Entry Point.
Provides an interactive menu-driven CLI to execute pipeline tasks sequentially or individually.
"""

from __future__ import annotations

import sys

from analysis import analyze_data
from api_data import fetch_api_data
from json_processing import process_json_data
from utils import get_logger
from web_scraping import scrape_book_data

logger = get_logger("main")


def display_menu() -> None:
    """Renders the CLI interactive selection menu."""
    print("=" * 44)
    print("   Data Collection and Processing Pipeline   ")
    print("=" * 44)
    print("1. Fetch API Data (JSONPlaceholder Users)")
    print("2. Scrape Book Data (Books to Scrape)")
    print("3. Process & Generate JSON Reports")
    print("4. Analyze Data & Generate Insights")
    print("5. Exit")
    print("=" * 44)


def main() -> None:
    """Interactive loop managing user choice and routing execution."""
    while True:
        try:
            display_menu()
            choice = input("Enter your choice (1-5): ").strip()

            if choice == "1":
                fetch_api_data()
            elif choice == "2":
                scrape_book_data()
            elif choice == "3":
                process_json_data()
            elif choice == "4":
                analyze_data()
            elif choice == "5":
                print("Exiting pipeline. Goodbye!")
                sys.exit(0)
            else:
                print("Invalid choice. Please enter a valid number between 1 and 5.\n")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user. Exiting...")
            sys.exit(0)
        except Exception as exc:
            logger.error("An unexpected error occurred during execution: %s", exc)
            print(f"Error: {exc}. Please try again.\n")


if __name__ == "__main__":
    main()
