---
name: codebase-overview
description: >
  Architecture, data flows, directory structure, and project-specific
  conventions for eetc-utils. Use when exploring the codebase, planning
  a new feature, onboarding to a module, or trying to understand how the
  system fits together — instead of reading multiple files to discover it.
---

# eetc-utils — Codebase Overview

eetc-utils is a pure Python library (no service, no deployment of its own)
published to PyPI and imported by other EETC projects. It provides stateless
quant-finance and options functions, thin HTTP/SDK clients for EETC's own
services and the Claude API, and a minimal strategy framework that pulls price
data from the EETC Data Hub, replays it through a strategy against a simulated
broker, and writes results to disk.

## Architecture

```
caller (other EETC project / script)
  ├── finance.py, options.py ──────────── pure functions (pandas / numpy / arch)
  ├── clients/
  │     ├── EETCDataClient ─────────────→ EETC Data Hub API (Cloud Run)
  │     ├── EETCNotificationsClient ────→ EETC Notifications Manager (Cloud Run)
  │     └── ClaudeClient ───────────────→ Anthropic API (anthropic SDK)
  └── strategy/
        ├── Engine / BacktestEngine ─→ EETCDataClient.get_price_data
        │       └─→ Strategy.on_start → on_data (per bar) → on_stop
        │       └─→ BrokerSim (fills, mark-to-market) → metrics → results/
        └── strategy.py (live Strategy ABC, run() is user-implemented)
```

### Layers

| Layer | Location | Responsibility |
|-------|----------|----------------|
| Finance | `src/eetc_utils/finance.py` | Kelly leverage/position size, DCF intrinsic value, `beta_to_discount_rate`, GARCH annualized vol, compound interest, daily→weekly OHLC. Pure functions — no I/O |
| Options | `src/eetc_utils/options.py` | Black-Scholes price, `GEX`, `find_strikes_in_range`, option IV → underlying IV, helpers `PDF`/`CND`/`D1`/`D2`. Pure functions — no I/O |
| Clients | `src/eetc_utils/clients/` | One class per external service; HTTP/SDK calls and response parsing only — no business logic |
| Live strategy | `src/eetc_utils/strategy/strategy.py` | `Strategy` ABC: abstract `on_start`, `on_data`, `on_stop`, `run` |
| Engine | `src/eetc_utils/strategy/engine.py` | `Engine` — despite its location, a near-copy of `BacktestEngine` (uses `BrokerSim` and the backtesting `context`); accepts an injected `broker_sim` and reads `EETC_API_KEY` |
| Backtesting | `src/eetc_utils/strategy/backtesting/` | `Strategy` (no-op hooks taking `context`), `BacktestEngine`, `BrokerSim` + `Trade`, `metrics` (`trades_to_pnl_series`, `compute_perf_stats`) |

## Data Flow

**Backtest run** (`BacktestEngine.run(strategy, symbol, start, end)`)

1. `EETCDataClient.get_price_data(symbol, from_date=start, to_date=end)` →
   DataFrame of daily bars.
2. Build `context` = `{"engine", "symbol", "place_order"}`; `place_order(side,
   qty, data=bar, timestamp=ts)` calls `BrokerSim.place_market_order` and
   records the `Trade`.
3. `strategy.on_start(context)`, then for each bar
   `strategy.on_data(bar, bar["date"], context)` followed by
   `BrokerSim.mark_to_market(bar, date)`; then `strategy.on_stop(context)`.
4. Write `{output_dir}/{strategy.name}__{symbol}__trades.json`, `__equity.csv`
   and `__perf.json` (`compute_perf_stats`: annual return, annual vol, Sharpe,
   max drawdown; 252-day annualization). `output_dir` defaults to `results/`.
5. Return `{"trades", "equity", "perf"}`.

**Data Hub reads** (`EETCDataClient.get_*`)

1. Public method builds the URL/params.
2. `_send_http_request` sends a GET with header `EETC-API-Key`, raising
   `HTTPError` on non-200.
3. Return a DataFrame by default, or raw JSON with `as_json=True`.

**Data Hub writes** (`save_orders`, `save_roguetrader_signals`,
`save_realtime_bars`, `save_touch_events`, `save_gex_snapshots`): POST a JSON
list directly with `requests.post` (header `EETC-API-Key`), raising on
anything other than 200/201. `_send_http_request` is GET-only.

## External Dependencies

| Client / Service | Source | Purpose |
|------------------|--------|---------|
| `EETCDataClient` | `src/eetc_utils/clients/eetc_data.py` | EETC Data Hub — price, fundamentals, indicators, companies, orders, RogueTrader signals; saves orders, signals, realtime bars, touch events, GEX snapshots. Auth header `EETC-API-Key` |
| `EETCNotificationsClient` | `src/eetc_utils/clients/eetc_notifications.py` | EETC Notifications Manager — `send_message_to_telegram`, `send_post_on_x`, `send_email`. Auth header `X-API-Key` |
| `ClaudeClient` | `src/eetc_utils/clients/claude.py` | Anthropic API via `anthropic.Anthropic`; `send_message` for single/multi-turn text; underlying SDK exposed as `.client` |
| `arch` | PyPI | GARCH model in `garch_annualized_volatility` |

Base URLs for both EETC services are hard-coded in the client constructors.

## Environment & Configuration

| Variable | Purpose |
|----------|---------|
| `EETC_API_KEY` | EETC Data Hub key. Read only by `strategy/engine.py` `Engine`, where it **overrides** the `eetc_api_key` argument. `EETCDataClient`, `EETCNotificationsClient` and `BacktestEngine` take the key explicitly |
| `ANTHROPIC_API_KEY` | Fallback used by the `anthropic` SDK when `ClaudeClient(api_key=None)` |

The library reads no other configuration. Publishing tokens live in
`.pypirc` (secrets — DO NOT READ), extracted by the Makefile publish targets.

## Deployment

| Component | Detail |
|-----------|--------|
| Build | `uv build` (`uv_build` backend) → `dist/` |
| Registry | PyPI as `eetc-utils`; TestPyPI via the `testpypi` index in `pyproject.toml` |
| Release | Bump `version` in `pyproject.toml`, commit `chore: release X.Y.Z`, then `make publish_package_on_pypi_test` / `make publish_package_on_pypi` — only when the user asks |
| Dependencies | Dependabot updates `uv` deps daily (`.github/dependabot.yml`); no CI workflows |

## Adding a New Data Hub Endpoint

The most common change (recent history: `save_realtime_bars`,
`save_touch_events`, `save_gex_snapshots`).

1. Add a method to `EETCDataClient` in
   `src/eetc_utils/clients/eetc_data.py`, mirroring its siblings: `get_*`
   methods go through `_send_http_request` and support `as_json`; `save_*`
   methods POST a list of dicts and document the expected keys in the
   docstring.
2. Add a mock payload fixture to `tests/conftest.py` if needed, and tests to
   `tests/clients/test_eetc_data.py` patching
   `src.eetc_utils.clients.eetc_data.requests.get` / `.post`.
3. Document the method in `README.md` (Quick Start / Key Functions).
4. Release as a separate `chore: release X.Y.Z` commit bumping the version.

## Testing

General rules: `eetc:python-tests`.

- Layout: `tests/` mirrors `src/eetc_utils` (`tests/test_finance.py`,
  `tests/test_options.py`, `tests/clients/test_*.py`). Function-based pytest
  tests, not classes; `# ai-generated` marker and `# given / # when / # then`
  sections. The strategy framework has no tests yet.
- Fixtures: all shared fixtures live in `tests/conftest.py` — `api_key`,
  `data_client`, `notifications_client`, `claude_client`, mock payloads
  (`mock_price_data`, `mock_fundamentals_data`, `mock_indicator_data`,
  `mock_indicators_list`, `mock_companies_data`, `mock_orders_data`,
  `mock_roguetrader_signals_data`) and OHLC frames (`sample_ohlc_dataframe`,
  `sample_daily_ohlc_for_weekly_conversion`).
- Mock: the EETC Data Hub and Notifications Manager (`unittest.mock.patch` on
  the module's `requests.get` / `requests.post`) and the Anthropic API
  (`patch.object(claude_client.client.messages, "create", ...)`). Never hit a
  real service from tests.
- Run:

```bash
source .venv/bin/activate && python -m pytest tests/
source .venv/bin/activate && python -m pytest tests/test_finance.py
```

## Review Checklist (project-specific)

- Two `Strategy` base classes exist — live (`strategy/strategy.py`, ABC with
  no-arg hooks) and backtesting (`strategy/backtesting/strategy.py`, hooks
  take `context`). Check the right one is used.
- New client methods follow the `_send_http_request` / public-method split and
  raise `requests.HTTPError` on failure instead of returning error payloads.
- No real network calls in tests; new fixtures go in `tests/conftest.py`.
- Imports use the `src.eetc_utils` prefix. Known issue: the strategy engines
  import `src.eetc_utils...` inside the package, which likely breaks for users
  installing from PyPI (README imports `eetc_utils...`) — don't spread it into
  new runtime imports without checking.
- `finance.py` / `options.py` stay pure — no I/O or client calls.
- Version bumps go in a separate `chore: release` commit; README updated for
  any new public function or client method.
