# EETC Utils

[![PyPI version](https://badge.fury.io/py/eetc-utils.svg)](https://badge.fury.io/py/eetc-utils)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library providing reusable utilities for financial analysis and algorithmic trading. Built by [East Empire Trading Company](https://github.com/east-empire-trading-company) for quantitative finance and trading strategy development.

## Features

### Finance Utilities
- **Quantitative Finance Functions**: Kelly Criterion, DCF valuation, volatility forecasting
- **GARCH Models**: Advanced volatility analysis using ARCH library integration
- **OHLC Data Manipulation**: Tools for working with time-series price data

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
from src.eetc_utils.finance import (
    optimal_leverage_kelly_criterion,
    dcf_valuation,
    forecast_volatility_garch
)

# Calculate optimal leverage using Kelly Criterion
leverage = optimal_leverage_kelly_criterion(
    win_rate=0.55,
    avg_win=0.02,
    avg_loss=0.01
)

# DCF valuation
intrinsic_value = dcf_valuation(
    free_cash_flows=[100, 110, 121],
    discount_rate=0.10,
    terminal_growth_rate=0.03
)

# Forecast volatility using GARCH
volatility = forecast_volatility_garch(returns_series, horizon=5)
```

### EETC Data Hub Client

```python
from src.eetc_utils.clients.eetc_data import EETCDataClient
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
from src.eetc_utils.clients.eetc_notifications import EETCNotificationsClient
import os

# Initialize client (requires EETC_API_KEY environment variable)
client = EETCNotificationsClient(api_key=os.getenv("EETC_API_KEY"))

# Send trade update via Telegram
client.send_trade_update_to_telegram(msg="Shorted TSLA x100 at 1312.69.")
```


### Backtesting Framework

```python
from src.eetc_utils.strategy.backtesting.strategy import Strategy
from src.eetc_utils.strategy.backtesting.engine import BacktestEngine
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

### Key Classes

#### Finance Module (`finance.py`)
- `optimal_leverage_kelly_criterion()`: Calculate optimal position sizing
- `dcf_valuation()`: Discounted cash flow valuation
- `forecast_volatility_garch()`: GARCH-based volatility forecasting
- Various OHLC data manipulation utilities

#### API Clients
- **EETCDataClient**: HTTP client for fetching market data and fundamentals
- **EETCNotificationsClient**: Send trading notifications via Telegram

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