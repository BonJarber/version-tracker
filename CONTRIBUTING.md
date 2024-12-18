# Contributing to Version Tracker

Thank you for your interest in contributing to Version Tracker! This document outlines the process for adding new software products to our version tracking system.

## Adding a New Product

1. **Research Phase**
   - Identify a reliable source for version information:
     - Official API endpoints
     - Release RSS/Atom feeds
     - GitHub releases
     - Official release pages
   - Determine what version data is consistently available
   - Verify update frequency/patterns
   - Document the source and any rate limits or restrictions

2. **Implementation**
   - Create new product JSON file in `data/<category>/<product>.json`
   - Implement version checker in `scripts/checkers/<product>_checker.py`
   - Add appropriate error handling and logging
   - Add tests to `tests/checkers/test_<product>.py`

3. **Required Files**
   ```
   data/<category>/<product>.json         # Initial product data
   scripts/checkers/<product>_checker.py  # Version checker implementation
   tests/checkers/test_<product>.py       # Test suite for the checker
   ```

4. **Data File Structure**
   ```json
   {
     "name": "Product Name",
     "identifier": "product-id",
     "type": "<category>",
     "versions": {
       "stable": {
         "version": null
       }
     },
     "metadata": {
       "last_checked": null,
       "check_method": "api|scrape|feed",
       "check_url": "https://api.example.com/versions"
     }
   }
   ```

5. **Testing Requirements**
   - Version checker must have unit tests
   - Tests must cover:
     - Successful version fetching
     - Error handling (timeouts, bad responses)
     - JSON schema validation
     - Data file reading/writing

6. **Pull Request Process**
   1. Fork the repository
   2. Create a feature branch
   3. Implement your changes
   4. Run tests locally (`python -m pytest`)
   5. Submit PR with description of:
      - What product you're adding
      - How versions are sourced
      - Any special considerations
      - Test coverage

## Development Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/MacOS
   # or
   .venv\Scripts\activate     # Windows
   ```
3. Install dependencies:
   ```bash
   pip install httpx jsonschema pytest pytest-asyncio pytest-cov
   ```

## Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage report
python -m pytest --cov=scripts

# Run specific test file
python -m pytest tests/checkers/test_chrome.py
```

## Code Style
- Follow PEP 8
- Use type hints
- Include docstrings for all functions/classes
- Keep functions focused and single-purpose
- Add appropriate logging