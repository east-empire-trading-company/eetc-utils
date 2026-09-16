from typing import Any, Dict, List, Optional, Union

import anthropic
from anthropic.types import Message

DEFAULT_MODEL = "claude-sonnet-5"
DEFAULT_MAX_TOKENS = 4096


class ClaudeClient:
    """
    Simple client for sending prompts to the Claude API.

    Wraps the official `anthropic` SDK for single- and multi-turn
    text completions. For advanced use cases not covered by
    `send_message` (streaming, vision, tool use), use the
    underlying `client` attribute directly.

    :param api_key: Anthropic API key. If not provided, the
        underlying SDK falls back to the `ANTHROPIC_API_KEY`
        environment variable.
    :param model: Default model ID used when no `model` argument
        is passed to `send_message`.

    Example:
        >>> client = ClaudeClient(api_key="your-api-key")
        >>> client.send_message("What is the capital of France?")
        'The capital of France is Paris.'
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
    ):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def send_message(
        self,
        prompt: str,
        system: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        model: Optional[str] = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        as_text: bool = True,
    ) -> Union[str, Message]:
        """
        Send a prompt to Claude and return its response.

        Appends `prompt` as the final user turn after any prior
        `messages`, so the same method covers both single-turn
        and multi-turn conversations.

        :param prompt: The user message to send to Claude.
        :param system: Optional system prompt to steer Claude's
            behavior for this request.
        :param messages: Optional prior conversation turns (each
            a dict with "role" and "content" keys) sent as
            context before `prompt`.
        :param model: Model ID for this request. Falls back to
            the model set on the client if not provided.
        :param max_tokens: Maximum number of tokens to generate.
        :param as_text: If True (default), returns the response
            as a string; if False, returns the raw Claude API
            message object.
        :return: Claude's reply as a string (default) or the raw
            anthropic Message object (if as_text=False).
        :raises anthropic.APIError: If the Claude API request
            fails.
        """

        conversation = list(messages) if messages else []
        conversation.append({"role": "user", "content": prompt})

        request_kwargs: Dict[str, Any] = {}
        if system is not None:
            request_kwargs["system"] = system

        response = self.client.messages.create(
            model=model or self.model,
            max_tokens=max_tokens,
            messages=conversation,
            **request_kwargs,
        )

        if as_text:
            return self._extract_text(response)

        return response

    def _extract_text(self, message: Message) -> str:
        """
        Concatenate all text blocks from a Claude response.

        :param message: Claude API response message.
        :return: Concatenated text content from the response.
        """

        return "".join(block.text for block in message.content if block.type == "text")
