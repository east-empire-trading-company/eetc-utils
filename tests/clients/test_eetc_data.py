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
