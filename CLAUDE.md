# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

eetc-utils is a Python library providing reusable utilities for financial analysis and algorithmic trading. It's published to PyPI as `eetc-utils` and is used across EETC (East Empire Trading Company) projects.

## Development Commands

### Environment Setup
```bash
sudo apt-get install build-essential
make install_python_requirements
```

### Code Formatting
```bash
make reformat_code  # Runs `uv run black .` to format all Python code
```

### Testing
```bash
python -m pytest tests/
python -m pytest tests/test_financials.py  # Run single test file
```

### Package Publishing

**Important**: Before publishing, update the `version` field in the `[project]` section of `pyproject.toml`, and update `[project.dependencies]` / `[dependency-groups]` if dependencies changed. The `[build-system]` table (`uv_build`) should not normally need to change.

```bash
# Build the package
uv build

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
   - **ClaudeClient** (`claude.py`): Simple wrapper around the Anthropic SDK
     - Sends single- and multi-turn text prompts to Claude
     - Requires `ANTHROPIC_API_KEY` environment variable or explicit API key
     - Exposes the underlying `anthropic.Anthropic` client for advanced use

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

Shared EETC conventions come from the `eetc` plugin — apply them:

- Writing or editing Python code: `eetc:python-code-style`
- After writing code, before running tests: `eetc:python-simplify`
- Writing or editing tests: `eetc:python-tests`
- Commits and PRs: `eetc:git-conventions`

Project-specific additions:

- Format with `black` (`make reformat_code`); code line length 88 (black
  default), docstrings 80
- Private methods (prefixed with `_`) get docstrings too
- Keep data-fetching methods on one structure: a private helper sends the HTTP
  request, public methods build params and parse the response:

```python
def _send_http_request(self, url: str, params: Optional[Dict[str, Any]]) -> Response:
    """Helper method for sending GET requests."""
    ...

def get_price_data(self, symbol: str) -> pd.DataFrame:
    """Public method that uses the helper."""
    response = self._send_http_request(url, params)
    ...
```

### Testing

- **pytest**, **function-based tests** (not classes)
- Test folder structure mirrors `src/eetc_utils`
- All shared fixtures belong in `tests/conftest.py`
- Mock the EETC Data Hub, Notifications Manager and Anthropic APIs

## Dependencies

The project uses uv for dependency management, packaging, and
publishing (`pyproject.toml` + `uv.lock`). Core dependencies:
- `pandas`: Data manipulation
- `numpy`: Numerical operations
- `arch`: GARCH models for volatility forecasting
- `black`: Code formatting
- `requests`: HTTP client for data API

Python version: 3.12+

## Important Notes

- Import paths use `src.eetc_utils` prefix (e.g., `from src.eetc_utils.finance import calculate_optimal_leverage_kelly`)
- API key for EETC Data Hub can be set via `EETC_API_KEY` environment variable
- Backtest results are saved to `results/` directory with naming pattern: `{strategy_name}__{symbol}__[trades.json|equity.csv|perf.json]`
