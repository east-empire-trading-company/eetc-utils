# CLAUDE.md

eetc-utils: a Python library of reusable utilities for financial analysis and
algorithmic trading — quant finance and options math, API clients (EETC Data
Hub, EETC Notifications Manager, Claude) and a strategy/backtesting framework.
Published to PyPI as `eetc-utils` and used across EETC (East Empire Trading
Company) projects.

## MANDATORY WORKFLOW RULES

YOU MUST follow these rules without exception:

**1. Plan before acting on complex tasks**
For any non-trivial task involving multiple steps, multiple files, or
architectural decisions: YOU MUST enter Plan Mode first. Load the
`codebase-overview` skill to understand the architecture before exploring
files. Form a plan and confirm the approach before writing any code. Do NOT
jump straight to implementation.

**2. YOU MUST load and apply the python-code-style skill before writing any Python code**
Skill: `eetc:python-code-style`

**3. YOU MUST load and apply the python-tests skill before writing, editing, or generating tests**
Skill: `eetc:python-tests`

**4. YOU MUST run /simplify after writing code and before running tests**
After finishing an implementation, invoke the `/simplify` skill to review
the changed code for reuse, quality, and efficiency — and fix any issues
found — before proceeding to run tests.

**5. YOU MUST load and apply the git-conventions skill before creating commits or PRs**
Skill: `eetc:git-conventions`
Small project — work and commit directly on `master`. Only branch or open a
PR when the user explicitly asks.

**6. Format with black; code line length 88, docstrings 80**
Run `make reformat_code` after editing Python code. Private methods (prefixed
with `_`) get docstrings too.

**7. Keep API client methods on one structure**
A private helper sends the HTTP request; public methods build params and
parse the response (see `EETCDataClient._send_http_request`):

```python
def _send_http_request(self, url: str, params: Optional[Dict[str, Any]]) -> Response:
    """Helper method for sending GET requests."""
    ...

def get_price_data(self, symbol: str) -> pd.DataFrame:
    """Public method that uses the helper."""
    response = self._send_http_request(url, params)
    ...
```

**8. Import paths use the `src.eetc_utils` prefix**
In source and tests, e.g.
`from src.eetc_utils.finance import calculate_optimal_leverage_kelly`.

**9. Bump the version before publishing**
Before a release, update `version` in the `[project]` section of
`pyproject.toml`, and `[project.dependencies]` / `[dependency-groups]` if
dependencies changed. The `[build-system]` table (`uv_build`) should not
normally need to change. Never publish to PyPI unless the user asks.

## Key Files

| File | Purpose |
|------|---------|
| `src/eetc_utils/finance.py` | Kelly criterion, DCF valuation, GARCH volatility, OHLC helpers |
| `src/eetc_utils/options.py` | Black-Scholes pricing, GEX, strike ranges, IV conversion |
| `src/eetc_utils/clients/eetc_data.py` | `EETCDataClient` — EETC Data Hub API (get + save endpoints) |
| `src/eetc_utils/clients/eetc_notifications.py` | `EETCNotificationsClient` — Telegram / X / email via Notifications Manager |
| `src/eetc_utils/clients/claude.py` | `ClaudeClient` — thin wrapper around the Anthropic SDK |
| `src/eetc_utils/strategy/` | Strategy base classes, engines, backtesting (`BrokerSim`, metrics) |
| `tests/conftest.py` | All shared fixtures (clients, mock API payloads, OHLC frames) |
| `pyproject.toml` | Package metadata, version, dependencies, uv build/index config |
| `Makefile` | Install, lock upgrade, format and publish targets |
| `.pypirc` | PyPI / TestPyPI API tokens used by the publish targets (secrets — DO NOT READ) |

## Project-Specific Commands

```bash
make install_python_requirements                            # uv sync
make update_python_requirements                             # uv lock --upgrade && uv sync
make reformat_code                                          # uv run black .
source .venv/bin/activate && python -m pytest tests/        # run all tests
source .venv/bin/activate && python -m pytest tests/test_finance.py  # run one test file
uv build                                                    # build sdist + wheel into dist/
make publish_package_on_pypi_test                           # publish to TestPyPI (only when asked)
make publish_package_on_pypi                                # publish to PyPI (only when asked)
```

System setup on Linux: `sudo apt-get install build-essential` before
`make install_python_requirements`.
