from unittest.mock import Mock, patch

import anthropic
import pytest

from src.eetc_utils.clients.claude import DEFAULT_MODEL, ClaudeClient


@pytest.fixture
def mock_claude_message():
    return Mock(content=[Mock(type="text", text="The capital of France is Paris.")])


# ai-generated
def test_client_initialization(api_key, claude_client):
    # given / when
    # claude_client is constructed by the fixture

    # then
    assert claude_client.model == DEFAULT_MODEL
    assert claude_client.client.api_key == api_key
    assert isinstance(claude_client.client, anthropic.Anthropic)


# ai-generated
def test_client_initialization_with_custom_model(api_key):
    # given
    custom_model = "claude-opus-5"

    # when
    client = ClaudeClient(api_key=api_key, model=custom_model)

    # then
    assert client.model == custom_model
    assert client.client.api_key == api_key


# ai-generated
def test_send_message_returns_text(claude_client, mock_claude_message):
    # given
    with patch.object(
        claude_client.client.messages, "create", return_value=mock_claude_message
    ) as mock_create:
        # when
        result = claude_client.send_message("What is the capital of France?")

    # then
    assert result == "The capital of France is Paris."
    mock_create.assert_called_once_with(
        model=DEFAULT_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": "What is the capital of France?"}],
    )


# ai-generated
def test_send_message_with_system_prompt(claude_client, mock_claude_message):
    # given
    system_prompt = "You are a helpful geography assistant."

    with patch.object(
        claude_client.client.messages, "create", return_value=mock_claude_message
    ) as mock_create:
        # when
        claude_client.send_message(
            "What is the capital of France?", system=system_prompt
        )

    # then
    mock_create.assert_called_once_with(
        model=DEFAULT_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": "What is the capital of France?"}],
        system=system_prompt,
    )


# ai-generated
def test_send_message_without_system_prompt_omits_kwarg(
    claude_client, mock_claude_message
):
    # given
    with patch.object(
        claude_client.client.messages, "create", return_value=mock_claude_message
    ) as mock_create:
        # when
        claude_client.send_message("Hello")

    # then
    call_kwargs = mock_create.call_args.kwargs
    assert "system" not in call_kwargs


# ai-generated
def test_send_message_with_message_history(claude_client, mock_claude_message):
    # given
    history = [
        {"role": "user", "content": "My name is Alice."},
        {"role": "assistant", "content": "Nice to meet you, Alice."},
    ]
    original_history = list(history)

    with patch.object(
        claude_client.client.messages, "create", return_value=mock_claude_message
    ) as mock_create:
        # when
        claude_client.send_message("What's my name?", messages=history)

    # then
    mock_create.assert_called_once_with(
        model=DEFAULT_MODEL,
        max_tokens=4096,
        messages=[
            {"role": "user", "content": "My name is Alice."},
            {"role": "assistant", "content": "Nice to meet you, Alice."},
            {"role": "user", "content": "What's my name?"},
        ],
    )
    assert history == original_history


# ai-generated
def test_send_message_with_model_override(claude_client, mock_claude_message):
    # given
    with patch.object(
        claude_client.client.messages, "create", return_value=mock_claude_message
    ) as mock_create:
        # when
        claude_client.send_message("Hello", model="claude-opus-5")

    # then
    call_kwargs = mock_create.call_args.kwargs
    assert call_kwargs["model"] == "claude-opus-5"


# ai-generated
def test_send_message_with_custom_max_tokens(claude_client, mock_claude_message):
    # given
    with patch.object(
        claude_client.client.messages, "create", return_value=mock_claude_message
    ) as mock_create:
        # when
        claude_client.send_message("Hello", max_tokens=256)

    # then
    call_kwargs = mock_create.call_args.kwargs
    assert call_kwargs["max_tokens"] == 256


# ai-generated
def test_send_message_as_text_false_returns_raw_message(
    claude_client, mock_claude_message
):
    # given
    with patch.object(
        claude_client.client.messages, "create", return_value=mock_claude_message
    ):
        # when
        result = claude_client.send_message("Hello", as_text=False)

    # then
    assert result is mock_claude_message


# ai-generated
def test_send_message_propagates_api_error(claude_client):
    # given
    error = anthropic.APIConnectionError(request=Mock())

    with patch.object(claude_client.client.messages, "create", side_effect=error):
        # when / then
        with pytest.raises(anthropic.APIConnectionError):
            claude_client.send_message("Hello")
