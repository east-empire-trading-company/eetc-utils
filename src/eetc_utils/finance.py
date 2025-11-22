import logging
from typing import Optional

import numpy as np
import pandas as pd
from arch import arch_model


def garch_annualized_volatility(df: pd.DataFrame) -> float:
    """
    Calculate an annualized volatility forecast using the GARCH model.

    Uses GARCH(1,1) to model volatility clustering and forecast
    one-step-ahead variance, then annualizes the result assuming 252
    trading days per year.

    :param df: DataFrame with 'close' column containing price data.
    :return: Annualized volatility forecast as a decimal (e.g., 0.25
        for 25% volatility).
    """

    closes = df["close"]
    returns = 100 * closes.pct_change().dropna()

    model = arch_model(returns)

    res = model.fit()

    # get the variance forecast
    forecast = res.forecast(horizon=1, reindex=False)
    variance_forecast = forecast.variance.iloc[-1][0]

    # compute the annualized volatility forecast
    volatility_forecast = np.sqrt(variance_forecast)
    annualized_volatility_forecast = volatility_forecast * np.sqrt(252) / 100

    return annualized_volatility_forecast


def calculate_optimal_leverage_kelly(
    df: pd.DataFrame,
    position_type: str = "LONG",
    regime_start_date: str = "2020-01-01",
    fractional_kelly_multiplier: Optional[float] = 0.5,
    use_garch: bool = True,
) -> float:
    """
    Calculate optimal leverage for a position using the Kelly Criterion.

    Uses historical data from the specified regime (default: post-2020) up to
    the position start date to calculate expected returns and variance, then
    applies Kelly Criterion: f* = μ / σ²

    :param df: DataFrame with columns 'date', 'close' (minimum).
        Date should be datetime or parseable string.
    :param position_type: Position type, either "LONG" or "SHORT".
        For SHORT positions, returns are inverted. Defaults to "LONG".
    :param regime_start_date: Start date of the historical regime to analyze.
        Defaults to "2020-01-01" (post-COVID regime).
    :param fractional_kelly_multiplier: Multiplier for fractional Kelly
        (e.g., 0.5 for half-Kelly, 0.25 for quarter-Kelly).
        Defaults to 0.5. Use None if you don't want to use fractional Kelly.
    :param use_garch: If True, uses GARCH(1,1) model for volatility
        forecasting instead of historical variance. Defaults to True.
    :return: Optimal leverage ratio as a decimal (e.g., 2.0 for 2x
        leverage). Returns 0.0 if insufficient data or negative Kelly.
    """

    if df.empty:
        raise ValueError("df cannot be empty.")
    if fractional_kelly_multiplier is not None and fractional_kelly_multiplier <= 0:
        raise ValueError(
            "fractional_kelly_multiplier cannot be negative or zero.",
        )
    if position_type not in ["LONG", "SHORT"]:
        raise ValueError(
            f"position_type must be 'LONG' or 'SHORT', got '{position_type}'."
        )

    # make a copy and ensure date column is datetime
    df = df[["date", "close"]].copy()
    df["date"] = pd.to_datetime(df["date"])

    # filter for regime period UP TO latest date (lookback window)
    regime_start = pd.to_datetime(regime_start_date)
    last_date = df["date"].max()
    mask = (df["date"] >= regime_start) & (df["date"] < last_date)
    df = df.loc[mask].sort_values(by="date").reset_index(drop=True)

    # GARCH needs more data (typically 100+ observations)
    min_observations = 100 if use_garch else 30
    if len(df) < min_observations:
        logging.warning(
            f"Only {len(df)} data observations available. "
            f"Need at least {min_observations} observations.",
        )
        return 0.0

    # use daily log returns (more appropriate for Kelly)
    df["log_return"] = np.log(df["close"] / df["close"].shift(1))

    # for SHORT positions, invert the returns
    if position_type == "SHORT":
        df["log_return"] = -df["log_return"]

    # remove NaN values from first row
    df = df.dropna()

    # calculate expected return (mean)
    daily_mean_return = df["log_return"].mean()
    annualized_return = daily_mean_return * 252

    # calculate variance: simple historical or GARCH forecast
    if use_garch:
        # use GARCH function to get annualized volatility
        annualized_volatility = garch_annualized_volatility(df)
        annualized_variance = annualized_volatility ** 2
    else:
        # simple historical variance
        daily_variance = df["log_return"].var()
        annualized_variance = daily_variance * 252
        annualized_volatility = np.sqrt(annualized_variance)

    # Kelly Criterion: f* = μ / σ²
    if annualized_variance == 0 or not np.isfinite(annualized_variance):
        logging.warning(
            "Zero/invalid variance detected. Cannot calculate Kelly.",
        )
        return 0.0

    optimal_leverage = annualized_return / annualized_variance

    # Kelly can be negative if expected return is negative
    if optimal_leverage < 0:
        logging.warning(
            f"Negative Kelly: ({optimal_leverage:.4f}). "
            f"Expected return is negative.",
        )
        return 0.0

    # apply fractional Kelly if requested
    if fractional_kelly_multiplier is not None:
        optimal_leverage *= fractional_kelly_multiplier

    return optimal_leverage


def calculate_position_size_kelly(
    capital: float,
    win_probability: float,
    profit_loss_ratio: float,
) -> float:
    """
    Use the Kelly Criterion to calculate the position size.

    Applies the classic Kelly Criterion formula: f* = p - q/b where
    f* is the fraction of capital to bet, p is win probability, q is
    loss probability, and b is the profit/loss ratio.

    :param capital: Total capital available for betting.
    :param win_probability: Probability of winning (0 to 1, e.g.,
        0.6 for 60% win rate).
    :param profit_loss_ratio: Ratio of average win to average loss
        (e.g., 2.0 means wins are 2x larger than losses).
    :return: Optimal position size in the same units as capital.
    """

    p = win_probability  # win probability
    q = 1 - p  # loss probability
    b = profit_loss_ratio  # profit/loss ratio

    kelly_multiplier = p - (q / b)

    return kelly_multiplier * capital


def compound_interest(amount: float, period: int, interest: float) -> float:
    """
    Calculate compound interest over a specified period.

    Iteratively applies compound interest formula: A = P(1 + r/100)^t
    where A is final amount, P is principal, r is interest rate, and
    t is time periods.

    :param amount: Starting principal amount.
    :param period: Number of compounding periods (e.g., years or
        months).
    :param interest: Interest rate per period as a percentage (e.g.,
        5.0 for 5% interest).
    :return: Final amount after compounding, rounded to 2 decimal
        places.
    """

    for x in range(0, period):
        amount = amount + amount * (interest / 100)

    return round(amount, 2)


def performance_over_time(
    price_data: pd.DataFrame,
    start_date: str,
    end_date: str,
) -> float:
    """
    Calculate the performance of an asset over a time period.

    Computes the percentage change from the first closing price to
    the last closing price in the specified date range.

    :param price_data: DataFrame with DatetimeIndex and 'close'
        column.
    :param start_date: Start date for the calculation period.
    :param end_date: End date for the calculation period.
    :return: Performance as a percentage (e.g., 25.5 for 25.5%
        gain, -10.2 for 10.2% loss).
    """

    df = price_data[start_date:end_date]
    return (df["close"].iloc[-1] / df["close"].iloc[0]) * 100 - 100


def beta_to_discount_rate(beta: Optional[float]) -> float:
    """
    Map a beta value to an appropriate discount rate for DCF analysis.

    Converts stock beta (systematic risk measure) to a discount rate
    using predefined ranges. Higher beta indicates higher risk and
    requires higher discount rate.

    :param beta: Stock beta value (measure of systematic risk
        relative to the market). If None, returns default rate of
        1.09 (9%).
    :return: Discount rate as a multiplier (e.g., 1.05 for 5% rate,
        1.09 for 9% rate).
    """

    discount_rate = 1.09  # default rate

    if beta is None:
        return discount_rate

    if beta < 0.8:
        discount_rate = 1.05  # 5%
    elif 0.8 <= beta < 1:
        discount_rate = 1.06  # 6%
    elif 1 <= beta < 1.1:
        discount_rate = 1.065  # 6.5%
    elif 1.1 <= beta < 1.2:
        discount_rate = 1.07  # 7%
    elif 1.2 <= beta < 1.3:
        discount_rate = 1.075  # 7.5%
    elif 1.3 <= beta < 1.4:
        discount_rate = 1.08  # 8%
    elif 1.4 <= beta < 1.5:
        discount_rate = 1.085  # 8.5%
    else:  # if beta >= 1.5
        discount_rate = 1.09  # 9%

    return discount_rate


def intrinsic_value_using_dcf(
    cash_flow: float,
    growth_years: int,
    shares: int,
    growth_rate: float,
    beta: Optional[float] = None,  # optional
    perpetual_growth_rate: Optional[float] = None,  # optional
) -> float:
    """
    Calculate intrinsic value per share using DCF valuation model.

    Projects future cash flows with specified growth rate for n years,
    applies terminal value calculation with perpetual growth, and
    discounts all cash flows to present value. Discount rate is
    derived from beta (if provided) or defaults to 9%.

    :param cash_flow: Most recent annual cash flow (typically
        operating cash flow or free cash flow).
    :param growth_years: Number of years to project high growth
        (e.g., 5 or 10 years).
    :param shares: Total shares outstanding.
    :param growth_rate: Expected annual growth rate as multiplier
        (e.g., 1.15 for 15% growth).
    :param beta: Stock beta for discount rate calculation. If None,
        uses default 9% discount rate. Defaults to None.
    :param perpetual_growth_rate: Terminal growth rate as multiplier
        (e.g., 1.02 for 2% GDP growth). If None, uses 1.02 (2%).
        Defaults to None.
    :return: Intrinsic value per share (fair value estimate).
    """

    # use 9% as the default discount rate (for now, 11-12% is also an option)
    discount_rate = 1.09 if beta is None else beta_to_discount_rate(beta)

    # unless specified, can be GDP growth or Inflation (healthy is around 2%)
    if perpetual_growth_rate is None:
        perpetual_growth_rate = 1.02

    # sum of present value of cash over the next n years
    present_value_of_cash_flow_total = 0

    # cash flow of the current year based on growth and discount rates
    projected_cash_flow = cash_flow

    # discount rate over next n years
    discount_rate_total = 1

    # next n years
    n = growth_years

    for i in range(1, n + 2):
        if i == n + 1:  # terminal year
            projected_cash_flow *= perpetual_growth_rate
            projected_cash_flow /= discount_rate - perpetual_growth_rate
        else:
            projected_cash_flow *= growth_rate

        # Only update discount rate total for non-terminal years
        if i != n + 1:
            discount_rate_total *= discount_rate

        present_value_of_cash_flow = projected_cash_flow / discount_rate_total
        present_value_of_cash_flow_total += present_value_of_cash_flow

    intrinsic_value_per_share = present_value_of_cash_flow_total / shares

    return intrinsic_value_per_share


def convert_daily_ohlc_data_to_weekly(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert daily OHLC price data to weekly timeframe.

    Resamples daily bars to weekly using: first open, max high,
    min low, last close, and sum of volume. The index is adjusted
    to the beginning of each week (Monday).

    :param df: DataFrame with 'date', 'open', 'high', 'low', 'close',
        and 'volume' columns.
    :return: DataFrame with weekly OHLC data, indexed by week start
        date.
    """

    df["date"] = pd.to_datetime(df["date"], yearfirst=True)
    df = df.set_index("date")
    logic = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }
    df = df.resample("W").apply(logic)
    # set the index to the beginning of the week
    df.index = df.index - pd.tseries.frequencies.to_offset("6D")
    df = df.sort_values(by=["date"])

    return df
