"""Structured logging that Google Cloud Logging parses natively.

Writes one JSON object per line on stdout, following the EETC logging standard
(see docs/logging.md). Projects keep calling the stdlib `logging` module; this
module only provides the setup, plus a helper for reading trace IDs.
"""

import json
import logging
import os
import re
import sys
from collections.abc import Callable, Mapping
from typing import Any

_TRACE_ID_RE = re.compile("[0-9a-fA-F]{32}")

# Every attribute a plain LogRecord has; anything else came from `extra=`.
_STANDARD_ATTRS = frozenset(
    vars(logging.LogRecord("", logging.NOTSET, "", 0, "", None, None))
) | {"message", "asctime"}


def _extra_fields(record: logging.LogRecord) -> dict[str, Any]:
    """Return the fields passed to the log call with `extra=`."""
    return {
        key: value for key, value in vars(record).items() if key not in _STANDARD_ATTRS
    }


class JSONFormatter(logging.Formatter):
    """Formats a record as a JSON line for Google Cloud Logging.

    Each line has `severity` and `message`, the `extra=` fields as flat keys,
    and `exception.*` fields when the record has exception info.

    The trace ID comes from the record's `trace_id` field (passed with
    `extra=` or bound with a `logging.LoggerAdapter`), falling back to
    `trace_id_getter`. When there is one and `project_id` is set, it is
    written as `logging.googleapis.com/trace`, otherwise as `trace_id`.
    """

    def __init__(
        self,
        project_id: str = "",
        trace_id_getter: Callable[[], str | None] | None = None,
    ):
        """Create the formatter.

        Args:
            project_id: Google Cloud project ID for the trace field. Empty
                leaves the trace field out.
            trace_id_getter: Called for records without a `trace_id` field to
                get the current trace ID, or None / "" when there is none.
        """
        super().__init__()
        self.project_id = project_id
        self.trace_id_getter = trace_id_getter

    def format(self, record: logging.LogRecord) -> str:
        """Return the record as one line of JSON."""
        # Python's level names (WARNING, CRITICAL) already match Cloud Logging.
        entry = {"severity": record.levelname, "message": record.getMessage()}
        entry.update(_extra_fields(record))

        trace_id = entry.pop("trace_id", None)
        if not trace_id and self.trace_id_getter:
            trace_id = self.trace_id_getter()
        if trace_id and self.project_id:
            entry["logging.googleapis.com/trace"] = (
                f"projects/{self.project_id}/traces/{trace_id}"
            )
        elif trace_id:
            entry["trace_id"] = trace_id

        if record.exc_info and record.exc_info[0] is not None:
            exc_type, exc, _ = record.exc_info
            entry["exception.type"] = exc_type.__name__
            entry["exception.message"] = str(exc)
            entry["exception.stacktrace"] = self.formatException(record.exc_info)

        return json.dumps(entry, default=str)


class _TextFormatter(logging.Formatter):
    """Formats a record as a readable line for local runs."""

    def __init__(self):
        """Create the formatter with a timestamped format."""
        super().__init__("%(asctime)s %(levelname)s %(name)s %(message)s")

    def format(self, record: logging.LogRecord) -> str:
        """Return the record as text, with `extra=` fields as key=value."""
        fields = "".join(
            f" {key}={value!r}" for key, value in _extra_fields(record).items()
        )
        # Keep the fields on the message line, before any traceback.
        message_line, newline, rest = super().format(record).partition("\n")
        return message_line + fields + newline + rest


def configure_logging(
    trace_id_getter: Callable[[], str | None] | None = None,
) -> None:
    """Install a stdout handler on the root logger, replacing existing ones.

    Reads `LOG_FORMAT` (`json` by default, or `text` for local runs),
    `LOG_LEVEL` (`info` by default) and `GOOGLE_CLOUD_PROJECT` (the project ID
    for the trace field).

    Args:
        trace_id_getter: Called for records without a `trace_id` field to get
            the current trace ID; see `JSONFormatter`. How the ID is stored is
            up to the project.

    Raises:
        ValueError: If `LOG_LEVEL` is not a known level.
    """

    handler = logging.StreamHandler(sys.stdout)
    if os.environ.get("LOG_FORMAT", "json") == "text":
        handler.setFormatter(_TextFormatter())
    else:
        handler.setFormatter(
            JSONFormatter(os.environ.get("GOOGLE_CLOUD_PROJECT", ""), trace_id_getter)
        )

    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "info").upper(),
        handlers=[handler],
        force=True,
    )


def extract_trace_id(headers: Mapping[str, str]) -> str:
    """Return the trace ID from request headers, or "" if there is no valid one.

    Reads `traceparent` (`00-<trace>-<span>-<flags>`) and falls back to
    `X-Cloud-Trace-Context` (`<trace>/<span>;o=1`). Only 32 hex characters are
    accepted.

    Args:
        headers: Any mapping of header names to values, such as a framework's
            request headers or a message's attributes. Lookups use the names
            as written above, so a plain dict must use that casing.
    """

    parts = headers.get("traceparent", "").split("-")
    if len(parts) == 4 and _TRACE_ID_RE.fullmatch(parts[1]):
        return parts[1]

    parts = headers.get("X-Cloud-Trace-Context", "").split("/")
    if len(parts) == 2 and _TRACE_ID_RE.fullmatch(parts[0]):
        return parts[0]

    return ""
