import unittest
from orderpilot.roi_simple import estimate_roi


class ROITests(unittest.TestCase):
    def test_positive(self):
        r = estimate_roi(orders_per_month=600, seconds_saved_per_order=60,
                         hourly_lkr=600, monthly_subscription_lkr=500)
        self.assertEqual(r["net_monthly_value_lkr"], "5500.00")
        self.assertTrue(r["potentially_positive"])

    def test_negative(self):
        r = estimate_roi(orders_per_month=520, seconds_saved_per_order=62,
                         hourly_lkr=400, monthly_subscription_lkr=3500,
                         monthly_operating_lkr=2200)
        self.assertEqual(r["net_monthly_value_lkr"], "-2117.78")

    def test_bad_parameters(self):
        valid = dict(orders_per_month=20, seconds_saved_per_order=60,
                     hourly_lkr=400, monthly_subscription_lkr=500)
        for field, bad in [
            ("orders_per_month", 0),
            ("orders_per_month", True),
            ("hourly_lkr", "NaN"),
            ("seconds_saved_per_order", -2),
            ("monthly_subscription_lkr", "inf"),
            ("seconds_saved_per_order", 40000),
        ]:
            with self.subTest(field=field, bad=bad), self.assertRaises(ValueError):
                estimate_roi(**(valid | {field: bad}))


if __name__ == "__main__":
    unittest.main()
