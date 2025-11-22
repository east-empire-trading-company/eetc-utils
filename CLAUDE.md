# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

eetc-utils is a Python library providing reusable utilities for financial analysis and algorithmic trading. It's published to PyPI as `eetc-utils` and is used across EETC (East Empire Trading Company) projects.

## Development Commands

### Environment Setup
```bash
sudo apt-get install build-essential
make update_and_install_python_requirements
```

### Code Formatting
```bash
make reformat_code  # Uses black to format all Python code
```

### Testing
```bash
python -m pytest tests/
python -m pytest tests/test_financials.py  # Run single test file
```

### Package Publishing

**Important**: Before publishing, update both dependencies in `[build_system]` and the `version` field in `[project]` section of `pyproject.toml`.

```bash
# Build the package
python -m build

# Test on PyPI Test
make publish_package_on_pypi_test

# Publish to production PyPI
make publish_package_on_pypi
```

## Architecture

### Module Structure

The library is organized into four main areas:

1. **Finance Utilities** (`src/eetc_utils/finance.py`)
   - Quantitative finance functions: Kelly Criterion, DCF valuation, volatility forecasting
   - GARCH model integration for volatility analysis
   - OHLC data manipulation utilities

2. **API Clients** (`src/eetc_utils/clients/`)
   - **EETCDataClient** (`eetc_data.py`): HTTP client for EETC Data Hub API
     - Fetches price data, fundamentals, macroeconomic indicators, and order history
     - Requires `EETC_API_KEY` environment variable or explicit API key
     - All methods support returning data as pandas DataFrame (default) or raw JSON
   - **EETCNotificationsClient** (`eetc_notifications.py`): Client for EETC Notifications Manager
     - Sends trade updates and notifications to Telegram channels
     - Requires API key for authentication

3. **Strategy Framework** (`src/eetc_utils/strategy/`)
   - **Live Trading**: `strategy.py` - Base `Strategy` class (ABC) for live trading strategies
   - **Execution Engine**: `engine.py` - Engine for running live/paper trading strategies
   - **Backtesting** (`backtesting/`):
     - `strategy.py`: Simplified `Strategy` base class for historical testing
     - `engine.py`: `BacktestEngine` orchestrates backtesting runs, saves results to `results/` directory
     - `broker_sim.py`: `BrokerSim` simulates order execution with configurable slippage and commission
     - `metrics.py`: Computes performance statistics (Sharpe, max drawdown, etc.)

### Strategy Pattern

**Two distinct Strategy base classes exist:**

- `src/eetc_utils/strategy/strategy.py` - For live trading (ABC with abstract methods)
- `src/eetc_utils/strategy/backtesting/strategy.py` - For backtesting (simplified interface)

Both follow lifecycle pattern: `on_start()` → `on_data()` (per bar/tick) → `on_stop()`

The backtesting strategy receives a `context` dict containing:
- `engine`: Reference to the BacktestEngine
- `symbol`: The instrument being traded
- `place_order`: Lambda function for order placement

## Coding Conventions

Follow these conventions when writing or modifying code to ensure consistency across the codebase.

### Type Hints

- **Always use type hints** for function parameters and return values
- Use `Optional[Type]` for parameters that can be `None`
- Use specific types over generic ones:
  - ✅ `Dict[str, Any]` instead of `dict`
  - ✅ `List[Dict]` instead of `list`
- Boolean parameters must be explicitly typed as `bool`
- For union return types, use `Union[pd.DataFrame, List[Dict]]` to indicate conditional returns

**Example:**
```python
def get_data(
    symbol: str,
    date: Optional[str] = None,
    as_json: bool = False
) -> Union[pd.DataFrame, List[Dict]]:
    ...
```

### Docstrings

- **All classes and public methods must have docstrings**
- **Private methods** (prefixed with `_`) should also have docstrings explaining their purpose
- Use **Sphinx-style** docstrings with `:param:`, `:return:`, and `:raises:` sections
- **Maximum line length: 80 characters** (wrap long lines)
- **Always add a blank line after the closing `"""`** of every docstring
- **Examples in docstrings:**
  - **Classes**: Include examples showing initialization and basic usage
  - **Methods/Functions**: Do NOT include examples - the signature and description should be sufficient
  - This keeps function documentation concise while providing helpful class usage patterns
- Clearly document when return type depends on parameters (e.g., `as_json` flag)

**Class docstring template:**
```python
class MyClient:
    """
    Brief one-line description.

    More detailed description explaining the purpose and main
    functionality of the class. Wrap lines at 80 characters to
    maintain readability.

    :param param_name: Description of parameter. Wrap long
        descriptions at 80 characters with proper indentation.
    :raises ExceptionType: When this exception is raised.

    Example:
        >>> client = MyClient(api_key="key")
        >>> result = client.do_something()
    """

    def __init__(self, param_name: str):
        ...
```

**Method docstring template:**
```python
def method_name(
    self,
    param1: str,
    param2: Optional[int] = None,
    as_json: bool = False
) -> Union[pd.DataFrame, List[Dict]]:
    """
    Brief description of what the method does.

    Longer explanation if needed, including behavior details. Wrap
    at 80 characters for better readability.

    :param param1: Description with examples (e.g., "AAPL").
    :param param2: Optional parameter description.
    :param as_json: If True, returns raw JSON; if False (default),
        returns pandas DataFrame.
    :return: Detailed description. If return type is conditional,
        document both possible return types clearly.
    :raises requests.HTTPError: If the API request fails.
    """

    # Implementation starts here
    ...
```

### Error Handling

- **Always validate and handle errors** from external APIs
- Use `response.raise_for_status()` for HTTP requests
- Document all exceptions in docstrings with `:raises:` section
- Acceptable status codes for POST requests: `[200, 201]`
- Acceptable status codes for GET requests: `[200]`

**Example:**
```python
response = requests.post(url, json=data, headers=headers)

if response.status_code not in [200, 201]:
    response.raise_for_status()

return response.json()
```

### Code Organization

- Extract common patterns into reusable methods
- Keep methods focused on a single responsibility
- Use consistent patterns across similar methods (e.g., all data-fetching methods should follow same structure)

**Example:**
```python
def _send_http_request(self, url: str, params: Optional[Dict[str, Any]]) -> Response:
    """Helper method for sending GET requests."""
    ...

def get_price_data(self, symbol: str) -> pd.DataFrame:
    """Public method that uses the helper."""
    response = self._send_http_request(url, params)
    ...
```

### Imports

- Group imports in standard order:
  1. Standard library (`from typing import ...`)
  2. Third-party packages (`import pandas as pd`)
  3. Local imports (`from src.eetc_utils import ...`)
- Use explicit imports: `from typing import Union, List, Dict, Any, Optional`
- Import types even if only used in annotations

**Example:**
```python
from typing import Union, List, Dict, Any, Optional

import pandas as pd
import requests
from requests import Response
```

### Formatting

- Use `black` for code formatting: `make reformat_code`
- **Code line length**: Maximum 88 characters (black default)
- **Docstring line length**: Maximum 80 characters (wrap manually)
- Use double quotes for strings
- Leave blank line before return statements in functions
- Leave blank line after docstrings in functions

### Comments

- **Comments should start with lowercase letters**
- **Exception**: Keep proper names, acronyms, and technical terms in their standard case
- **Only add comments when the code is not self-explanatory**
  - Add comments for complex logic, non-obvious calculations, or important context
  - Don't comment obvious code where the intent is clear from variable/function names
- This applies to inline comments, block comments, and TODO comments

**When to add comments:**

✅ **Good use of comments** (explaining non-obvious logic):
```python
# Kelly Criterion: f* = μ / σ²
optimal_leverage = annualized_return / annualized_variance

# GARCH needs more data (typically 100+ observations)
min_observations = 100 if use_garch else 30

# set the index to the beginning of the week (Monday)
df.index = df.index - pd.tseries.frequencies.to_offset("6D")

# for SHORT positions, invert the returns
if position_type == "SHORT":
    df["log_return"] = -df["log_return"]
```

❌ **Unnecessary comments** (stating the obvious):
```python
# assign symbol to a variable
symbol = "AAPL"

# check if df is empty
if df.empty:
    raise ValueError("df cannot be empty.")

# convert date column to datetime
df["date"] = pd.to_datetime(df["date"])

# return the result
return result
```

**Comment formatting:**

✅ **Correct formatting:**
```python
# calculate daily log returns
df["log_return"] = np.log(df["close"] / df["close"].shift(1))

# TODO: add support for intraday data
```

❌ **Incorrect formatting:**
```python
# Calculate daily log returns  (starts with uppercase)
# The user specified this parameter  (starts with uppercase)
```

### Return Values

- Methods should return data (not `None`) unless they are pure side-effect operations
- If a method returns data, document the return type accurately
- For methods with conditional returns (e.g., DataFrame vs JSON), document both options clearly

### Testing Conventions

Follow these conventions when writing tests to maintain consistency and quality.

#### General Principles

- **Use pytest** as the testing framework
- **Function-based tests**: Write tests as functions, not classes
- **No docstrings for tests**: Test functions should be self-explanatory based on their signature and code. Do not write docstrings for test functions.
- **Test essential functionality only**: Focus on custom code and core business logic
- **Don't test library code**: Avoid testing third-party libraries or framework behavior
- **Test folder structure**: Mirror the `src/eetc_utils` structure in the `tests/` directory
- **Fixtures location**: All shared fixtures belong in `tests/conftest.py`

#### Test Structure

Every test function must follow this pattern:

1. **AI-generated marker**: Add `# ai-generated` comment above each test function
2. **Three-section structure**: Separate test logic with comments:
   - `# given` - Setup and preparation
   - `# when` - Execute the code under test
   - `# then` - Assertions and verification

**Example:**
```python
# ai-generated
def test_get_price_data_returns_dataframe(mock_client, sample_price_data):
    # given
    client = mock_client
    symbol = "AAPL"

    # when
    result = client.get_price_data(symbol)

    # then
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3
    assert list(result.columns) == ["open", "high", "low", "close"]
    assert result.iloc[0]["close"] == 150.0
    assert result.iloc[1]["close"] == 151.0
    assert result.iloc[2]["close"] == 152.0
```

#### Comprehensive Assertions

When asserting on returned data or mock calls:

- **Don't check only the first item** - verify all relevant items
- **For DataFrames**: Check shape, columns, and multiple rows
- **For JSON/dicts**: Verify structure and multiple entries
- **For mock calls**: Check all expected calls, not just `call_count`

**Examples:**

❌ **Incomplete assertion:**
```python
# then
assert len(result) > 0
assert result[0]["symbol"] == "AAPL"
```

✅ **Comprehensive assertion:**
```python
# then
assert len(result) == 2
assert result[0]["symbol"] == "AAPL"
assert result[0]["price"] == 150.0
assert result[1]["symbol"] == "GOOGL"
assert result[1]["price"] == 2800.0
```

❌ **Incomplete mock verification:**
```python
# then
assert mock_request.called
```

✅ **Comprehensive mock verification:**
```python
# then
assert mock_request.call_count == 2
mock_request.assert_any_call("/api/prices", params={"symbol": "AAPL"})
mock_request.assert_any_call("/api/prices", params={"symbol": "GOOGL"})
```

## Dependencies

The project uses Poetry for dependency management. Core dependencies:
- `pandas`: Data manipulation
- `numpy`: Numerical operations
- `arch`: GARCH models for volatility forecasting
- `black`: Code formatting
- `requests`: HTTP client for data API

Python version: 3.12+

## Important Notes

- Import paths use `src.eetc_utils` prefix (e.g., `from src.eetc_utils.finance import calculate_optimal_leverage_kelly`)
- Test file uses outdated import `from src.utils.finance` - this should be `from src.eetc_utils.finance`
- API key for EETC Data Hub can be set via `EETC_API_KEY` environment variable
- Backtest results are saved to `results/` directory with naming pattern: `{strategy_name}__{symbol}__[trades.json|equity.csv|perf.json]`
