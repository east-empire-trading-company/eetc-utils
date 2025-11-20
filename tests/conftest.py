import pytest
import pandas as pd

from src.eetc_utils.clients.eetc_data import EETCDataClient
from src.eetc_utils.clients.eetc_notifications import EETCNotificationsClient


@pytest.fixture
def api_key():
    """
    Fixture providing a test API key.

    :return: Test API key string.
    """

    return "test-api-key-123"


@pytest.fixture
def data_client(api_key):
    """
    Fixture providing an EETCDataClient instance.

    :param api_key: API key from the api_key fixture.
    :return: EETCDataClient instance for testing.
    """

    return EETCDataClient(api_key=api_key)


@pytest.fixture
def notifications_client(api_key):
    """
    Fixture providing an EETCNotificationsClient instance.

    :param api_key: API key from the api_key fixture.
    :return: EETCNotificationsClient instance for testing.
    """

    return EETCNotificationsClient(api_key=api_key)


@pytest.fixture
def mock_price_data():
    """
    Fixture providing sample price data response.

    :return: List of dictionaries representing price data.
    """

    return [
        {
            "symbol": "AAPL",
            "date": "2024-01-01",
            "open": 180.0,
            "high": 185.0,
            "low": 179.0,
            "close": 183.0,
            "volume": 50000000,
        },
        {
            "symbol": "AAPL",
            "date": "2024-01-02",
            "open": 183.0,
            "high": 188.0,
            "low": 182.0,
            "close": 186.0,
            "volume": 52000000,
        },
    ]


@pytest.fixture
def mock_fundamentals_data():
    """
    Fixture providing sample fundamentals data response.

    :return: List of dictionaries representing fundamentals data.
    """

    return [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "fiscal_year": 2023,
            "fiscal_period": "Q4",
            "revenue": 89498000000,
            "net_income": 22956000000,
        }
    ]


@pytest.fixture
def mock_indicator_data():
    """
    Fixture providing sample indicator data response.

    :return: List of dictionaries representing indicator data.
    """

    return [
        {
            "name": "GDP",
            "date": "2024-01-01",
            "value": 27360.935,
            "frequency": "Quarterly",
        },
        {
            "name": "GDP",
            "date": "2024-04-01",
            "value": 27740.085,
            "frequency": "Quarterly",
        },
    ]


@pytest.fixture
def mock_indicators_list():
    """
    Fixture providing sample indicators list response.

    :return: Dictionary mapping frequencies to indicator names.
    """

    return {
        "Quarterly": ["GDP", "Unemployment Rate"],
        "Monthly": ["CPI", "Inflation Rate"],
        "Daily": ["DXY", "VIX"],
    }


@pytest.fixture
def mock_companies_data():
    """
    Fixture providing sample companies data response.

    :return: Dictionary containing company data.
    """

    return {
        "companies": [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "sector": "Technology",
                "industry": "Consumer Electronics",
            },
            {
                "symbol": "MSFT",
                "name": "Microsoft Corporation",
                "sector": "Technology",
                "industry": "Software",
            },
        ]
    }


@pytest.fixture
def mock_orders_data():
    """
    Fixture providing sample orders data response.

    :return: List of dictionaries representing order data.
    """

    return [
        {
            "order_id": "order_123",
            "asset_type": "EQUITY",
            "action": "BUY",
            "symbol": "AAPL",
            "size": 100,
            "price": 150.0,
            "currency": "USD",
            "exchange": "NASDAQ",
            "strategy": "test_strategy",
            "broker": "IBKR",
        }
    ]


@pytest.fixture
def sample_ohlc_dataframe():
    """
    Fixture providing sample OHLC DataFrame for finance calculations.

    :return: DataFrame with OHLC price data.
    """

    data = {
        "date": pd.date_range(start="2024-01-01", periods=30, freq="D").strftime(
            "%Y-%m-%d"
        ),
        "open": [100 + i * 0.5 for i in range(30)],
        "high": [102 + i * 0.5 for i in range(30)],
        "low": [99 + i * 0.5 for i in range(30)],
        "close": [101 + i * 0.5 for i in range(30)],
        "volume": [1000000 + i * 10000 for i in range(30)],
    }

    return pd.DataFrame(data)


@pytest.fixture
def sample_daily_ohlc_for_weekly_conversion():
    """
    Fixture providing daily OHLC data for weekly conversion testing.

    :return: DataFrame with daily OHLC data spanning multiple weeks.
    """

    data = {
        "date": [
            "2024-01-01",
            "2024-01-02",
            "2024-01-03",
            "2024-01-04",
            "2024-01-05",
            "2024-01-08",
            "2024-01-09",
            "2024-01-10",
            "2024-01-11",
            "2024-01-12",
        ],
        "open": [100, 102, 101, 103, 105, 104, 106, 108, 107, 109],
        "high": [103, 104, 103, 106, 108, 107, 109, 111, 110, 112],
        "low": [99, 101, 100, 102, 104, 103, 105, 107, 106, 108],
        "close": [102, 101, 103, 105, 104, 106, 108, 107, 109, 111],
        "volume": [
            1000000,
            1100000,
            1200000,
            1300000,
            1400000,
            1500000,
            1600000,
            1700000,
            1800000,
            1900000,
        ],
    }

    return pd.DataFrame(data)
