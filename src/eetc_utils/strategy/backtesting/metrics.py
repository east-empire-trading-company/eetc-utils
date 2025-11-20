import pandas as pd
import numpy as np


def trades_to_pnl_series(trades):
    if not trades:
        return pd.DataFrame()

    df = pd.DataFrame([t.__dict__ for t in trades])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").set_index("timestamp")

    df["signed_qty"] = df.apply(
        lambda r: r["qty"] if r["side"] == "BUY" else -r["qty"], axis=1
    )
    df["cash_delta"] = -df["price"] * df["signed_qty"] - df.get("commission", 0)
    df["position"] = df["signed_qty"].cumsum()
    df["cash"] = df["cash_delta"].cumsum()
    df["last_price"] = df["price"]
    df["nav"] = df["cash"] + df["position"] * df["last_price"]

    return df[["position", "cash", "nav"]]


def compute_perf_stats(nav_series: pd.Series):
    if nav_series is None or nav_series.empty:
        return {}
    returns = nav_series.pct_change().dropna()
    ann_ret = (1 + returns.mean()) ** 252 - 1
    ann_vol = returns.std() * np.sqrt(252)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else float("nan")
    cum = (1 + returns).cumprod()
    peak = cum.cummax()
    drawdown = (cum - peak) / peak
    max_dd = float(drawdown.min()) if not drawdown.empty else 0.0
    return {
        "annual_return": ann_ret,
        "annual_vol": ann_vol,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
    }
