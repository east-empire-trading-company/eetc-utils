import unittest

from financials import intrinsic_value_using_dcf


class TestFinancials(unittest.TestCase):
    def test_intrinsic_value_using_dcf(self):
        # given
        expected_val = 124.2003644237247
        cash_flow = 80670000000
        growth_years = 3
        shares = 16980000000
        growth_rate = 1.15
        beta = 1.21

        # when
        val = intrinsic_value_using_dcf(
            cash_flow=cash_flow,
            growth_years=growth_years,
            shares=shares,
            growth_rate=growth_rate,
            beta=beta,
        )

        # then
        self.assertEqual(val, expected_val)
