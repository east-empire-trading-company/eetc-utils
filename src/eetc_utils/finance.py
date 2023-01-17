import math
from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd
from arch import arch_model


def garch_annualized_volatility(df: pd.DataFrame) -> float:
    """
    Calculate an annualized volatility forecast using the GARCH model.
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


def optimal_leverage_kelly_criterion(
    price_data: pd.DataFrame,
    position_start_date: str,
    position_type: str = "LONG",
    position_end_date: str = None,
    use_fractional_kelly: bool = False,
    use_garch: bool = False,
) -> float:
    """
    Calculate optimal leverage for a position using the Kelly Criterion.
    This is done by analysing the performance beginning with the start date,
    calculating annualized volatility, returns and using (fractional) Kelly to
    calculate the final value for optimal leverage. We also use GARCH to
    forecast annualized volatility to improve the model further.

    :param price_data: Price DataFrame
    :param position_start_date: Date when the position was entered into,
    format of "yyyy-mm-dd"
    :param position_type: String that indicates the position type, can be either
    "LONG" or "SHORT"
    :param position_end_date: Date when the position was exited (optional),
    format "yyyy-mm-dd"
    :param use_fractional_kelly: Indicates whether to use fractional Kelly or no
    :param use_garch: Indicates whether to use GARCH model for annualized
    volatility or not
    :return: Optimal leverage for the position
    """

    if not position_end_date:
        position_end_date = datetime.now().strftime("%Y-%m-%d")

    df = price_data[["date", "open", "high", "low", "close", "volume"]]
    mask = (df["date"] > position_start_date) & (df["date"] <= position_end_date)
    df = df.loc[mask]
    df = df.sort_values(by=["date"])

    # calculate daily returns (current close in relation to the previous close)
    if position_type == "SHORT":
        df["return_perc"] = 1 - (df["close"] / df["close"].shift(-1))
        df["return_perc"] = df["return_perc"].round(3)
    else:
        df["return_perc"] = (df["close"] / df["close"].shift(-1)) - 1
        df["return_perc"] = df["return_perc"].round(3)

    # calculate daily volatility
    df["volatility_perc"] = (df["high"] - df["low"]) / df["open"]
    df["volatility_perc"] = df["volatility_perc"].round(2)

    # calculate annualized return
    annualized_return = df["return_perc"].std() * math.sqrt(252)

    # calculate annualized volatility
    annualized_volatility = df["volatility_perc"].std() * math.sqrt(252)

    if use_garch:
        annualized_volatility = garch_annualized_volatility(df)

    # calculate optimal leverage
    optimal_leverage = annualized_return / (annualized_volatility**2)

    # use fractional kelly
    if use_fractional_kelly:
        optimal_leverage *= 0.5

    return optimal_leverage


def compound_interest(amount: float, period: int, interest: float) -> float:
    """
    Calculates compound interest.
    https://en.wikipedia.org/wiki/Compound_interest

    :param amount: Start amount.
    :param period: Periods of time (years, months, etc.).
    :param interest: Interest per period of time (year, month, etc.).
    :return:
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
    Calculates performance of an asset over time using it's OHLC price data.

    :param price_data: OHLC price data.
    :param start_date: Start date of the time period.
    :param end_date: End date of the time period.
    :return: Performance over time as a percentage.
    """

    df = price_data[start_date:end_date]
    return (df["Close"].iloc[-1] / df["Close"].iloc[0]) * 100 - 100


def beta_to_discount_rate(beta: Optional[float]) -> float:
    """
    Get a Discount Rate that "matches" the specified Beta.
    :param beta: https://en.wikipedia.org/wiki/Beta_(finance)
    :return: Discount Rate most fitting for the specified Beta.
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
    Calculates Intrinsic Value using the Discounted Cash Flow(DCF) model.
    https://en.wikipedia.org/wiki/Discounted_cash_flow

    :param cash_flow: Most recent Cash Flow (usually Operating Cash Flow)
    :param growth_years: # of years where growth is expected to match the
    specified growth rate.
    :param shares: # of Shares Outstanding.
    :param growth_rate: Expected growth rate.
    :param beta: https://en.wikipedia.org/wiki/Beta_(finance)
    :param perpetual_growth_rate: Expected growth rate after the final growth
    year, usually matches the GDP growth within which the business operates or
    the inflation rate.
    :return: Intrinsic value per share(the "real" share price).
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

        if i == n + 1:  # terminal year
            discount_rate_total = discount_rate_total
        else:
            discount_rate_total *= discount_rate

        present_value_of_cash_flow = projected_cash_flow / discount_rate_total
        present_value_of_cash_flow_total += present_value_of_cash_flow

    intrinsic_value_per_share = present_value_of_cash_flow_total / shares

    return intrinsic_value_per_share
