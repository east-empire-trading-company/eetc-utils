from typing import Union, List, Dict, Any, Optional

import pandas as pd
import requests
from requests import Response


class EETCDataClient:
    """
    Client for interacting with the EETC Data Hub API.

    Provides methods to fetch historical price data, fundamentals,
    macroeconomic indicators, and trading order records. All methods
    support returning data as either pandas DataFrames or raw JSON.

    :param api_key: API key for authenticating with EETC Data Hub.
    :raises requests.HTTPError: If API requests fail with non-200
        status codes.

    Example:
        >>> client = EETCDataClient(api_key="your-api-key")
        >>> data = client.get_price_data("AAPL", from_date="2024-01-01")
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://eetc-data-hub-service-nb7ewdzv6q-ue.a.run.app/api"

    def _send_http_request(
        self, url: str, params: Optional[Dict[str, Any]]
    ) -> Response:
        """
        Send an HTTP GET request to the EETC Data Hub API.

        :param url: Full URL endpoint to request.
        :param params: Query parameters to include in the request.
        :return: Response object from the API.
        :raises requests.HTTPError: If the response status code is not
            200.
        """

        if params is None:
            params = {}

        response = requests.get(
            url,
            params=params,
            headers={"EETC-API-Key": self.api_key},
        )

        if response.status_code != 200:
            response.raise_for_status()

        return response

    def get_price_data(
        self,
        symbol: str,
        date: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        as_json: bool = False,
    ) -> Union[pd.DataFrame, List[Dict]]:
        """
        Get historical price data from EETC Data Hub via REST API.

        :param symbol: Ticker symbol of the instrument (e.g., "AAPL").
        :param date: Specific date in format "yyyy-mm-dd".
        :param from_date: Earliest date in format "yyyy-mm-dd".
        :param to_date: Latest date in format "yyyy-mm-dd".
        :param as_json: If True, returns raw JSON list; if False
            (default), returns pandas DataFrame.
        :return: Historical price data as pandas DataFrame (default) or
            list of dicts (if as_json=True).
        :raises requests.HTTPError: If the API request fails.
        """

        url = f"{self.base_url}/price/?symbol={symbol}"
        params = {}

        # add optional query params
        if date:
            params["date"] = date

        if from_date:
            params["from_date"] = from_date

        if to_date:
            params["to_date"] = to_date

        # send the HTTP request to EETC Data Hub
        response = self._send_http_request(url, params)

        # process and return response data
        response_data = response.json()

        if as_json:
            return response_data

        if not response_data:
            return pd.DataFrame()

        df = pd.json_normalize(response_data)
        df = df.sort_values(by=["date"])

        return df

    def get_fundamentals_data(
        self,
        symbol: str,
        frequency: str = "Quarterly",
        name: Optional[str] = None,
        year: Optional[int] = None,
        as_json: bool = False,
    ) -> Union[pd.DataFrame, List[Dict]]:
        """
        Get historical fundamentals data from EETC Data Hub via REST API.

        :param symbol: Ticker symbol of the instrument (e.g., "AAPL").
        :param frequency: Frequency of data - "Yearly" or "Quarterly"
            (default).
        :param name: Optional name of the instrument/company for
            filtering.
        :param year: Optional specific year to filter results.
        :param as_json: If True, returns raw JSON list; if False
            (default), returns pandas DataFrame.
        :return: Historical fundamentals data as pandas DataFrame
            (default) or list of dicts (if as_json=True).
        :raises requests.HTTPError: If the API request fails.
        """

        url = f"{self.base_url}/fundamentals/?symbol={symbol}&frequency={frequency}"
        params = {}

        # add optional query params
        if name:
            params["name"] = name

        if year:
            params["year"] = year

        # send the HTTP request to EETC Data Hub
        response = self._send_http_request(url, params)

        # process and return response data
        response_data = response.json()

        if as_json:
            return response_data

        if not response_data:
            return pd.DataFrame()

        return pd.json_normalize(response_data)

    def get_indicator_data(
        self,
        name: str,
        frequency: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        as_json: bool = False,
    ) -> Union[pd.DataFrame, List[Dict]]:
        """
        Get historical macroeconomic indicator data from EETC Data Hub.

        :param name: Name of the macroeconomic indicator (e.g., "GDP",
            "CPI").
        :param frequency: Optional frequency filter - "Yearly",
            "Quarterly", "Monthly", "Weekly", or "Daily".
        :param from_date: Earliest date in format "yyyy-mm-dd".
        :param to_date: Latest date in format "yyyy-mm-dd".
        :param as_json: If True, returns raw JSON list; if False
            (default), returns pandas DataFrame.
        :return: Historical indicator data as pandas DataFrame (default)
            or list of dicts (if as_json=True).
        :raises requests.HTTPError: If the API request fails.
        """

        url = f"{self.base_url}/indicators/?name={name}"
        params = {}

        # add optional query params
        if frequency:
            params["frequency"] = frequency

        if from_date:
            params["from_date"] = from_date

        if to_date:
            params["to_date"] = to_date

        # send the HTTP request to EETC Data Hub
        response = self._send_http_request(url, params)

        # process and return response data
        response_data = response.json()

        if as_json:
            return response_data

        if not response_data:
            return pd.DataFrame()

        df = pd.json_normalize(response_data)
        df = df.sort_values(by=["date"])

        return df

    def get_indicators(self) -> Dict[str, List[str]]:
        """
        Get list of supported macroeconomic indicators grouped by
        frequency.

        :return: Dictionary mapping frequency types to lists of
            indicator names.
        :raises requests.HTTPError: If the API request fails.
        """

        url = f"{self.base_url}/indicators/names/"

        # send the HTTP request to EETC Data Hub
        response = self._send_http_request(url, {})

        # process and return response data
        response_data = response.json()

        return response_data

    def get_companies(self, index: Optional[str] = None) -> Dict[str, Any]:
        """
        Get list of supported companies from EETC Data Hub.

        :param index: Optional index name to filter companies (e.g.,
            "SP500", "NASDAQ100").
        :return: Dictionary containing company data from the EETC Data
            Hub database.
        :raises requests.HTTPError: If the API request fails.
        """

        url = f"{self.base_url}/companies/"
        params = {}

        # add optional query params
        if index:
            params["index"] = index

        # send the HTTP request to EETC Data Hub
        response = self._send_http_request(url, params)

        # process and return response data
        response_data = response.json()

        return response_data

    def get_orders(
        self,
        order_id: Optional[str] = None,
        asset_type: Optional[str] = None,
        action: Optional[str] = None,
        symbol: Optional[str] = None,
        strike: Optional[float] = None,
        right: Optional[str] = None,
        currency: Optional[str] = None,
        exchange: Optional[str] = None,
        strategy: Optional[str] = None,
        broker: Optional[str] = None,
        position_id: Optional[str] = None,
        as_json: bool = False,
    ) -> Union[pd.DataFrame, List[Dict]]:
        """
        Retrieve order records from the EETC Data Hub via the
        `/orders` API.

        All parameters are optional filters that can be combined to
        narrow down results.

        :param order_id: Unique identifier of the order.
        :param asset_type: Type of asset - "EQUITY", "OPTION",
            "FUTURE", etc.
        :param action: Order action - "BUY" or "SELL".
        :param symbol: Ticker symbol of the instrument (e.g., "AAPL").
        :param strike: Strike price (applicable for options only).
        :param right: Option right - "CALL" or "PUT" (applicable for
            options only).
        :param currency: Currency of the trade (e.g., "USD").
        :param exchange: Exchange where the order was placed (e.g.,
            "NASDAQ").
        :param strategy: Trading strategy name associated with the
            order.
        :param broker: Broker handling the order (e.g., "IBKR").
        :param position_id: Identifier of the related position, if any.
        :param as_json: If True, returns raw JSON list; if False
            (default), returns pandas DataFrame.
        :return: Order data as pandas DataFrame (default) or list of
            dicts (if as_json=True).
        :raises requests.HTTPError: If the API request fails.
        """

        url = f"{self.base_url}/orders/"
        params = {
            "order_id": order_id,
            "asset_type": asset_type,
            "action": action,
            "symbol": symbol,
            "strike": strike,
            "right": right,
            "currency": currency,
            "exchange": exchange,
            "strategy": strategy,
            "broker": broker,
            "position_id": position_id,
        }
        # Remove any None values (so only provided filters are sent)
        params = {k: v for k, v in params.items() if v is not None}

        response = self._send_http_request(url, params)
        data = response.json()

        return data if as_json else pd.json_normalize(data)

    def save_orders(self, orders: List[Dict[str, Any]]) -> None:
        """
        Save one or multiple orders to the EETC Data Hub.

        :param orders: List of order dictionaries. Each order should
            contain:
            - order_id (str): Unique identifier for the order
            - asset_type (str): Type of asset (e.g., "EQUITY",
              "OPTION")
            - action (str): "BUY" or "SELL"
            - symbol (str): Ticker symbol
            - size (int): Number of shares/contracts
            - price (float): Execution price
            - currency (str): Currency code (e.g., "USD")
            - exchange (str): Exchange name
            - strategy (str): Strategy name
            - broker (str): Broker identifier
            - strike (float, optional): Strike price for options
            - right (str, optional): "CALL" or "PUT" for options
            - position_id (str, optional): Related position identifier

        Example:
            >>> client.save_orders([{
            ...     "order_id": "123",
            ...     "asset_type": "OPTION",
            ...     "action": "BUY",
            ...     "symbol": "AAPL",
            ...     "strike": 150.0,
            ...     "right": "CALL",
            ...     "size": 10,
            ...     "price": 120.5,
            ...     "currency": "USD",
            ...     "exchange": "NASDAQ",
            ...     "strategy": "Long Call",
            ...     "broker": "IBKR",
            ...     "position_id": "pos_123"
            ... }])

        :raises requests.HTTPError: If the API request fails
            (non-200/201 status).
        """

        url = f"{self.base_url}/orders/"

        response = requests.post(
            url,
            json=orders,
            headers={
                "Content-Type": "application/json",
                "EETC-API-Key": self.api_key,
            },
        )

        if response.status_code not in [200, 201]:
            response.raise_for_status()
