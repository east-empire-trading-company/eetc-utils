import logging
from collections.abc import Mapping

from typesafe_sdk import (
    AsyncTypeSafeClient,
    Choice,
    Content,
    Noul,
    Question,
    Score,
    SystemOneResponse,
    TypeSafeClient,
    TypeSafeError,
)

__all__ = [
    "DEFAULT_MODEL",
    "Choice",
    "JevClient",
    "JevClientAsync",
    "Noul",
    "Score",
    "TypeSafeError",
    "jev_cost_usd",
]

logger = logging.getLogger(__name__)

# new Jev releases land often; pin per call where a threshold depends on one
# model's probabilities
DEFAULT_MODEL = "jev-latest"

# list rate as of 2026-11: $0.042 per million input tokens, i.e. 42
# micro-dollars per thousand; output is free
_INPUT_MICROS_PER_THOUSAND = 42


def jev_cost_usd(input_tokens: int) -> float:
    """
    Price one Jev request at the list rate.

    Rounded up to the whole micro-dollar, so a small request never costs
    zero. Output tokens are free.

    :param input_tokens: Input tokens the request reported.
    :return: The cost in USD.
    """

    # integer ceiling division, so the rate never drifts through float maths
    micros = -(-input_tokens * _INPUT_MICROS_PER_THOUSAND // 1000)
    return micros / 1_000_000


def _log_response(response: SystemOneResponse) -> None:
    """
    Log one answered request: the model that answered, its tokens and cost.

    Never logs the state or the questions. Request timing is already logged
    by the ``typesafe_sdk`` logger.

    :param response: The SDK response.
    """

    input_tokens = response.usage.input_tokens
    logger.info(
        "Jev judgment answered.",
        extra={
            "jev.model": response.model,
            "jev.input_tokens": input_tokens,
            "jev.cost_usd": (
                None if input_tokens is None else jev_cost_usd(input_tokens)
            ),
        },
    )


class JevClient:
    """
    Sync client for TypeSafe Jev judgments (``Noul``, ``Choice``, ``Score``).

    Wraps the SDK's ``TypeSafeClient``, for sync apps. Async apps use
    ``JevClientAsync``, which has the same constructor and ``judge()``. For
    anything ``judge`` doesn't cover (assets, retry policy), use the
    underlying ``client`` attribute directly.

    :param api_key: TypeSafe API key. If not provided, the SDK falls back to
        the ``TYPESAFE_API_KEY`` environment variable, and raises
        ``TypeSafeError`` here if neither is set.
    :param model: Default Jev model used when no ``model`` argument is passed
        to ``judge``.

    Example:
        >>> jev = JevClient(api_key="your-api-key")
        >>> response = jev.judge(
        ...     "Q3 revenue guidance raised 20%",
        ...     {"catalyst": Noul(instructions="Is this an earnings catalyst?")},
        ... )
        >>> response.nouls["catalyst"].noul
        0.93
    """

    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL):
        self.client = TypeSafeClient(api_key=api_key)
        self.model = model

    def judge(
        self,
        state: Content,
        questions: Mapping[str, Question],
        model: str | None = None,
    ) -> SystemOneResponse:
        """
        Ask every question about one state, in a single request.

        The questions run in parallel and cannot see each other's answers.
        The client returns the SDK response unchanged; the caller:

        - reads each answer by the name it gave its question:
          ``response.nouls[name].noul`` (probability of yes, 0-1),
          ``response.choices[name].choice`` (with ``.confidence`` and
          ``.probabilities``), ``response.scores[name].score`` (the
          probability-weighted average of the levels the question defined,
          so not 0-1 unless the levels are; with ``.confidence``,
          ``.legend`` and ``.probabilities``)
        - applies its own cut-offs, which the client never does
        - decides whether a ``TypeSafeError`` stops it or is skipped over;
          the client lets every error through
        - can read ``response.model`` (the version that answered, even when
          ``jev-latest`` was asked for) and ``response.usage.input_tokens``
          (the billed tokens)

        Example:
            >>> response = jev.judge(
            ...     {"answer": text},
            ...     {"fundamental": Noul(
            ...         instructions="Is `answer` about a fundamental change?"
            ...     )},
            ... )
            >>> if response.nouls["fundamental"].noul >= 0.7:  # the cut-off
            ...     ...

        :param state: What the questions are about: text, or a JSON object
            whose fields the questions reference in backticks.
        :param questions: Question objects (``Noul``, ``Choice``, ``Score``)
            keyed by the name their answer comes back under; the name is not
            sent to the model.
        :param model: Jev model for this request. Falls back to the model
            set on the client if not provided.
        :return: The SDK's ``SystemOneResponse``: the answers by name
            (``.nouls``, ``.choices``, ``.scores``), the answering
            ``.model`` and the request's token ``.usage``.
        :raises typesafe_sdk.TypeSafeError: If the request fails after the
            SDK's own retries.
        """

        response = self.client.system_one(state, questions, model=model or self.model)
        _log_response(response)
        return response


class JevClientAsync:
    """
    Async client for TypeSafe Jev judgments (``Noul``, ``Choice``, ``Score``).

    Wraps the SDK's ``AsyncTypeSafeClient``, for async apps. Sync apps use
    ``JevClient``, which has the same constructor and ``judge()``. For
    anything ``judge`` doesn't cover (assets, retry policy), use the
    underlying ``client`` attribute directly.

    :param api_key: TypeSafe API key. If not provided, the SDK falls back to
        the ``TYPESAFE_API_KEY`` environment variable, and raises
        ``TypeSafeError`` here if neither is set.
    :param model: Default Jev model used when no ``model`` argument is passed
        to ``judge``.

    Example:
        >>> jev = JevClientAsync(api_key="your-api-key")
        >>> response = await jev.judge(
        ...     "Q3 revenue guidance raised 20%",
        ...     {"catalyst": Noul(instructions="Is this an earnings catalyst?")},
        ... )
        >>> response.nouls["catalyst"].noul
        0.93
    """

    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL):
        self.client = AsyncTypeSafeClient(api_key=api_key)
        self.model = model

    async def judge(
        self,
        state: Content,
        questions: Mapping[str, Question],
        model: str | None = None,
    ) -> SystemOneResponse:
        """
        Ask every question about one state, in a single request.

        The questions run in parallel and cannot see each other's answers.
        The client returns the SDK response unchanged; the caller:

        - reads each answer by the name it gave its question:
          ``response.nouls[name].noul`` (probability of yes, 0-1),
          ``response.choices[name].choice`` (with ``.confidence`` and
          ``.probabilities``), ``response.scores[name].score`` (the
          probability-weighted average of the levels the question defined,
          so not 0-1 unless the levels are; with ``.confidence``,
          ``.legend`` and ``.probabilities``)
        - applies its own cut-offs, which the client never does
        - decides whether a ``TypeSafeError`` stops it or is skipped over;
          the client lets every error through
        - can read ``response.model`` (the version that answered, even when
          ``jev-latest`` was asked for) and ``response.usage.input_tokens``
          (the billed tokens)

        Example:
            >>> response = await jev.judge(
            ...     {"answer": text},
            ...     {"fundamental": Noul(
            ...         instructions="Is `answer` about a fundamental change?"
            ...     )},
            ... )
            >>> if response.nouls["fundamental"].noul >= 0.7:  # the cut-off
            ...     ...

        :param state: What the questions are about: text, or a JSON object
            whose fields the questions reference in backticks.
        :param questions: Question objects (``Noul``, ``Choice``, ``Score``)
            keyed by the name their answer comes back under; the name is not
            sent to the model.
        :param model: Jev model for this request. Falls back to the model
            set on the client if not provided.
        :return: The SDK's ``SystemOneResponse``: the answers by name
            (``.nouls``, ``.choices``, ``.scores``), the answering
            ``.model`` and the request's token ``.usage``.
        :raises typesafe_sdk.TypeSafeError: If the request fails after the
            SDK's own retries.
        """

        response = await self.client.system_one(
            state, questions, model=model or self.model
        )
        _log_response(response)
        return response
