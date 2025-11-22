# EETC Utils

[![PyPI version](https://badge.fury.io/py/eetc-utils.svg)](https://badge.fury.io/py/eetc-utils)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library providing reusable utilities for financial analysis and algorithmic trading. Built by [East Empire Trading Company](https://github.com/east-empire-trading-company) for quantitative finance and trading strategy development.

## Features

### Finance Utilities
- **Quantitative Finance Functions**: Kelly Criterion position sizing, DCF valuation, compound interest
- **GARCH Models**: Advanced volatility forecasting using ARCH library integration
- **OHLC Data Manipulation**: Convert daily data to weekly timeframes, performance calculations

### Options Trading
- **Black-Scholes Pricing**: Calculate option prices for calls and puts
- **Greeks Calculations**: Gamma exposure (GEX) and other option Greeks
- **Volatility Analysis**: Convert option IV to underlying IV, standard distribution functions
- **Strike Range Tools**: Find strike prices within percentage ranges

### API Clients
- **EETC Data Hub Client**: Fetch price data, fundamentals, macroeconomic indicators, and order history
- **EETC Notifications Client**: Send trade updates and notifications to Telegram channels

### Strategy Framework
- **Live Trading**: Abstract base classes for implementing live/paper trading strategies
- **Execution Engine**: Production-ready engine for running trading strategies
- **Backtesting Framework**: Complete backtesting suite with broker simulation, performance metrics, and result persistence

## Installation

```bash
pip install eetc-utils
```

## Quick Start

### Finance Utilities

```python
from eetc_utils.finance import (
    calculate_optimal_leverage_kelly,
    intrinsic_value_using_dcf,
    garch_annualized_volatility,
    convert_daily_ohlc_data_to_weekly
)
import pandas as pd

# Calculate optimal leverage using Kelly Criterion
price_df = pd.DataFrame({
    'date': pd.date_range('2020-01-01', periods=200),
    'close': [100 + i * 0.5 for i in range(200)]
})

leverage = calculate_optimal_leverage_kelly(
    df=price_df,
    position_type="LONG",
    regime_start_date="2020-01-01",
    fractional_kelly_multiplier=0.5,
    use_garch=False
)

# DCF valuation
intrinsic_value = intrinsic_value_using_dcf(
    cash_flow=1000000000,
    growth_years=10,
    shares=100000000,
    growth_rate=1.15,
    beta=1.2
)

# Forecast volatility using GARCH
volatility = garch_annualized_volatility(price_df)

# Convert daily OHLC to weekly
weekly_df = convert_daily_ohlc_data_to_weekly(price_df)
```

### Options Trading

```python
from eetc_utils.options import (
    calculate_option_price_black_scholes,
    find_strikes_in_range,
    GEX,
    calculate_underlying_iv_from_option_iv
)

# Calculate Black-Scholes option price
call_price = calculate_option_price_black_scholes(
    right="C",
    und_price=100.0,
    strike=105.0,
    rate=0.05,
    tte=0.5,
    implied_vol=0.25,
    pv_dividend=0.0
)

# Find strike prices within a range
strikes = find_strikes_in_range(
    range_length_perc=0.1,
    price=100.0
)

# Calculate Gamma Exposure
gex = GEX(oi=1000, gamma=0.05)

# Convert option IV to underlying IV
underlying_iv = calculate_underlying_iv_from_option_iv(
    option_implied_vol=0.20,
    t=30/365
)
```

### EETC Data Hub Client

```python
from eetc_utils.clients.eetc_data import EETCDataClient
import os

# Initialize client (requires EETC_API_KEY environment variable)
client = EETCDataClient(api_key=os.getenv("EETC_API_KEY"))

# Fetch price data
price_data = client.get_price_data(symbol="AAPL", start_date="2024-01-01")

# Get fundamentals
fundamentals = client.get_fundamentals(symbol="AAPL")

# Fetch macroeconomic indicators
macro_data = client.get_macro_indicators(indicator="GDP", country="US")
```

### EETC Notifications Manager Client

```python
from eetc_utils.clients.eetc_notifications import EETCNotificationsClient
import os

# Initialize client (requires EETC_API_KEY environment variable)
client = EETCNotificationsClient(api_key=os.getenv("EETC_API_KEY"))

# Send trade update via Telegram
client.send_trade_update_to_telegram(msg="Shorted TSLA x100 at 1312.69.")
```


### Backtesting Framework

```python
from eetc_utils.strategy.backtesting.strategy import Strategy
from eetc_utils.strategy.backtesting.engine import BacktestEngine
import pandas as pd

class MyStrategy(Strategy):
    def on_start(self, context):
        self.position = 0

    def on_data(self, bar, context):
        # Simple moving average crossover
        if len(self.data) < 20:
            return

        sma_short = self.data['close'].tail(5).mean()
        sma_long = self.data['close'].tail(20).mean()

        if sma_short > sma_long and self.position == 0:
            context['place_order']('buy', quantity=100)
            self.position = 100
        elif sma_short < sma_long and self.position > 0:
            context['place_order']('sell', quantity=100)
            self.position = 0

    def on_stop(self, context):
        pass

# Load historical data
data = pd.read_csv("AAPL_historical.csv")

# Run backtest
engine = BacktestEngine(
    strategy=MyStrategy(),
    data=data,
    symbol="AAPL",
    initial_capital=100000,
    commission=0.001
)

results = engine.run()
print(f"Total Return: {results['total_return']:.2%}")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {results['max_drawdown']:.2%}")
```

## Documentation

### Module Structure

```
src/eetc_utils/
├── finance.py              # Quantitative finance utilities
├── options.py              # Options pricing and Greeks
├── clients/
│   ├── eetc_data.py       # EETC Data Hub API client
│   └── eetc_notifications.py  # Notifications client
└── strategy/
    ├── strategy.py         # Live trading strategy base class
    ├── engine.py          # Live trading execution engine
    └── backtesting/
        ├── strategy.py    # Backtesting strategy base class
        ├── engine.py      # Backtesting engine
        ├── broker_sim.py  # Broker simulator
        └── metrics.py     # Performance metrics
```

### Key Functions & Classes

#### Finance Module (`finance.py`)
- `calculate_optimal_leverage_kelly()`: Calculate optimal leverage using Kelly Criterion
- `calculate_position_size_kelly()`: Calculate position size based on Kelly Criterion
- `intrinsic_value_using_dcf()`: Discounted cash flow valuation
- `garch_annualized_volatility()`: GARCH-based volatility forecasting
- `convert_daily_ohlc_data_to_weekly()`: Convert daily OHLC data to weekly timeframes
- `performance_over_time()`: Calculate percentage performance between dates
- `compound_interest()`: Calculate compound interest
- `beta_to_discount_rate()`: Map beta to discount rate for DCF

#### Options Module (`options.py`)
- `calculate_option_price_black_scholes()`: Black-Scholes option pricing for calls and puts
- `find_strikes_in_range()`: Find strike prices within a percentage range
- `GEX()`: Calculate Gamma Exposure for option contracts
- `calculate_underlying_iv_from_option_iv()`: Convert option IV to underlying IV
- `PDF()`: Standard normal probability density function
- `CND()`: Cumulative normal distribution
- `D1()`, `D2()`: Black-Scholes d1 and d2 calculations

#### API Clients
- **EETCDataClient**: HTTP client for fetching market data and fundamentals
  - `get_price_data()`: Fetch historical price data
  - `get_fundamentals()`: Get company fundamentals
  - `get_macro_indicators()`: Fetch macroeconomic indicators
  - `get_order_history()`: Retrieve order history
- **EETCNotificationsClient**: Send trading notifications via Telegram
  - `send_trade_update_to_telegram()`: Send trade notifications

#### Strategy Framework
- **Live Trading**: `Strategy` (ABC) for implementing live strategies
- **Backtesting**: Simplified `Strategy` class with `on_start()`, `on_data()`, `on_stop()` lifecycle
- **Engines**: Orchestrate strategy execution (live or backtest)
- **BrokerSim**: Simulate order execution with configurable slippage and commission
- **Metrics**: Calculate Sharpe ratio, max drawdown, and other performance statistics

## Development

### Prerequisites
- Python 3.12+
- Poetry (for dependency management)

### Setup

```bash
# Install system dependencies
sudo apt-get install build-essential

# Install Python dependencies
make update_and_install_python_requirements
```

### Code Formatting

```bash
make reformat_code  # Uses black for consistent code style
```

### Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_financials.py

# Run with coverage
python -m pytest tests/ --cov=src/eetc_utils
```

### Publishing to PyPI

#### Prerequisites

Create a `.pypirc` file in the project root with your PyPI API tokens:

```ini
[distutils]
index-servers =
  pypi
  testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_PYPI_TOKEN_HERE

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-YOUR_PRODUCTION_PYPI_TOKEN_HERE
```

**Note**: The `.pypirc` file is already in `.gitignore` and will not be committed to version control.

To generate API tokens:
- **TestPyPI**: https://test.pypi.org/manage/account/token/
- **Production PyPI**: https://pypi.org/manage/account/token/

#### Publishing Steps

1. Update version in `pyproject.toml`:
   - Increment `version` field in `[tool.poetry]` section
   - Update dependencies in `[tool.poetry.dependencies]` if needed

2. Build the package:
   ```bash
   python -m build
   ```

3. Test on PyPI Test:
   ```bash
   make publish_package_on_pypi_test
   ```

4. Publish to production PyPI:
   ```bash
   make publish_package_on_pypi
   ```

The Makefile commands automatically read credentials from `.pypirc` and configure Poetry before publishing.

## Configuration

### Environment Variables

- `EETC_API_KEY`: API key for EETC Data Hub client (required for data access)

## Contributing

Contributions are welcome! Please ensure:
- Code follows the project's style guide (enforced by `black`)
- All tests pass before submitting PR
- New features include appropriate tests
- Documentation is updated for API changes

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- **East Empire Trading Company** - [eastempiretradingcompany2019@gmail.com](mailto:eastempiretradingcompany2019@gmail.com)
- **Stefan Delic** - [einfach.jung1@gmail.com](mailto:einfach.jung1@gmail.com)
- **Milos Dovedan** - [dovedanmilosh@gmail.com](mailto:dovedanmilosh@gmail.com)

## Links

- **Homepage**: [https://github.com/east-empire-trading-company/eetc-utils](https://github.com/east-empire-trading-company/eetc-utils)
- **PyPI**: [https://pypi.org/project/eetc-utils/](https://pypi.org/project/eetc-utils/)
- **Bug Tracker**: [https://github.com/east-empire-trading-company/eetc-utils/issues](https://github.com/east-empire-trading-company/eetc-utils/issues)

## Support

For questions, issues, or feature requests, please [open an issue](https://github.com/east-empire-trading-company/eetc-utils/issues) on GitHub.