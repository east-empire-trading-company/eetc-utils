import math

import pytest

from src.eetc_utils.options import (
    find_strikes_in_range,
    calculate_option_price_black_scholes,
    calculate_underlying_iv_from_option_iv,
    GEX,
    PDF,
    CND,
    D1,
    D2,
)


# ai-generated
def test_find_strikes_in_range_returns_correct_strikes():
    # given
    range_length_perc = 0.1
    price = 100.0

    # calculate expected range
    lower_bound = int(price - (range_length_perc * price))
    upper_bound = int(price + (range_length_perc * price))
    expected_strikes = list(range(lower_bound, upper_bound + 2))

    # when
    result = find_strikes_in_range(range_length_perc, price)

    # then
    assert isinstance(result, list)
    assert len(result) == len(expected_strikes)
    assert result == expected_strikes
    assert result[0] == 90
    assert result[-1] == 111


# ai-generated
def test_calculate_option_price_black_scholes_call_option():
    # given
    right = "C"
    und_price = 100.0
    strike = 100.0
    rate = 0.05
    tte = 1.0
    implied_vol = 0.2
    pv_dividend = 0.0

    # calculate expected components
    div_yield = pv_dividend / und_price
    f = und_price * math.exp((rate - div_yield) * tte)
    d1 = (math.log(f / strike) + ((implied_vol**2 * tte) / 2)) / (
        implied_vol * math.sqrt(tte)
    )
    d2 = d1 - (implied_vol * math.sqrt(tte))

    # standard normal PDF
    pdf_d1 = (math.exp(-0.5 * d1**2)) / math.sqrt(2 * math.pi)
    pdf_d2 = (math.exp(-0.5 * d2**2)) / math.sqrt(2 * math.pi)

    # approximate CND values for this case
    expected_price_approx = 10.45

    # when
    result = calculate_option_price_black_scholes(
        right, und_price, strike, rate, tte, implied_vol, pv_dividend
    )

    # then
    assert isinstance(result, float)
    assert result > 0
    assert result == pytest.approx(expected_price_approx, rel=0.01)


# ai-generated
def test_calculate_option_price_black_scholes_put_option():
    # given
    right = "P"
    und_price = 100.0
    strike = 100.0
    rate = 0.05
    tte = 1.0
    implied_vol = 0.2
    pv_dividend = 0.0

    # approximate expected put price
    expected_price_approx = 5.57

    # when
    result = calculate_option_price_black_scholes(
        right, und_price, strike, rate, tte, implied_vol, pv_dividend
    )

    # then
    assert isinstance(result, float)
    assert result > 0
    assert result == pytest.approx(expected_price_approx, rel=0.01)


# ai-generated
def test_calculate_underlying_iv_from_option_iv_returns_correct_value():
    # given
    option_implied_vol = 0.2
    t = 30 / 365

    # calculate expected result
    expected_result = option_implied_vol * math.sqrt(t) * math.sqrt(2 / math.pi)

    # when
    result = calculate_underlying_iv_from_option_iv(option_implied_vol, t)

    # then
    assert isinstance(result, float)
    assert result > 0
    assert result == pytest.approx(expected_result, abs=1e-10)
    assert result == pytest.approx(0.0457, rel=0.01)


# ai-generated
def test_gex_calculates_correctly():
    # given
    oi = 1000
    gamma = 0.05

    # calculate expected GEX
    expected_gex = gamma * oi * 100

    # when
    result = GEX(oi, gamma)

    # then
    assert isinstance(result, float)
    assert result == expected_gex
    assert result == 5000.0


# ai-generated
def test_pdf_calculates_standard_normal_density():
    # given
    x = 0.0

    # at x=0, PDF should be 1/sqrt(2*pi)
    expected_pdf = 1 / math.sqrt(2 * math.pi)

    # when
    result = PDF(x)

    # then
    assert isinstance(result, float)
    assert result == pytest.approx(expected_pdf, abs=1e-10)
    assert result == pytest.approx(0.3989, rel=0.001)


# ai-generated
def test_pdf_calculates_for_nonzero_value():
    # given
    x = 1.0

    # calculate expected PDF at x=1
    expected_pdf = (math.exp(-0.5 * x**2)) / math.sqrt(2 * math.pi)

    # when
    result = PDF(x)

    # then
    assert isinstance(result, float)
    assert result == pytest.approx(expected_pdf, abs=1e-10)
    assert result == pytest.approx(0.2420, rel=0.001)


# ai-generated
def test_cnd_calculates_cumulative_distribution():
    # given
    x = 0.0
    sdx = PDF(0.0)

    # at x=0, CND should be 0.5
    expected_cnd = 0.5

    # when
    result = CND(x, sdx)

    # then
    assert isinstance(result, float)
    assert result == pytest.approx(expected_cnd, rel=0.01)


# ai-generated
def test_cnd_calculates_for_positive_value():
    # given
    x = 1.0
    sdx = PDF(1.0)

    # at x=1, CND should be approximately 0.8413
    expected_cnd = 0.8413

    # when
    result = CND(x, sdx)

    # then
    assert isinstance(result, float)
    assert result > 0.5
    assert result == pytest.approx(expected_cnd, rel=0.01)


# ai-generated
def test_d1_calculates_black_scholes_d1():
    # given
    strike = 100.0
    implied_vol = 0.2
    tte = 1.0
    forward_price = 105.0

    # calculate expected d1
    expected_d1 = (
        math.log(forward_price / strike) + ((implied_vol**2 * tte) / 2)
    ) / (implied_vol * math.sqrt(tte))

    # when
    result = D1(strike, implied_vol, tte, forward_price)

    # then
    assert isinstance(result, float)
    assert result == pytest.approx(expected_d1, abs=1e-10)
    assert result == pytest.approx(0.3438, rel=0.01)


# ai-generated
def test_d2_calculates_black_scholes_d2():
    # given
    d1_value = 0.3438
    implied_vol = 0.2
    tte = 1.0

    # calculate expected d2
    expected_d2 = d1_value - (implied_vol * math.sqrt(tte))

    # when
    result = D2(d1_value, implied_vol, tte)

    # then
    assert isinstance(result, float)
    assert result == pytest.approx(expected_d2, abs=1e-10)
    assert result == pytest.approx(0.1438, rel=0.01)