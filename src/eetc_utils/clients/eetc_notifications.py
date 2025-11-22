from typing import Dict, Any

import requests


class EETCNotificationsClient:
    """
    Client for interacting with the EETC Notifications Manager API.

    Provides methods to send notifications to various channels
    including Telegram.

    :param api_key: API key for authenticating with EETC
        Notifications Manager.

    Example:
        >>> client = EETCNotificationsClient(api_key="your-api-key")
        >>> response = client.send_trade_update_to_telegram(
        ...     "Trade executed: BUY 100 AAPL @ $150"
        ... )
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = (
            "https://eetc-notifications-manager-148296566920.us-east1.run.app"
        )

    def send_trade_update_to_telegram(self, msg: str) -> Dict[str, Any]:
        """
        Send a trade update message to the Telegram channel.

        :param msg: The trade update message to send. Should contain
            relevant trade information such as symbol, action, quantity,
            and price.
        :return: Response data from the API as a dictionary, typically
            containing status information about the message delivery.
        :raises requests.HTTPError: If the API request fails.
        """

        response = requests.post(
            f"{self.base_url}/api/v1/telegram/send_trade_update",
            json={"message": msg},
            headers={"X-API-Key": self.api_key},
        )
        if response.status_code not in [200, 201]:
            response.raise_for_status()

        return response.json()
