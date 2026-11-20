from typing import Any

import requests


class EETCNotificationsClient:
    """
    Client for interacting with the EETC Notifications Manager API.

    Provides methods to send notifications to Telegram, X (Twitter) and
    email. Sends are fire-and-forget: the API accepts the request, sends in
    the background and echoes the request body back. A successful call means
    the send was accepted, not delivered; delivery failures are only logged
    by the Notifications Manager, so don't retry on success.

    :param api_key: API key for authenticating with EETC
        Notifications Manager.

    Example:
        >>> client = EETCNotificationsClient(api_key="your-api-key")
        >>> response = client.send_message_to_telegram(
        ...     "<b>Trade executed</b>: BUY 100 AAPL @ $150"
        ... )
        >>> response = client.send_post_on_x(
        ...     "Trade executed: BUY 100 AAPL @ $150"
        ... )
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = (
            "https://eetc-notifications-manager-148296566920.us-east1.run.app"
        )

    def _send_http_request(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Send an HTTP POST request to the EETC Notifications Manager API.

        :param path: Endpoint path, appended to the base URL.
        :param payload: JSON body of the request.
        :return: Response data from the API, the request body echoed back.
        :raises requests.HTTPError: If the response status code is 4xx or 5xx.
        """

        response = requests.post(
            f"{self.base_url}{path}",
            json=payload,
            headers={"X-API-Key": self.api_key},
        )
        response.raise_for_status()

        return response.json()

    def send_message_to_telegram(self, msg: str) -> dict[str, Any]:
        """
        Send a message to the EETC Telegram channel.

        :param msg: The message to send, max 4096 characters. Parsed as
            Telegram HTML (<b>, <i>, <a href>, <code>, ...), so escape
            literal <, > and & as &lt;, &gt; and &amp;.
        :return: Response data from the API, the request body echoed back.
        :raises requests.HTTPError: If the API request fails.
        """

        return self._send_http_request(
            "/api/v1/telegram/send_message", {"message": msg}
        )

    def send_post_on_x(self, msg: str) -> dict[str, Any]:
        """
        Post a message as plain text on the EETC X (Twitter) profile.

        :param msg: The message to post. X silently rejects posts over 280
            characters and duplicates of recent posts.
        :return: Response data from the API, the request body echoed back.
        :raises requests.HTTPError: If the API request fails.
        """

        return self._send_http_request("/api/v1/x/post", {"message": msg})

    def send_email(
        self, subject: str, body_html: str, recipients: list[str]
    ) -> dict[str, Any]:
        """
        Send one HTML email from the EETC sender address.

        :param subject: Email subject.
        :param body_html: Email body as HTML.
        :param recipients: Email addresses, at least one. All go in the To
            field, so every recipient sees the others; call once per
            recipient if that matters.
        :return: Response data from the API, the request body echoed back.
        :raises requests.HTTPError: If the API request fails.
        """

        return self._send_http_request(
            "/api/v1/email/send_email",
            {"subject": subject, "body_html": body_html, "recipients": recipients},
        )
