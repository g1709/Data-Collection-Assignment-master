# Data Collection and Processing Pipeline

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Code Style: PEP 8](https://img.shields.io/badge/code%20style-pep8-green.svg)](https://peps.python.org/pep-0008/)
[![Tests: Pytest](https://img.shields.io/badge/tests-pytest-success.svg)](https://docs.pytest.org/)

An enterprise-ready, fault-tolerant data engineering pipeline that extracts data from REST APIs and web pages, validates and cleans datasets, serializes data to UTF-8 JSON, and computes statistical insights.

---

## Project Structure

```text
Data-Collection-Assignment/
│
├── api_data.py             # REST API client with timeouts, retry handling & schema validation
├── web_scraping.py         # Multi-page web scraper with pagination, DOM guards & UTF-8 encoding
├── json_processing.py      # Schema validation, filtering engine & aggregated report generator
├── analysis.py             # Descriptive statistics, frequency distributions & business metrics
├── utils.py                # Centralized logging, safe JSON I/O, DRY calculations & schema validators
├── main.py                 # Menu-driven CLI entry point with defensive error boundaries
│
├── tests/
│   └── test_pipeline.py    # Comprehensive automated test suite (12 unit & integration tests)
│
├── users.json              # Extracted user entities from JSONPlaceholder API
├── books.json              # Extracted book catalogue from books.toscrape.com
├── report.json             # Aggregated summary report with cross-dataset metrics
│
├── requirements.txt        # Pinned production and testing dependencies
├── .gitignore              # Ignores byte-compiled files, caches, and OS artifacts
└── README.md               # Architecture documentation and execution guide
```

---

## Engineering Features

- **Resilient Networking:** Explicit timeouts (`timeout=10`), HTTP status verification (`raise_for_status()`), and comprehensive network error handling (`requests.exceptions.RequestException`).
- **Full Catalogue Pagination:** Web scraper traverses paginated catalog links (`li.next a`) dynamically to collect records across multiple pages.
- **Strict Character Encoding:** Pure UTF-8 enforcement eliminates encoding anomalies and character corruption (e.g. `Â£` mojibake).
- **Zero Code Duplication (DRY):** Common mathematical operations (such as average price) and file operations are centralized in `utils.py`.
- **Schema Validation & Defensive Parsing:** Safe DOM access guards against missing tags or altered class indices; input payloads are validated against required keys.
- **Automated Testing Suite:** 12 automated unit and integration tests using `pytest` and `unittest.mock`.
- **Structured Logging:** Standardized logging using Python's built-in `logging` framework.

---

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/g1709/Data-Collection-Assignment-master.git
   cd Data-Collection-Assignment-master
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## How to Run

### Interactive Menu
Launch the interactive CLI pipeline:
```bash
python main.py
```

### Individual Execution
Run any module independently as a CLI script:
```bash
python api_data.py          # Part A: Fetch API Users
python web_scraping.py      # Part B: Scrape Book Data
python json_processing.py   # Part C: Filter & Generate JSON Report
python analysis.py          # Part D: Run Statistical Analysis
```

---

## Running Automated Tests

Execute the automated test suite with verbose reporting:
```bash
pytest -v
```

All 12 unit tests cover networking mocks, parsing logic, schema validation, calculations, and data filters.

---

## Data Schemas

### `users.json`
```json
[
  {
    "name": "Leanne Graham",
    "email": "Sincere@april.biz",
    "company": "Romaguera-Crona"
  }
]
```

### `books.json`
```json
[
  {
    "title": "A Light in the Attic",
    "price": "£51.77",
    "numeric_price": 51.77,
    "rating": 3
  }
]
```

### `report.json`
```json
{
  "total_users": 10,
  "total_books": 100,
  "average_price": 34.56,
  "metrics": {
    "five_star_books_count": 19,
    "users_in_group_companies": 2
  }
}
```
