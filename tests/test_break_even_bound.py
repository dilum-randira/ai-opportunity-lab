"""Regression checks for conservative whole-message break-even bounds."""
from decimal import Decimal
import random
import unittest
from orderpilot.unit_economics import project


class BreakEvenBoundTests(unittest.TestCase):
    def test_fractional_service_rounding_cannot_make_threshold_optimistic(self):
        scenario = dict(monthly_orders=1, seconds_saved_per_order=3600,
                        hourly_lkr='2', subscription_lkr='1.5',
                        service_messages_per_order='0.5', service_rate_lkr='1')
        result = project(**scenario)
        threshold = result['conservative_break_even_orders_excluding_allowance']
        self.assertEqual(threshold, 2)
        self.assertGreaterEqual(Decimal(project(**(scenario | {'monthly_orders': threshold}))['monthly_lkr']['net_value']), Decimal('0'))

    def test_randomized_conservative_thresholds(self):
        rng = random.Random(20261021)
        checked = 0
        for _ in range(250):
            seconds = rng.choice([60, 300, 1800, 3600])
            hourly = rng.choice([20, 100, 500])
            price = rng.choice([0, 10, 50, 100, 200])
            svc_per_order = rng.choice(['0', '0.1', '0.25', '0.5', '1', '1.3'])
            util_per_order = rng.choice(['0', '0.2', '0.5', '1.5'])
            svc_rate = rng.choice(['0', '1', '5', '20'])
            util_rate = rng.choice(['0', '2', '8'])
            base = dict(monthly_orders=1, seconds_saved_per_order=seconds,
                        hourly_lkr=hourly, subscription_lkr=price,
                        service_messages_per_order=svc_per_order,
                        service_rate_lkr=svc_rate,
                        utility_messages_per_order=util_per_order,
                        utility_rate_lkr=util_rate,
                        free_service_messages=rng.choice([0, 10, 100]))
            threshold = project(**base)['conservative_break_even_orders_excluding_allowance']
            if threshold is None:
                continue
            for n in [threshold, min(1_000_000, threshold + 1), min(1_000_000, threshold + 17)]:
                net = Decimal(project(**(base | {'monthly_orders': n}))['monthly_lkr']['net_value'])
                self.assertGreaterEqual(net, Decimal('0'), (base, n, net))
                checked += 1
        self.assertGreater(checked, 200)

if __name__ == '__main__':
    unittest.main()
