import asyncio
import inspect
import logging
from unittest.mock import AsyncMock, Mock, patch

import pytest
from typesafe_sdk import AsyncTypeSafeClient, SystemOneResponse, TypeSafeClient

from src.eetc_utils.clients import JevClient as ExportedJevClient
from src.eetc_utils.clients import JevClientAsync as ExportedJevClientAsync
from src.eetc_utils.clients.jev import (
    DEFAULT_MODEL,
    Choice,
    JevClient,
    JevClientAsync,
    Noul,
    TypeSafeError,
    jev_cost_usd,
)

STATE = {"headline": "ACME raises full-year guidance 20%"}
QUESTIONS = {
    "fundamental": Noul(instructions="Is `headline` about a fundamental change?"),
    "sector": Choice(
        instructions="Which sector is `headline` about?",
        criteria={"tech": None, "energy": None},
    ),
}
CLIENT_CLASSES = [JevClient, JevClientAsync]
JEV_LOGGER = "src.eetc_utils.clients.jev"


def _patch_system_one(client, **mock_kwargs):
    """
    Patch the SDK call of either client with the right mock type.

    :param client: A JevClient or JevClientAsync.
    :param mock_kwargs: Passed to the mock (``return_value``, ``side_effect``).
    :return: The ``patch.object`` context manager; entering it yields the mock.
    """

    mock_class = AsyncMock if isinstance(client, JevClientAsync) else Mock
    return patch.object(client.client, "system_one", mock_class(**mock_kwargs))


def _judge(client, *args, **kwargs):
    """
    Call ``judge`` on either client and return its response.

    :param client: A JevClient or JevClientAsync.
    :return: What ``judge`` returned, awaited for the async client.
    """

    result = client.judge(*args, **kwargs)
    return asyncio.run(result) if inspect.iscoroutine(result) else result


# ai-generated
@pytest.mark.parametrize(
    ("client_class", "sdk_class"),
    [(JevClient, TypeSafeClient), (JevClientAsync, AsyncTypeSafeClient)],
)
def test_client_initialization(api_key, client_class, sdk_class):
    # given / when
    client = client_class(api_key=api_key)

    # then
    assert client.model == DEFAULT_MODEL == "jev-latest"
    assert isinstance(client.client, sdk_class)


# ai-generated
def test_clients_are_exported_from_the_clients_package():
    # given / when
    # the classes are imported from src.eetc_utils.clients at module level

    # then
    assert ExportedJevClient is JevClient
    assert ExportedJevClientAsync is JevClientAsync


# ai-generated
@pytest.mark.parametrize("client_class", CLIENT_CLASSES)
def test_judge_sends_state_questions_and_default_model(
    api_key, client_class, mock_jev_response
):
    # given
    client = client_class(api_key=api_key)

    # when
    with _patch_system_one(client, return_value=mock_jev_response) as system_one:
        response = _judge(client, STATE, QUESTIONS)

    # then
    assert response is mock_jev_response
    assert response.nouls["fundamental"].noul == 0.82
    assert response.choices["sector"].choice == "tech"
    system_one.assert_called_once_with(STATE, QUESTIONS, model="jev-latest")


# ai-generated
@pytest.mark.parametrize("client_class", CLIENT_CLASSES)
@pytest.mark.parametrize(
    ("call_model", "sent_model"),
    [(None, "jev-1.13.0"), ("jev-1.12.0", "jev-1.12.0")],
)
def test_constructor_and_per_call_model_override_the_default(
    api_key, client_class, call_model, sent_model, mock_jev_response
):
    # given
    client = client_class(api_key=api_key, model="jev-1.13.0")

    # when
    with _patch_system_one(client, return_value=mock_jev_response) as system_one:
        _judge(client, STATE, QUESTIONS, model=call_model)

    # then
    assert client.model == "jev-1.13.0"
    system_one.assert_called_once_with(STATE, QUESTIONS, model=sent_model)


# ai-generated
@pytest.mark.parametrize("client_class", CLIENT_CLASSES)
def test_judge_propagates_sdk_errors_unchanged(api_key, client_class, caplog):
    # given
    client = client_class(api_key=api_key)
    error = TypeSafeError("rate limited")
    caplog.set_level(logging.INFO, logger=JEV_LOGGER)

    # when
    with (
        _patch_system_one(client, side_effect=error) as system_one,
        pytest.raises(TypeSafeError) as raised,
    ):
        _judge(client, STATE, QUESTIONS)

    # then
    assert raised.value is error
    assert caplog.records == []
    system_one.assert_called_once_with(STATE, QUESTIONS, model="jev-latest")


# ai-generated
@pytest.mark.parametrize("client_class", CLIENT_CLASSES)
def test_judge_logs_answering_model_tokens_and_cost_but_not_state(
    api_key, client_class, mock_jev_response, caplog
):
    # given
    client = client_class(api_key=api_key)
    caplog.set_level(logging.INFO, logger=JEV_LOGGER)

    # when
    with _patch_system_one(client, return_value=mock_jev_response):
        _judge(client, STATE, QUESTIONS)

    # then
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == logging.INFO
    assert record.getMessage() == "Jev judgment answered."
    assert getattr(record, "jev.model") == "jev-1.14.0"
    assert getattr(record, "jev.input_tokens") == 1200
    assert getattr(record, "jev.cost_usd") == 0.000051
    assert "ACME" not in str(vars(record))
    assert "fundamental" not in str(vars(record))


# ai-generated
@pytest.mark.parametrize("client_class", CLIENT_CLASSES)
def test_judge_logs_no_cost_when_usage_is_not_reported(api_key, client_class, caplog):
    # given
    client = client_class(api_key=api_key)
    response = SystemOneResponse.model_validate(
        {"model": "jev-1.14.0", "usage": {}, "answers": {}}
    )
    caplog.set_level(logging.INFO, logger=JEV_LOGGER)

    # when
    with _patch_system_one(client, return_value=response):
        _judge(client, STATE, QUESTIONS)

    # then
    assert len(caplog.records) == 1
    assert getattr(caplog.records[0], "jev.model") == "jev-1.14.0"
    assert getattr(caplog.records[0], "jev.input_tokens") is None
    assert getattr(caplog.records[0], "jev.cost_usd") is None


# ai-generated
@pytest.mark.parametrize("client_class", CLIENT_CLASSES)
def test_judge_docstring_documents_what_the_caller_handles(client_class):
    # given
    doc = inspect.getdoc(client_class.judge)

    # when / then
    assert ":return:" in doc
    assert ":raises typesafe_sdk.TypeSafeError:" in doc
    assert "cut-off" in doc
    assert "response.nouls[name].noul" in doc
    assert "response.choices[name].choice" in doc
    assert "response.scores[name].score" in doc
    assert "response.model" in doc
    assert "response.usage.input_tokens" in doc


# ai-generated
@pytest.mark.parametrize(
    ("input_tokens", "expected_usd"),
    [
        (0, 0.0),
        (1, 0.000001),  # 0.042 micros rounds up to a whole micro
        (1000, 0.000042),
        (1001, 0.000043),
        (1200, 0.000051),  # 50.4 micros rounds up
        (32_000, 0.001344),
        (1_000_000, 0.042),
    ],
)
def test_jev_cost_usd_rounds_up_to_the_micro_dollar(input_tokens, expected_usd):
    # given / when
    cost = jev_cost_usd(input_tokens)

    # then
    assert cost == expected_usd
