import pytest
from unittest.mock import Mock, patch
import pandas as pd
from requests import HTTPError

from src.eetc_utils.clients.eetc_data import EETCDataClient


# ai-generated
def test_client_initialization(api_key):
    # given
    expected_base_url = "https://eetc-data-hub-service-nb7ewdzv6q-ue.a.run.app/api"

    # when
    client = EETCDataClient(api_key=api_key)

    # then
    assert client.api_key == api_key
    assert client.base_url == expected_base_url


# ai-generated
@patch("src.eetc_utils.clients.eetc_data.requests.get")
def test_send_http_request_success(mock_get, data_client):
    # given
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_get.return_value = mock_response
    url = "https://test.com/api/endpoint"
    params = {"param1": "value1"}

    # when
    response = data_client._send_http_request(url, params)

    # then
    assert response.status_code == 200
    mock_get.assert_called_once_with(
        url,
        params=params,
        headers={"EETC-API-Key": data_client.api_key},
    )


# ai-generated
@patch("src.eetc_utils.clients.eetc_data.requests.get")
def test_send_http_request_error(mock_get, data_client):
    # given
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = HTTPError("404 Client Error")
    mock_get.return_value = mock_response
    url = "https://test.com/api/endpoint"

    # when / then
    with pytest.raises(HTTPError):
        data_client._send_http_request(url, {})


# ai-generated
@patch.object(EETCDataClient, "_send_http_request")
def test_get_price_data_as_dataframe(mock_send, data_client, mock_price_data):
    # given
    mock_response = Mock()
    mock_response.json.return_value = mock_price_data
    mock_send.return_value = mock_response

    # when
    result = data_client.get_price_data("AAPL")

    # then
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert list(result.columns) == [
        "symbol",
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]
    assert result["symbol"].iloc[0] == "AAPL"
    assert result["symbol"].iloc[1] == "AAPL"
    assert result["date"].iloc[0] == "2024-01-01"
    assert result["date"].iloc[1] == "2024-01-02"
    assert result["close"].iloc[0] == 183.0
    assert result["close"].iloc[1] == 186.0


# ai-generated
@patch.object(EETCDataClient, "_send_http_request")
def test_get_price_data_as_json(mock_send, data_client, mock_price_data):
    # given
    mock_response = Mock()
    mock_response.json.return_value = mock_price_data
    mock_send.return_value = mock_response

    # when
    result = data_client.get_price_data("AAPL", as_json=True)

    # then
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["symbol"] == "AAPL"
    assert result[0]["date"] == "2024-01-01"
    assert result[0]["close"] == 183.0
    assert result[1]["symbol"] == "AAPL"
    assert result[1]["date"] == "2024-01-02"
    assert result[1]["close"] == 186.0


# ai-generated
@patch.object(EETCDataClient, "_send_http_request")
def test_get_price_data_with_date_filters(mock_send, data_client):
    # given
    mock_response = Mock()
    mock_response.json.return_value = []
    mock_send.return_value = mock_response
    expected_url = f"{data_client.base_url}/price/?symbol=AAPL"
    expected_params = {
        "date": "2024-01-01",
        "from_date": "2024-01-01",
        "to_date": "2024-12-31",
    }

    # when
    data_client.get_price_data(
        "AAPL",
        date="2024-01-01",
        from_date="2024-01-01",
        to_date="2024-12-31",
    )

    # then
    mock_send.assert_called_once_with(expected_url, expected_params)


# ai-generated
@patch.object(EETCDataClient, "_send_http_request")
def test_get_fundamentals_data_as_dataframe(
    mock_send, data_client, mock_fundamentals_data
):
    # given
    mock_response = Mock()
    mock_response.json.return_value = mock_fundamentals_data
    mock_send.return_value = mock_response

    # when
    result = data_client.get_fundamentals_data("AAPL")

    # then
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert "symbol" in result.columns
    assert "name" in result.columns
    assert "fiscal_year" in result.columns
    assert result["symbol"].iloc[0] == "AAPL"
    assert result["name"].iloc[0] == "Apple Inc."
    assert result["fiscal_year"].iloc[0] == 2023


# ai-generated
@patch.object(EETCDataClient, "_send_http_request")
def test_get_fundamentals_data_as_json(mock_send, data_client, mock_fundamentals_data):
    # given
    mock_response = Mock()
    mock_response.json.return_value = mock_fundamentals_data
    mock_send.return_value = mock_response

    # when
    result = data_client.get_fundamentals_data("AAPL", as_json=True)

    # then
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["symbol"] == "AAPL"
    assert result[0]["name"] == "Apple Inc."
    assert result[0]["fiscal_year"] == 2023
    assert result[0]["revenue"] == 89498000000


# ai-generated
@patch.object(EETCDataClient, "_send_http_request")
def test_get_fundamentals_data_with_filters(mock_send, data_client):
    # given
    mock_response = Mock()
    mock_response.json.return_value = []
    mock_send.return_value = mock_response
    expected_url = f"{data_client.base_url}/fundamentals/?symbol=AAPL&frequency=Yearly"
    expected_params = {"name": "Apple Inc.", "year": 2023}

    # when
    data_client.get_fundamentals_data(
        "AAPL",
        frequency="Yearly",
        name="Apple Inc.",
        year=2023,
    )

    # then
    mock_send.assert_called_once_with(expected_url, expected_params)


# ai-generated
@patch.object(EETCDataClient, "_send_http_request")
def test_get_indicator_data_as_dataframe(mock_send, data_client, mock_indicator_data):
    # given
    mock_response = Mock()
    mock_response.json.return_value = mock_indicator_data
    mock_send.return_value = mock_response

    # when
    result = data_client.get_indicator_data("GDP")

    # then
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert list(result.columns) == ["name", "date", "value", "frequency"]
    assert result["name"].iloc[0] == "GDP"
    assert result["name"].iloc[1] == "GDP"
    assert result["date"].iloc[0] == "2024-01-01"
    assert result["date"].iloc[1] == "2024-04-01"
    assert result["value"].iloc[0] == 27360.935
    assert result["value"].iloc[1] == 27740.085


# ai-generated
@patch.object(EETCDataClient, "_send_http_request")
def test_get_indicator_data_as_json(mock_send, data_client, mock_indicator_data):
    # given
    mock_response = Mock()
    mock_response.json.return_value = mock_indicator_data
    mock_send.return_value = mock_response

    # when
    result = data_client.get_indicator_data("GDP", as_json=True)

    # then
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["name"] == "GDP"
    assert result[0]["date"] == "2024-01-01"
    assert result[0]["value"] == 27360.935
    assert result[1]["name"] == "GDP"
    assert result[1]["date"] == "2024-04-01"
    assert result[1]["value"] == 27740.085


# ai-generated
@patch.object(EETCDataClient, "_send_http_request")
def test_get_indicator_data_with_filters(mock_send, data_client):
    # given
    mock_response = Mock()
    mock_response.json.return_value = []
    mock_send.return_value = mock_response
    expected_url = f"{data_client.base_url}/indicators/?name=GDP"
    expected_params = {
        "frequency": "Quarterly",
        "from_date": "2024-01-01",
        "to_date": "2024-12-31",
    }

    # when
    data_client.get_indicator_data(
        "GDP",
        frequency="Quarterly",
        from_date="2024-01-01",
        to_date="2024-12-31",
    )

    # then
    mock_send.assert_called_once_with(expected_url, expected_params)


# ai-generated
@patch.object(EETCDataClient, "_send_http_request")
def test_get_indicators_returns_dict(mock_send, data_client, mock_indicators_list):
    # given
    mock_response = Mock()
    mock_response.json.return_value = mock_indicators_list
    mock_send.return_value = mock_response

    # when
    result = data_client.get_indicators()

    # then
    assert isinstance(result, dict)
    assert len(result) == 3
    assert "Quarterly" in result
    assert "Monthly" in result
    assert "Daily" in result
    assert "GDP" in result["Quarterly"]
    assert "Unemployment Rate" in result["Quarterly"]
    assert "CPI" in result["Monthly"]
    assert "VIX" in result["Daily"]


# ai-generated
@patch.object(EETCDataClient, "_send_http_request")
def test_get_companies_returns_dict(mock_send, data_client, mock_companies_data):
    # given
    mock_response = Mock()
    mock_response.json.return_value = mock_companies_data
    mock_send.return_value = mock_response

    # when
    result = data_client.get_companies()

    # then
    assert isinstance(result, dict)
    assert "companies" in result
    assert len(result["companies"]) == 2
    assert result["companies"][0]["symbol"] == "AAPL"
    assert result["companies"][0]["name"] == "Apple Inc."
    assert result["companies"][1]["symbol"] == "MSFT"
    assert result["companies"][1]["name"] == "Microsoft Corporation"


# ai-generated
@patch.object(EETCDataClient, "_send_http_request")
def test_get_companies_with_index_filter(mock_send, data_client):
    # given
    mock_response = Mock()
    mock_response.json.return_value = {}
    mock_send.return_value = mock_response
    expected_url = f"{data_client.base_url}/companies/"
    expected_params = {"index": "SP500"}

    # when
    data_client.get_companies(index="SP500")

    # then
    mock_send.assert_called_once_with(expected_url, expected_params)


# ai-generated
@patch.object(EETCDataClient, "_send_http_request")
def test_get_orders_as_dataframe(mock_send, data_client, mock_orders_data):
    # given
    mock_response = Mock()
    mock_response.json.return_value = mock_orders_data
    mock_send.return_value = mock_response

    # when
    result = data_client.get_orders()

    # then
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert "order_id" in result.columns
    assert "asset_type" in result.columns
    assert "symbol" in result.columns
    assert result["order_id"].iloc[0] == "order_123"
    assert result["asset_type"].iloc[0] == "EQUITY"
    assert result["symbol"].iloc[0] == "AAPL"


# ai-generated
@patch.object(EETCDataClient, "_send_http_request")
def test_get_orders_as_json(mock_send, data_client, mock_orders_data):
    # given
    mock_response = Mock()
    mock_response.json.return_value = mock_orders_data
    mock_send.return_value = mock_response

    # when
    result = data_client.get_orders(as_json=True)

    # then
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["order_id"] == "order_123"
    assert result[0]["asset_type"] == "EQUITY"
    assert result[0]["action"] == "BUY"
    assert result[0]["symbol"] == "AAPL"
    assert result[0]["size"] == 100
    assert result[0]["price"] == 150.0


# ai-generated
@patch.object(EETCDataClient, "_send_http_request")
def test_get_orders_with_all_filters(mock_send, data_client):
    # given
    mock_response = Mock()
    mock_response.json.return_value = []
    mock_send.return_value = mock_response
    expected_params = {
        "order_id": "order_123",
        "asset_type": "OPTION",
        "action": "BUY",
        "symbol": "AAPL",
        "strike": 150.0,
        "right": "CALL",
        "currency": "USD",
        "exchange": "NASDAQ",
        "strategy": "test_strategy",
        "broker": "IBKR",
        "position_id": "pos_123",
    }

    # when
    data_client.get_orders(
        order_id="order_123",
        asset_type="OPTION",
        action="BUY",
        symbol="AAPL",
        strike=150.0,
        right="CALL",
        currency="USD",
        exchange="NASDAQ",
        strategy="test_strategy",
        broker="IBKR",
        position_id="pos_123",
    )

    # then
    call_args = mock_send.call_args
    assert call_args[0][1] == expected_params


# ai-generated
@patch("src.eetc_utils.clients.eetc_data.requests.post")
def test_save_orders_success(mock_post, data_client):
    # given
    mock_response = Mock()
    mock_response.status_code = 201
    mock_post.return_value = mock_response
    orders = [
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

    # when
    result = data_client.save_orders(orders)

    # then
    assert result is None
    mock_post.assert_called_once_with(
        f"{data_client.base_url}/orders/",
        json=orders,
        headers={
            "Content-Type": "application/json",
            "EETC-API-Key": data_client.api_key,
        },
    )


# ai-generated
@patch("src.eetc_utils.clients.eetc_data.requests.post")
def test_save_orders_error(mock_post, data_client):
    # given
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = HTTPError("400 Client Error")
    mock_post.return_value = mock_response
    orders = [{"order_id": "order_123"}]

    # when / then
    with pytest.raises(HTTPError):
        data_client.save_orders(orders)


# ai-generated
@patch.object(EETCDataClient, "_send_http_request")
def test_get_roguetrader_signals_as_dataframe(
    mock_send, data_client, mock_roguetrader_signals_data
):
    # given
    mock_response = Mock()
    mock_response.json.return_value = mock_roguetrader_signals_data
    mock_send.return_value = mock_response

    # when
    result = data_client.get_roguetrader_signals()

    # then
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert "date" in result.columns
    assert "symbol" in result.columns
    assert "previous_close" in result.columns
    assert result["date"].iloc[0] == "2024-01-15"
    assert result["symbol"].iloc[0] == "SPY"
    assert result["previous_close"].iloc[0] == 450.25


# ai-generated
@patch.object(EETCDataClient, "_send_http_request")
def test_get_roguetrader_signals_as_json(
    mock_send, data_client, mock_roguetrader_signals_data
):
    # given
    mock_response = Mock()
    mock_response.json.return_value = mock_roguetrader_signals_data
    mock_send.return_value = mock_response

    # when
    result = data_client.get_roguetrader_signals(as_json=True)

    # then
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["date"] == "2024-01-15"
    assert result[0]["symbol"] == "SPY"
    assert result[0]["previous_close"] == 450.25
    assert result[0]["open_price"] == 451.00
    assert result[0]["atm_strike"] == 450
    assert result[0]["gex_regime"] == "positive"


# ai-generated
@patch.object(EETCDataClient, "_send_http_request")
def test_get_roguetrader_signals_with_all_filters(mock_send, data_client):
    # given
    mock_response = Mock()
    mock_response.json.return_value = []
    mock_send.return_value = mock_response
    expected_params = {
        "date": "2024-01-15",
        "symbol": "SPY",
    }

    # when
    data_client.get_roguetrader_signals(
        date="2024-01-15",
        symbol="SPY",
    )

    # then
    call_args = mock_send.call_args
    assert call_args[0][1] == expected_params


# ai-generated
@patch("src.eetc_utils.clients.eetc_data.requests.post")
def test_save_roguetrader_signals_success(mock_post, data_client):
    # given
    mock_response = Mock()
    mock_response.status_code = 201
    mock_post.return_value = mock_response
    signals = [
        {
            "date": "2024-01-15",
            "symbol": "SPY",
            "previous_close": 450.25,
            "open_price": 451.00,
            "open_gap": 0.17,
            "atm_strike": 450,
            "atm_iv": 0.15,
            "implied_daily_move_pct": 1.2,
            "atm_greeks": {"delta": 0.5, "gamma": 0.02},
            "vix_previous_close": 14.5,
            "vix_at_calculation": 15.2,
            "vix_change_pct": 4.83,
            "signals": [{"signal": 13.12}],
            "aggregate_gex": 1250000.0,
            "zero_gamma_level": 448.5,
            "gex_regime": "positive",
            "trading_allowed": True,
            "halt_reason": None,
        }
    ]

    # when
    result = data_client.save_roguetrader_signals(signals)

    # then
    assert result is None
    mock_post.assert_called_once_with(
        f"{data_client.base_url}/roguetrader-signals/",
        json=signals,
        headers={
            "Content-Type": "application/json",
            "EETC-API-Key": data_client.api_key,
        },
    )


# ai-generated
@patch("src.eetc_utils.clients.eetc_data.requests.post")
def test_save_roguetrader_signals_error(mock_post, data_client):
    # given
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = HTTPError("400 Client Error")
    mock_post.return_value = mock_response
    signals = [{"date": "2024-01-15"}]

    # when / then
    with pytest.raises(HTTPError):
        data_client.save_roguetrader_signals(signals)


# ai-generated
@patch("src.eetc_utils.clients.eetc_data.requests.post")
def test_save_realtime_bars_success(mock_post, data_client):
    # given two bars with a missing interval between them
    mock_response = Mock()
    mock_response.status_code = 201
    mock_post.return_value = mock_response
    bars = [
        {
            "symbol": "SPY",
            "time": 1790947800,
            "open": 773.41,
            "high": 773.48,
            "low": 773.39,
            "close": 773.45,
            "volume": 1284.0,
            "wap": 773.4312,
            "count": 37,
        },
        {
            "symbol": "SPY",
            "time": 1790947815,
            "open": 773.46,
            "high": 773.52,
            "low": 773.44,
            "close": 773.5,
            "volume": 962.0,
            "wap": 773.4871,
            "count": 29,
        },
    ]

    # when
    result = data_client.save_realtime_bars(bars)

    # then the bars are posted exactly as given
    assert result is None
    mock_post.assert_called_once_with(
        f"{data_client.base_url}/realtime-bars/",
        json=bars,
        headers={
            "Content-Type": "application/json",
            "EETC-API-Key": data_client.api_key,
        },
    )
    mock_response.raise_for_status.assert_not_called()


# ai-generated
@patch("src.eetc_utils.clients.eetc_data.requests.post")
def test_save_realtime_bars_error(mock_post, data_client):
    # given
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = HTTPError("400 Client Error")
    mock_post.return_value = mock_response
    bars = [{"symbol": "SPY", "time": 1790947800}]

    # when
    with pytest.raises(HTTPError) as error:
        data_client.save_realtime_bars(bars)

    # then
    assert str(error.value) == "400 Client Error"
    mock_post.assert_called_once_with(
        f"{data_client.base_url}/realtime-bars/",
        json=bars,
        headers={
            "Content-Type": "application/json",
            "EETC-API-Key": data_client.api_key,
        },
    )
    mock_response.raise_for_status.assert_called_once_with()


# ai-generated
@patch("src.eetc_utils.clients.eetc_data.requests.post")
def test_save_touch_events_success(mock_post, data_client):
    # given a traded touch with one forward sample and a blocked one
    mock_response = Mock()
    mock_response.status_code = 201
    mock_post.return_value = mock_response
    events = [
        {
            "touch_id": "5f0c8a1e7d9b4c3a9e2f1b6d8a7c4e10",
            "version": 2,
            "session_date": "2026-10-02",
            "symbol": "SPY",
            "signal": "s1r",
            "signal_level": 775.12,
            "event": "TOUCH",
            "outcome": "TRADED",
            "position_id": "1790950500",
            "touched_at": "2026-10-02T14:15:00.250000+00:00",
            "underlying_mid": 775.125,
            "forward_path": [
                {
                    "horizon": "1m",
                    "offset_seconds": 60.031,
                    "underlying": 774.985,
                    "option_bid": 1.48,
                },
            ],
        },
        {
            "touch_id": "0a1b2c3d4e5f60718293a4b5c6d7e8f9",
            "version": 1,
            "session_date": "2026-10-02",
            "symbol": "SPY",
            "signal": "s3r",
            "signal_level": 778.77,
            "event": "TOUCH",
            "outcome": "BLOCKED_HIERARCHY",
            "position_id": None,
            "touched_at": "2026-10-02T15:02:11+00:00",
            "underlying_mid": None,
            "forward_path": [],
        },
    ]

    # when
    result = data_client.save_touch_events(events)

    # then the events are posted exactly as given
    assert result is None
    mock_post.assert_called_once_with(
        f"{data_client.base_url}/touch-events/",
        json=events,
        headers={
            "Content-Type": "application/json",
            "EETC-API-Key": data_client.api_key,
        },
    )
    mock_response.raise_for_status.assert_not_called()


# ai-generated
@patch("src.eetc_utils.clients.eetc_data.requests.post")
def test_save_touch_events_error(mock_post, data_client):
    # given
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = HTTPError("400 Client Error")
    mock_post.return_value = mock_response
    events = [{"touch_id": "0a1b2c3d4e5f60718293a4b5c6d7e8f9", "version": 1}]

    # when
    with pytest.raises(HTTPError) as error:
        data_client.save_touch_events(events)

    # then
    assert str(error.value) == "400 Client Error"
    mock_post.assert_called_once_with(
        f"{data_client.base_url}/touch-events/",
        json=events,
        headers={
            "Content-Type": "application/json",
            "EETC-API-Key": data_client.api_key,
        },
    )
    mock_response.raise_for_status.assert_called_once_with()


# ai-generated
@patch("src.eetc_utils.clients.eetc_data.requests.post")
def test_save_gex_snapshots_success(mock_post, data_client):
    # given two snapshots a minute apart, one with two zero-gamma crossings
    mock_response = Mock()
    mock_response.status_code = 201
    mock_post.return_value = mock_response
    snapshots = [
        {
            "session_date": "2026-10-05",
            "symbol": "SPY",
            "time": "2026-10-05T13:31:00.120000+00:00",
            "underlying": 773.125,
            "aggregate_gex": 1250000000.5,
            "gex_regime": "POSITIVE",
            "zero_gamma_level": 771,
            "zero_gamma_crossings": [771],
            "high_gamma_strike": 774,
            "gamma_weighted_strike": 773.42,
            "profile": [
                {"strike": 770, "call_gex": 900, "put_gex": -1400, "net_gamma": -500},
                {"strike": 771, "call_gex": 1800, "put_gex": -600, "net_gamma": 1200},
            ],
        },
        {
            "session_date": "2026-10-05",
            "symbol": "SPY",
            "time": "2026-10-05T13:32:00.090000+00:00",
            "underlying": None,
            "aggregate_gex": -40000000.0,
            "gex_regime": "NEGATIVE",
            "zero_gamma_level": 770,
            "zero_gamma_crossings": [770, 771],
            "high_gamma_strike": 771,
            "gamma_weighted_strike": 770.5,
            "profile": [],
        },
    ]

    # when
    result = data_client.save_gex_snapshots(snapshots)

    # then the snapshots are posted exactly as given
    assert result is None
    mock_post.assert_called_once_with(
        f"{data_client.base_url}/gex-snapshots/",
        json=snapshots,
        headers={
            "Content-Type": "application/json",
            "EETC-API-Key": data_client.api_key,
        },
    )
    mock_response.raise_for_status.assert_not_called()


# ai-generated
@patch("src.eetc_utils.clients.eetc_data.requests.post")
def test_save_gex_snapshots_error(mock_post, data_client):
    # given
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = HTTPError("400 Client Error")
    mock_post.return_value = mock_response
    snapshots = [{"session_date": "2026-10-05", "symbol": "SPY"}]

    # when
    with pytest.raises(HTTPError) as error:
        data_client.save_gex_snapshots(snapshots)

    # then
    assert str(error.value) == "400 Client Error"
    mock_post.assert_called_once_with(
        f"{data_client.base_url}/gex-snapshots/",
        json=snapshots,
        headers={
            "Content-Type": "application/json",
            "EETC-API-Key": data_client.api_key,
        },
    )
    mock_response.raise_for_status.assert_called_once_with()
