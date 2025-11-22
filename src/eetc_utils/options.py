import math
from typing import List


def find_strikes_in_range(range_length_perc: float, price: float) -> List[int]:
    """
    Calculate the range of strike prices implied by a given percentage move.

    :param range_length_perc: The range as a percentage.
    :param price: The current price.
    :return: A list of strike prices within the implied range.
    """

    lower_bound, upper_bound = int(price - (range_length_perc * price)), int(
        price + (range_length_perc * price)
    )
    return list(range(lower_bound, upper_bound + 2))


def calculate_option_price_black_scholes(
    right: str,
    und_price: float,
    strike: float,
    rate: float,
    tte: float,
    implied_vol: float,
    pv_dividend: float,
) -> float:
    """
    Calculate the Option Price using the Black & Scholes model.

    :param right: "C" or "P" to indicate whether it's a Call or Put Option.
    :param und_price: Underlying price.
    :param strike: Strike price.
    :param rate: Risk-free rate.
    :param tte: Time to expiration in years.
    :param implied_vol: Implied volatility of the Option.
    :param pv_dividend: Price dividend.
    :return: Option Price based on Black & Scholes model.
    """

    div_yield = pv_dividend / und_price
    # if no dividends, then forward price is just stock price
    f = und_price * math.exp((rate - div_yield) * tte)
    d1 = D1(strike, implied_vol, tte, f)
    d2 = D2(d1, implied_vol, tte)

    if right == "P":
        cd1 = CND(-d1, PDF(-d1))
        cd2 = CND(-d2, PDF(-d2))
        return (strike * math.exp(-rate * tte) * cd2) - (und_price * cd1)

    cd1 = CND(d1, PDF(d1))
    cd2 = CND(d2, PDF(d2))

    return ((f * cd1) - (strike * cd2)) * math.exp(-rate * tte)


def calculate_underlying_iv_from_option_iv(
    option_implied_vol: float, t: float
) -> float:
    """
    Calculate Implied Vol of the underlying during the specified Time period.
    Use this as a replacement for VIX, as VIX might be broken/manipulated.

    :param option_implied_vol: Implied Vol of an ATM Option.
    :param t: Time to expiration in years.
    :return: Implied Vol of the underlying during the specified Time period t.
    """

    return option_implied_vol * math.sqrt(t) * math.sqrt(2 / math.pi)


def GEX(oi, gamma) -> float:
    """
    Calculate GEX for a specific Option contract.

    :param oi: Open Interest in Specific Strike.
    :param gamma: Gamma.
    :return: GEX in shares.
    """

    return gamma * oi * 100


def PDF(x: float) -> float:
    """
    Standard Normal Probability Density function.

    :param x: Input variable of the function.
    :return: Probability density of x.
    """

    return (math.exp(-0.5 * pow(x, 2))) / math.sqrt(2 * math.pi)


def CND(x: float, sdx: float) -> float:
    """
    Using the Abramowitz & Stegun (1964) numerical approximation with 6 constant
    values. Account for negative values of x. Instead of using math.pow to
    calculate the t-values, we use multiplication to achieve ~20 times
    more efficiency.

    :param x: Input variable of the function.
    :param sdx: Probability density of x.
    :return: Cumulative Normal Distribution of x.
    """

    P = 0.2316419
    b1 = 0.319381350
    b2 = -0.356563782
    b3 = 1.781477937
    b4 = -1.821255978
    b5 = 1.330274429

    t = 1 / (1 + P * abs(x))
    t1 = t
    t2 = t1 * t
    t3 = t2 * t
    t4 = t3 * t
    t5 = t4 * t
    # SUM = B1 + B2 + B3 + B4 + B5 where (Bn = bn * tn)
    SUM = (b1 * t1) + (b2 * t2) + (b3 * t3) + (b4 * t4) + (b5 * t5)
    CD = 1 - (sdx * SUM)

    return 1 - CD if x < 0 else CD


def D1(x: float, iv: float, t: float, f: float) -> float:
    """
    Calculate d1 of Black-Scholes.

    :param x: Option Strike Price.
    :param iv: Implied Volatility.
    :param t: Time to expiration in years.
    :param f: Forward price of the underlying.
    :return: d1 of Black-Scholes.
    """

    return (math.log(f / x) + ((pow(iv, 2) * t) / 2)) / (pow(t, 0.5) * iv)


def D2(d1: float, iv: float, t: float) -> float:
    """
    Calculate d2 of Black-Scholes.

    :param d1: d1 of Black-Scholes.
    :param iv: Implied Volatility.
    :param t: Time to expiration in years.
    :return: d2 of Black-Scholes.
    """

    return d1 - (iv * pow(t, 0.5))
