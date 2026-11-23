import io
import json
import logging

import pytest

from src.eetc_utils.logging import (
    JSONFormatter,
    configure_logging,
    extract_trace_id,
)

TRACE_ID = "4bf92f3577b34da6a3ce929d0e0e4736"
OTHER_TRACE_ID = "0af7651916cd43dd8448eb211c80319c"


def _logger(formatter: logging.Formatter) -> tuple[logging.Logger, io.StringIO]:
    """Return a fresh logger writing through formatter, and its output stream."""
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(formatter)
    logger = logging.Logger("test")
    logger.addHandler(handler)
    return logger, stream


def _log(formatter: logging.Formatter, level: int, msg: str, **kwargs) -> str:
    """Log one record through formatter and return the output."""
    logger, stream = _logger(formatter)
    logger.log(level, msg, **kwargs)
    return stream.getvalue()


# ai-generated
def test_json_formatter_writes_severity_and_message():
    # given
    formatter = JSONFormatter()

    # when
    output = _log(formatter, logging.INFO, "Result written.")

    # then
    assert output.count("\n") == 1
    assert json.loads(output) == {"severity": "INFO", "message": "Result written."}


# ai-generated
@pytest.mark.parametrize(
    "level, severity",
    [
        (logging.DEBUG, "DEBUG"),
        (logging.INFO, "INFO"),
        (logging.WARNING, "WARNING"),
        (logging.ERROR, "ERROR"),
        (logging.CRITICAL, "CRITICAL"),
    ],
)
def test_json_formatter_spells_severity_as_cloud_logging_expects(level, severity):
    # given
    formatter = JSONFormatter()

    # when
    entry = json.loads(_log(formatter, level, "Something happened."))

    # then
    assert entry["severity"] == severity


# ai-generated
def test_json_formatter_flattens_extra_fields():
    # given
    formatter = JSONFormatter()
    extra = {"duration_ms": 1712, "http.request.method": "GET", "job.id": "abc"}

    # when
    entry = json.loads(_log(formatter, logging.INFO, "Job done.", extra=extra))

    # then
    assert entry == {
        "severity": "INFO",
        "message": "Job done.",
        "duration_ms": 1712,
        "http.request.method": "GET",
        "job.id": "abc",
    }


# ai-generated
def test_json_formatter_writes_non_serializable_extra_as_string():
    # given
    formatter = JSONFormatter()

    class Symbol:
        def __str__(self):
            return "AAPL"

    # when
    entry = json.loads(
        _log(formatter, logging.INFO, "Fetched.", extra={"symbol": Symbol()})
    )

    # then
    assert entry["symbol"] == "AAPL"


# ai-generated
def test_json_formatter_puts_exception_on_the_same_line():
    # given
    formatter = JSONFormatter()

    # when
    try:
        raise ValueError("bad input")
    except ValueError:
        output = _log(formatter, logging.ERROR, "Job failed.", exc_info=True)

    # then
    assert output.count("\n") == 1
    entry = json.loads(output)
    assert entry["severity"] == "ERROR"
    assert entry["message"] == "Job failed."
    assert entry["exception.type"] == "ValueError"
    assert entry["exception.message"] == "bad input"
    assert entry["exception.stacktrace"].startswith("Traceback")
    assert 'raise ValueError("bad input")' in entry["exception.stacktrace"]
    assert entry["exception.stacktrace"].endswith("ValueError: bad input")


# ai-generated
def test_json_formatter_writes_trace_field_from_extra():
    # given
    formatter = JSONFormatter("my-project")

    # when
    entry = json.loads(
        _log(formatter, logging.INFO, "Handled.", extra={"trace_id": TRACE_ID})
    )

    # then
    assert entry == {
        "severity": "INFO",
        "message": "Handled.",
        "logging.googleapis.com/trace": f"projects/my-project/traces/{TRACE_ID}",
    }


# ai-generated
def test_json_formatter_writes_trace_field_from_logger_adapter():
    # given
    logger, stream = _logger(JSONFormatter("my-project"))
    adapter = logging.LoggerAdapter(logger, {"trace_id": TRACE_ID}, merge_extra=True)

    # when
    adapter.info("Handled.", extra={"http.response.status_code": 200})

    # then
    assert json.loads(stream.getvalue()) == {
        "severity": "INFO",
        "message": "Handled.",
        "http.response.status_code": 200,
        "logging.googleapis.com/trace": f"projects/my-project/traces/{TRACE_ID}",
    }


# ai-generated
def test_json_formatter_writes_trace_field_from_getter():
    # given
    formatter = JSONFormatter("my-project", trace_id_getter=lambda: TRACE_ID)

    # when
    entry = json.loads(_log(formatter, logging.INFO, "Handled."))

    # then
    assert entry["logging.googleapis.com/trace"] == (
        f"projects/my-project/traces/{TRACE_ID}"
    )
    assert "trace_id" not in entry


# ai-generated
def test_json_formatter_prefers_explicit_trace_id_over_getter():
    # given
    formatter = JSONFormatter("my-project", trace_id_getter=lambda: OTHER_TRACE_ID)

    # when
    entry = json.loads(
        _log(formatter, logging.INFO, "Handled.", extra={"trace_id": TRACE_ID})
    )

    # then
    assert entry["logging.googleapis.com/trace"] == (
        f"projects/my-project/traces/{TRACE_ID}"
    )
    assert "trace_id" not in entry


# ai-generated
@pytest.mark.parametrize("trace_id", [None, ""])
def test_json_formatter_leaves_trace_field_out_when_getter_has_none(trace_id):
    # given
    formatter = JSONFormatter("my-project", trace_id_getter=lambda: trace_id)

    # when
    entry = json.loads(_log(formatter, logging.INFO, "Handled."))

    # then
    assert entry == {"severity": "INFO", "message": "Handled."}


# ai-generated
@pytest.mark.parametrize(
    "extra, getter_trace_id, expected",
    [
        pytest.param({"trace_id": TRACE_ID}, OTHER_TRACE_ID, TRACE_ID, id="extra"),
        pytest.param({}, OTHER_TRACE_ID, OTHER_TRACE_ID, id="getter"),
    ],
)
def test_json_formatter_writes_plain_trace_id_without_project(
    extra, getter_trace_id, expected
):
    # given
    formatter = JSONFormatter(trace_id_getter=lambda: getter_trace_id)

    # when
    entry = json.loads(_log(formatter, logging.INFO, "Handled.", extra=extra))

    # then
    assert entry == {"severity": "INFO", "message": "Handled.", "trace_id": expected}


# ai-generated
def test_configure_logging_writes_json_to_stdout_by_default(
    restore_root_logger, monkeypatch, capsys
):
    # given
    monkeypatch.delenv("LOG_FORMAT", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "my-project")

    # when
    configure_logging()
    configure_logging(trace_id_getter=lambda: TRACE_ID)
    logging.getLogger("app").info("Started.", extra={"job.id": "abc"})
    logging.getLogger("app").debug("Hidden.")

    # then
    output = capsys.readouterr().out
    assert json.loads(output) == {
        "severity": "INFO",
        "message": "Started.",
        "job.id": "abc",
        "logging.googleapis.com/trace": f"projects/my-project/traces/{TRACE_ID}",
    }
    assert restore_root_logger.level == logging.INFO
    assert len(restore_root_logger.handlers) == 1


# ai-generated
def test_configure_logging_text_format_is_readable(
    restore_root_logger, monkeypatch, capsys
):
    # given
    monkeypatch.setenv("LOG_FORMAT", "text")

    # when
    configure_logging()
    logging.getLogger("app").warning("Retrying.", extra={"attempt": 2})
    try:
        raise ValueError("bad input")
    except ValueError:
        logging.getLogger("app").exception("Job failed.")

    # then
    lines = capsys.readouterr().out.splitlines()
    assert lines[0].endswith(" WARNING app Retrying. attempt=2")
    assert lines[0][:4].isdigit()  # starts with the timestamp's year
    assert lines[1].endswith(" ERROR app Job failed.")
    assert lines[2] == "Traceback (most recent call last):"
    assert lines[-1] == "ValueError: bad input"


# ai-generated
@pytest.mark.parametrize(
    "log_level, expected",
    [
        ("debug", logging.DEBUG),
        ("info", logging.INFO),
        ("warning", logging.WARNING),
        ("error", logging.ERROR),
    ],
)
def test_configure_logging_reads_level_from_env(
    restore_root_logger, monkeypatch, log_level, expected
):
    # given
    monkeypatch.setenv("LOG_LEVEL", log_level)

    # when
    configure_logging()

    # then
    assert restore_root_logger.level == expected


# ai-generated
def test_configure_logging_rejects_unknown_level(restore_root_logger, monkeypatch):
    # given
    monkeypatch.setenv("LOG_LEVEL", "verbose")

    # when / then
    with pytest.raises(ValueError):
        configure_logging()


# ai-generated
@pytest.mark.parametrize(
    "headers, expected",
    [
        pytest.param(
            {"traceparent": f"00-{TRACE_ID}-00f067aa0ba902b7-01"},
            TRACE_ID,
            id="traceparent",
        ),
        pytest.param(
            {"X-Cloud-Trace-Context": f"{TRACE_ID}/1;o=1"},
            TRACE_ID,
            id="cloud-trace-context",
        ),
        pytest.param(
            {
                "traceparent": f"00-{TRACE_ID}-00f067aa0ba902b7-01",
                "X-Cloud-Trace-Context": f"{OTHER_TRACE_ID}/1;o=1",
            },
            TRACE_ID,
            id="traceparent-wins",
        ),
        pytest.param(
            {
                "traceparent": "00-not-a-trace",
                "X-Cloud-Trace-Context": f"{OTHER_TRACE_ID}/1;o=1",
            },
            OTHER_TRACE_ID,
            id="invalid-traceparent-falls-back",
        ),
        pytest.param(
            {"traceparent": f"00-{TRACE_ID[:-1]}-00f067aa0ba902b7-01"},
            "",
            id="short-trace-id",
        ),
        pytest.param(
            {"traceparent": f"00-{'z' * 32}-00f067aa0ba902b7-01"},
            "",
            id="non-hex-trace-id",
        ),
        pytest.param(
            {"X-Cloud-Trace-Context": f"{TRACE_ID}x/1;o=1"},
            "",
            id="long-cloud-trace-id",
        ),
        pytest.param(
            {"X-Cloud-Trace-Context": TRACE_ID}, "", id="cloud-trace-without-span"
        ),
        pytest.param({}, "", id="no-headers"),
    ],
)
def test_extract_trace_id(headers, expected):
    # given / when
    result = extract_trace_id(headers)

    # then
    assert result == expected
