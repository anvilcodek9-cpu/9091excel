# Naver Smart Store - Logen Delivery Integration

Python-based automation tool that fetches order data from Naver Smart Store and generates Excel files in Logen delivery service's bulk shipping format.

## Features

- Fetches orders from Naver Commerce API with payment status "PAYED" and shipping status "READY"
- Transforms Naver order data to Logen delivery format
- Generates dated Excel files ready for upload to Logen's bulk shipping system
- Comprehensive error handling with retry logic for API failures
- Validates required fields before processing

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `requests` - HTTP client for Naver Commerce API
- `openpyxl` - Excel file generation
- `pytest` - Testing framework
- `hypothesis` - Property-based testing library

## Configuration

### Access Token

The system requires a Naver Commerce API access token for authentication. You can provide it in two ways:

**Option 1: Environment Variable (Recommended)**

```bash
export NAVER_ACCESS_TOKEN="your_access_token_here"
```

**Option 2: Function Parameter**

Pass the token directly when calling the function (see usage examples below).

## Usage

### Basic Usage

```python
from src.main import generate_logen_shipping_file

# Using environment variable for access token
file_path = generate_logen_shipping_file()
print(f"Excel file generated: {file_path}")
```

### With Access Token Parameter

```python
from src.main import generate_logen_shipping_file

# Passing access token directly
access_token = "your_access_token_here"
file_path = generate_logen_shipping_file(access_token=access_token)
print(f"Excel file generated: {file_path}")
```

### Error Handling

```python
from src.main import generate_logen_shipping_file
from src.exceptions import NaverAPIError, DataTransformError, ExcelGenerationError

try:
    file_path = generate_logen_shipping_file()
    print(f"Success! File created: {file_path}")
except NaverAPIError as e:
    print(f"API Error: {e}")
except DataTransformError as e:
    print(f"Data Transformation Error: {e}")
except ExcelGenerationError as e:
    print(f"Excel Generation Error: {e}")
```

## Output

The system generates an Excel file with the following format:

**Filename:** `로젠발송양식_YYYYMMDD.xlsx` (where YYYYMMDD is the current date)

**Columns:**
- Column A: 받는사람 (Receiver Name)
- Column B: 주소 (Full Address)
- Column C: 전화번호 (Phone Number)
- Column D: 상품명 (Product Name)
- Column E: 배송메모 (Delivery Memo)

## Testing

### Run All Tests

```bash
pytest
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests with Coverage Report

```bash
# Install pytest-cov if not already installed
pip install pytest-cov

# Run tests with coverage
pytest --cov=src --cov-report=term-missing
```

### Run Tests with Branch Coverage

```bash
pytest --cov=src --cov-branch --cov-report=term
```

### Run Specific Test Files

```bash
# Test API client
pytest tests/test_api_client.py

# Test transformer
pytest tests/test_transformer.py

# Test Excel generator
pytest tests/test_excel_generator.py
```

## Project Structure

```
.
├── src/
│   ├── __init__.py
│   ├── api_client.py          # Naver Commerce API client
│   ├── transformer.py         # Data transformation logic
│   ├── excel_generator.py     # Excel file generation
│   ├── utils.py               # Utility functions
│   ├── models.py              # Data models
│   ├── exceptions.py          # Custom exceptions
│   └── main.py                # Main integration function
├── tests/
│   ├── __init__.py
│   ├── test_api_client.py
│   ├── test_transformer.py
│   ├── test_excel_generator.py
│   ├── test_utils.py
│   └── test_main.py
├── requirements.txt
└── README.md
```

## Components

### API Client (`src/api_client.py`)

Handles communication with Naver Commerce API:
- OAuth2 authentication using access token
- Automatic retry with exponential backoff for transient failures
- Filters orders by payment and shipping status

### Data Transformer (`src/transformer.py`)

Transforms Naver order data to Logen format:
- Maps Naver fields to Logen columns
- Combines base address and detailed address
- Validates required fields
- Handles missing optional fields

### Excel Generator (`src/excel_generator.py`)

Creates Excel files in Logen's format:
- Generates dated filenames
- Creates proper header row
- Formats data according to Logen specifications

## Error Handling

The system includes three custom exception types:

### NaverAPIError

Raised when API requests fail:
- Authentication failures (401)
- Network connectivity issues
- Server errors (5xx)
- Rate limiting (429)

### DataTransformError

Raised when data transformation fails:
- Missing required fields
- Invalid data types
- Malformed data

### ExcelGenerationError

Raised when Excel file creation fails:
- File system permission issues
- Disk space problems
- Invalid file paths

## API Retry Logic

The system implements exponential backoff for transient API failures:
- Maximum 3 retry attempts
- Initial delay: 1 second
- Exponential multiplier: 2x
- Retries on: Network errors, 5xx server errors

## Requirements

For detailed requirements and acceptance criteria, see:
- `.kiro/specs/naver-smartstore-logen-integration/requirements.md`
- `.kiro/specs/naver-smartstore-logen-integration/design.md`

## License

This project is proprietary software for internal use.
