"""Exact break-even must respect service allowances and integer billing."""
import unittest
from orderpilot.discrete_break_even import first_profitable_volume

class DiscreteBreakEvenTests(unittest.TestCase):
    def test_positive_at_one(self):
        r=first_profitable_volume(max_orders=10,seconds_saved_per_order=3600,hourly_lkr="10",subscription_lkr="1")
        self.assertEqual(r["first_positive_monthly_orders"],1)

    def test_no_positive_within_cap(self):
        r=first_profitable_volume(max_orders=10,seconds_saved_per_order=1,hourly_lkr="1",subscription_lkr="500")
        self.assertIsNone(r["first_positive_monthly_orders"])

    def test_allowance_changes_first_positive(self):
        params=dict(seconds_saved_per_order=3600,hourly_lkr="10",subscription_lkr="15",
                    service_messages_per_order="1",service_rate_lkr="9")
        free=first_profitable_volume(max_orders=20,free_service_messages=5,**params)
        paid=first_profitable_volume(max_orders=20,free_service_messages=0,**params)
        self.assertEqual(free["first_positive_monthly_orders"],2)
        self.assertEqual(paid["first_positive_monthly_orders"],16)

    def test_reject_invalid_caps(self):
        for value in [True,0,-1,1000001,"100"]:
            with self.subTest(value=value),self.assertRaises(ValueError):
                first_profitable_volume(max_orders=value,seconds_saved_per_order=1,hourly_lkr=1,subscription_lkr=1)

if __name__=="__main__":
    unittest.main()
