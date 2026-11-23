# Logging standard

How EETC Python projects log, using `eetc_utils.logging`. It is the Python
version of the [eetc-notifications-manager standard](https://github.com/east-empire-trading-company/eetc-notifications-manager/blob/master/docs/logging.md).
The goal: every line is structured JSON that Google Cloud Logging understands,
and everything a request causes can be found by its trace ID.

## Format

One JSON object per line on stdout. Cloud Run collects stdout; the app never
calls the Cloud Logging API.

```json
{"severity":"ERROR","message":"Job failed.","job.id":"abc","exception.type":"ValueError","exception.message":"bad input","exception.stacktrace":"Traceback ...","logging.googleapis.com/trace":"projects/east-empire-trading-company/traces/4bf92f3577b34da6a3ce929d0e0e4736"}
```

- `severity` and `message` are on every line. Cloud Logging reads both natively.
- No timestamp, service name, version or environment: Cloud Run adds the
  timestamp, service and revision (or job execution and task).
- Messages are constant sentences (`"Result written."`). Variable data always
  goes in fields, so a message can be searched for exactly.
- Keys are flat strings (`"http.route"`), never nested objects.
- A failure logged with `logger.exception(...)` is one line, with the traceback
  in `exception.stacktrace`.

Locally, `LOG_FORMAT=text` switches to readable lines with timestamps, and
fields as `key=value`.

## Setup

Call `configure_logging()` once at startup (in `main`, the job entry point, or
the app factory). It replaces the root logger's handlers, so it is safe to call
again.

```python
import logging

from eetc_utils.logging import configure_logging

configure_logging()
```

Projects with their own logging setup can use the formatter directly:
`handler.setFormatter(JSONFormatter(project_id, trace_id_getter))`.

## Writing logs

- Call the stdlib `logging` module directly. There is no wrapper: each module
  has `logger = logging.getLogger(__name__)`.
- Libraries (including eetc-utils) never configure logging on import; only the
  application calls `configure_logging()`.
- Pass a constant message and put variable data in `extra`:

  ```python
  logger.info("Result written.", extra={"result.rows": len(rows), "duration_ms": ms})
  ```

- `extra` keys must not clash with `LogRecord` attributes (`name`, `msg`,
  `args`, `message`, ...); the stdlib raises `KeyError` for those.
- Inside `except`, use `logger.exception("...")` so the traceback lands in the
  same line.

## Fields

Names follow the [OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv/).
Project-specific fields use the project's own namespace (`strategy.*`,
`notification.*`, ...).

| Field | Type | Used on |
|---|---|---|
| `severity` | `DEBUG` / `INFO` / `WARNING` / `ERROR` / `CRITICAL` | every line |
| `message` | string, constant | every line |
| `logging.googleapis.com/trace` | `projects/<project>/traces/<32-hex>` | lines with a trace ID, when `GOOGLE_CLOUD_PROJECT` is set |
| `exception.type` | string, exception class name | failures logged with exception info |
| `exception.message` | string | failures |
| `exception.stacktrace` | string | failures logged with exception info |
| `duration_ms` | int | timed work: requests, jobs, external calls |
| `http.request.method` | string | request line |
| `http.route` | string, route template | request line |
| `http.response.status_code` | int | request line |
| `user_agent.original` | string | request line |

## Levels

| Level | Meaning |
|---|---|
| `ERROR` | A human should look: 5xx responses, failed jobs, failed external calls that weren't retried. |
| `WARNING` | Unexpected but handled. |
| `INFO` | Lifecycle (`Job started.` / `Job finished.`), request lines, results. |
| `DEBUG` | Off in production. |

4xx responses are `INFO`: they are the caller's problem, not ours.

## Handle or log, never both

A failure is logged once, where it is handled. Code that raises or re-raises an
exception doesn't also log it; the code that catches it does.

## Privacy

Never log message bodies, email subjects or bodies, recipient addresses, API
keys, tokens, or URLs that contain them. Log counts and IDs only.

## Configuration

| Variable | Default | Values |
|---|---|---|
| `LOG_FORMAT` | `json` | `json`, or `text` for local runs |
| `LOG_LEVEL` | `info` | `debug`, `info`, `warning`, `error` |
| `GOOGLE_CLOUD_PROJECT` | empty | project ID for the trace field; without it the trace ID is written as a plain `trace_id` field |

Production uses the defaults plus `GOOGLE_CLOUD_PROJECT` (not secret).

## Trace IDs

eetc-utils doesn't store or manage trace IDs; how a project gets and keeps them
is up to the project. The formatter takes the trace ID from, in order:

1. The record's `trace_id` field, passed per call or bound with a
   `logging.LoggerAdapter`.
2. The `trace_id_getter` passed to `configure_logging()`, called for every
   record without a `trace_id` field.

When there is one and `GOOGLE_CLOUD_PROJECT` is set, it is written as
`logging.googleapis.com/trace`. Both sources are optional: Cloud Run Jobs and
scripts usually need neither, since Cloud Run already labels their lines with
the execution and task.

`extract_trace_id(headers)` reads the trace ID from `traceparent`
(`00-<trace>-<span>-<flags>`), falling back to `X-Cloud-Trace-Context`
(`<trace>/<span>;o=1`), and accepts only 32 hex characters. It takes any
mapping, so it works with any framework's request headers or a message's
attributes. Cloud Run sends these headers.

Per call:

```python
logger.info("Order saved.", extra={"trace_id": trace_id, "order.id": order_id})
```

Bound once per request (`merge_extra=True` keeps per-call `extra` fields,
which a `LoggerAdapter` otherwise replaces):

```python
log = logging.LoggerAdapter(
    logger, {"trace_id": extract_trace_id(request.headers)}, merge_extra=True
)
log.info("Request handled.", extra={"http.response.status_code": 200})
```

Every line during a request, with a project-owned context variable and a
getter (FastAPI shown; Django or any other framework works the same way):

```python
import contextvars

from eetc_utils.logging import configure_logging, extract_trace_id

trace_id_var = contextvars.ContextVar("trace_id", default="")
configure_logging(trace_id_getter=trace_id_var.get)


@app.middleware("http")
async def set_trace_id(request, call_next):
    token = trace_id_var.set(extract_trace_id(request.headers))
    try:
        return await call_next(request)
    finally:
        trace_id_var.reset(token)
```

In Logs Explorer, click a line's trace, or filter with
`trace="projects/east-empire-trading-company/traces/<id>"`.