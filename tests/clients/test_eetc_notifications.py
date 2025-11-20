import pytest
from unittest.mock import Mock, patch
from requests import HTTPError

from src.eetc_utils.clients.eetc_notifications import EETCNotificationsClient


# ai-generated
def test_client_initialization(api_key):
    # given
    expected_base_url = (
        "https://eetc-notifications-manager-148296566920.us-east1.run.app"
    )

    # when
    client = EETCNotificationsClient(api_key=api_key)

    # then
    assert client.api_key == api_key
    assert client.base_url == expected_base_url


# ai-generated
@patch("src.eetc_utils.clients.eetc_notifications.requests.post")
def test_send_trade_update_success(mock_post, notifications_client):
    # given
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success", "message_id": 123}
    mock_post.return_value = mock_response
    message = "Trade executed: BUY 100 AAPL @ $150.25"

    # when
    result = notifications_client.send_trade_update_to_telegram(message)

    # then
    assert result == {"status": "success", "message_id": 123}
    assert result["status"] == "success"
    assert result["message_id"] == 123
    mock_post.assert_called_once_with(
        f"{notifications_client.base_url}/api/v1/telegram/send_trade_update",
        json={"message": message},
        headers={"X-API-Key": notifications_client.api_key},
    )


# ai-generated
@patch("src.eetc_utils.clients.eetc_notifications.requests.post")
def test_send_trade_update_error(mock_post, notifications_client):
    # given
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.raise_for_status.side_effect = HTTPError("401 Unauthorized")
    mock_post.return_value = mock_response
    message = "Trade executed: BUY 100 AAPL @ $150.25"

    # when / then
    with pytest.raises(HTTPError):
        notifications_client.send_trade_update_to_telegram(message)
