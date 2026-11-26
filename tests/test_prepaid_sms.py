import unittest
from decimal import Decimal
from orderpilot.prepaid_sms import estimate_prepaid


class PrepaidTests(unittest.TestCase):
    def test_research_example(self):
        result = estimate_prepaid(1040, "0.84", "500")
        self.assertEqual((result.consumed, result.topups, result.cash_paid,
                          result.closing_credit),
                         (Decimal("873.60"), 2, Decimal("1000"), Decimal("126.40")))

    def test_exact_multiple(self):
        self.assertEqual(estimate_prepaid(100, "5", "500").topups, 1)

    def test_opening_credit(self):
        self.assertEqual(estimate_prepaid(10, "1", "500", "20").closing_credit,
                         Decimal("10"))
        self.assertEqual(estimate_prepaid(10, "1", "500", "20").topups, 0)

    def test_zero_demand(self):
        self.assertEqual(estimate_prepaid(0, "1", "500").cash_paid, Decimal("0"))

    def test_invalid(self):
        for args in [(-1,"1","500"), (True,"1","500"), (1,"NaN","500"),
                     (1,"1","0"), (1,"0.001","500"), (1,0.84,"500"),
                     (1,"1","500","-1")]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                estimate_prepaid(*args)
