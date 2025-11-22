import numpy as np
import pytest
import pandas as pd
from unittest.mock import patch, Mock

from src.eetc_utils.finance import (
    compound_interest,
    beta_to_discount_rate,
    intrinsic_value_using_dcf,
    convert_daily_ohlc_data_to_weekly,
    calculate_optimal_leverage_kelly,
    garch_annualized_volatility,
    performance_over_time,
)


# ai-generated
def test_compound_interest_calculates_correctly():
    # given
    amount = 1000.0
    period = 5
    interest = 10.0

    # when
    result = compound_interest(amount, period, interest)

    # then
    assert result == 1610.51
    assert isinstance(result, float)


# ai-generated
def test_beta_to_discount_rate_with_none_returns_default():
    # given
    beta = None

    # when
    result = beta_to_discount_rate(beta)

    # then
    assert result == 1.09


# ai-generated
def test_beta_to_discount_rate_with_various_betas():
    # given / when / then
    assert beta_to_discount_rate(0.5) == 1.05
    assert beta_to_discount_rate(0.8) == 1.06
    assert beta_to_discount_rate(0.9) == 1.06
    assert beta_to_discount_rate(1.0) == 1.065
    assert beta_to_discount_rate(1.1) == 1.07
    assert beta_to_discount_rate(1.2) == 1.075
    assert beta_to_discount_rate(1.3) == 1.08
    assert beta_to_discount_rate(1.4) == 1.085
    assert beta_to_discount_rate(1.5) == 1.09
    assert beta_to_discount_rate(2.0) == 1.09


# ai-generated
def test_intrinsic_value_using_dcf_calculates_correctly():
    # given
    cash_flow = 10000000000
    growth_years = 5
    shares = 1000000000
    growth_rate = 1.15
    beta = 1.2

    # when
    result = intrinsic_value_using_dcf(
        cash_flow, growth_years, shares, growth_rate, beta
    )

    # then
    assert isinstance(result, float)
    assert result > 0
    assert result == pytest.approx(321.31, rel=0.01)


# ai-generated
def test_intrinsic_value_using_dcf_with_defaults():
    # given
    cash_flow = 5000000000
    growth_years = 3
    shares = 500000000
    growth_rate = 1.10

    # when
    result = intrinsic_value_using_dcf(cash_flow, growth_years, shares, growth_rate)

    # then
    assert isinstance(result, float)
    assert result > 0
    assert result == pytest.approx(180.31, rel=0.01)


# ai-generated
def test_convert_daily_ohlc_data_to_weekly(sample_daily_ohlc_for_weekly_conversion):
    # given
    daily_df = sample_daily_ohlc_for_weekly_conversion.copy()

    # when
    weekly_df = convert_daily_ohlc_data_to_weekly(daily_df)

    # then
    assert isinstance(weekly_df, pd.DataFrame)
    assert len(weekly_df) == 2
    assert list(weekly_df.columns) == ["open", "high", "low", "close", "volume"]
    assert weekly_df["open"].iloc[0] == 100
    assert weekly_df["high"].iloc[0] == 108
    assert weekly_df["low"].iloc[0] == 99
    assert weekly_df["close"].iloc[0] == 104
    assert weekly_df["volume"].iloc[0] == 6000000
    assert weekly_df["open"].iloc[1] == 104
    assert weekly_df["high"].iloc[1] == 112
    assert weekly_df["low"].iloc[1] == 103
    assert weekly_df["close"].iloc[1] == 111
    assert weekly_df["volume"].iloc[1] == 8500000


# ai-generated
@patch("src.eetc_utils.finance.arch_model")
def test_garch_annualized_volatility_returns_positive_float(mock_arch_model):
    # given
    df = pd.DataFrame(
        {
            "close": [100, 101, 102, 101, 103, 104, 103, 105, 106, 107],
        }
    )
    mock_model = Mock()
    mock_res = Mock()
    mock_forecast = Mock()
    mock_forecast.variance = pd.DataFrame([[0.01]])
    mock_res.forecast.return_value = mock_forecast
    mock_model.fit.return_value = mock_res
    mock_arch_model.return_value = mock_model

    # when
    result = garch_annualized_volatility(df)

    # then
    assert isinstance(result, float)
    assert result > 0
    mock_arch_model.assert_called_once()
    mock_model.fit.assert_called_once()
    mock_res.forecast.assert_called_once_with(horizon=1, reindex=False)


# ai-generated
def test_performance_over_time_calculates_percentage_change():
    # given
    data = {
        "close": [100, 105, 110, 108, 112, 115, 118, 120, 125, 130],
    }
    df = pd.DataFrame(
        data, index=pd.date_range(start="2024-01-01", periods=10, freq="D")
    )
    start_date = "2024-01-01"
    end_date = "2024-01-10"

    # when
    result = performance_over_time(df, start_date, end_date)

    # then
    assert isinstance(result, float)
    assert result == 30.0
    assert result == pytest.approx((130 / 100) * 100 - 100, rel=0.01)


# ai-generated
def test_calculate_optimal_leverage_kelly_returns_correct_value():
    # given
    df = pd.DataFrame(
        {
            "date": pd.date_range(start="2020-01-01", periods=100, freq="D"),
            "close": [100.0 * (1.01 ** i) for i in range(100)],
        }
    )
    position_type = "LONG"
    regime_start_date = "2020-01-01"
    fractional_kelly_multiplier = 0.5
    use_garch = False

    # calculate expected result manually (matching function logic exactly)
    regime_start = pd.to_datetime(regime_start_date)
    last_date = df["date"].max()
    mask = (df["date"] >= regime_start) & (df["date"] < last_date)
    filtered_df = df.loc[mask].copy()

    filtered_df["log_return"] = np.log(
        filtered_df["close"] / filtered_df["close"].shift(1)
    )
    filtered_df = filtered_df.dropna()

    daily_mean_return = filtered_df["log_return"].mean()
    annualized_return = daily_mean_return * 252
    daily_variance = filtered_df["log_return"].var()
    annualized_variance = daily_variance * 252
    expected_kelly = annualized_return / annualized_variance
    expected_result = expected_kelly * fractional_kelly_multiplier

    # when
    result = calculate_optimal_leverage_kelly(
        df=df,
        position_type=position_type,
        regime_start_date=regime_start_date,
        fractional_kelly_multiplier=fractional_kelly_multiplier,
        use_garch=use_garch,
    )

    # then
    assert isinstance(result, float)
    assert result > 0
    assert result == pytest.approx(expected_result, rel=0.001)
