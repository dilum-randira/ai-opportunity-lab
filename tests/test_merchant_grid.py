"""Regression cases for explicit workload × subscription-price scenarios."""
import unittest

from orderpilot.merchant_grid import compare


class MerchantGridTests(unittest.TestCase):
    def test_multi_volume_price_grid_and_messaging_sign_reversal(self):
        report = compare(
            workloads=[
                {"monthly_orders": 100, "service_messages_by_number": [200], "utility_messages": 100},
                {"monthly_orders": 520, "service_messages_by_number": [1040], "utility_messages": 520},
            ],
            subscription_prices_lkr=["2000", "2500", "3000"],
            seconds_saved_per_order="60", hourly_lkr="400",
            service_rate_lkr="3", utility_rate_lkr="3",
        )
        self.assertEqual(report["scenario_count"], 6)
        self.assertEqual([row["monthly_orders"] for row in report["rows"]], [100, 520])
        high_volume = report["rows"][1]
        self.assertEqual(high_volume["platform_messaging_cost_lkr"], "1680.00")
        self.assertEqual(high_volume["message_counts"]["service_billable"], 40)
        middle_price = high_volume["prices"][1]
        self.assertEqual(middle_price["subscription_lkr"], "2500.00")
        self.assertEqual(middle_price["net_before_messaging_lkr"], "966.67")
        self.assertEqual(middle_price["net_after_messaging_lkr"], "-713.33")
        self.assertFalse(middle_price["positive_after_messaging_under_assumptions"])

    def test_per_number_allowances_remain_separate(self):
        report = compare(
            workloads=[{"monthly_orders": 100, "service_messages_by_number": [1500, 500]}],
            subscription_prices_lkr=["0"], seconds_saved_per_order="60", hourly_lkr="600",
            service_rate_lkr="2",
        )
        row = report["rows"][0]
        self.assertEqual(row["business_phone_number_count"], 2)
        self.assertEqual(row["message_counts"]["service_billable"], 500)
        self.assertEqual(row["platform_messaging_cost_lkr"], "1000.00")

    def test_subcent_display_does_not_override_exact_positive_flag(self):
        report = compare(
            workloads=[{"monthly_orders": 1, "service_messages_by_number": [1]}],
            subscription_prices_lkr=["0"], seconds_saved_per_order="1", hourly_lkr="1",
            service_rate_lkr="0.0004", free_service_messages_per_number=0,
        )
        price = report["rows"][0]["prices"][0]
        self.assertEqual(price["net_after_messaging_lkr"], "0.00")
        self.assertFalse(price["positive_after_messaging_under_assumptions"])

    def test_price_normalization_and_duplicate_detection(self):
        common = dict(workloads=[{"monthly_orders": 1, "service_messages_by_number": [0]}],
                      seconds_saved_per_order="1", hourly_lkr="1")
        for prices in ([], ["1", "1.00"], [True], ["NaN"], ["-1"], list(range(11))):
            with self.subTest(prices=prices), self.assertRaises(ValueError):
                compare(subscription_prices_lkr=prices, **common)

    def test_reject_identifiers_unknown_fields_and_invalid_counts(self):
        common = dict(subscription_prices_lkr=["0"], seconds_saved_per_order="1", hourly_lkr="1")
        bad = [
            [{"monthly_orders": 1, "service_messages_by_number": [0], "phone_number": "private"}],
            [{"monthly_orders": 1}],
            [{"monthly_orders": True, "service_messages_by_number": [0]}],
            [{"monthly_orders": 0, "service_messages_by_number": [0]}],
            [{"monthly_orders": 1, "service_messages_by_number": [True]}],
            [{"monthly_orders": 1, "service_messages_by_number": [-1]}],
            [{"monthly_orders": 1, "service_messages_by_number": []}],
            [{"monthly_orders": 1, "service_messages_by_number": [0], "utility_messages": -1}],
            [{"monthly_orders": 1, "service_messages_by_number": [0]},
             {"monthly_orders": 1, "service_messages_by_number": [0]}],
        ]
        for workloads in bad:
            with self.subTest(workloads=workloads), self.assertRaises(ValueError):
                compare(workloads=workloads, **common)

    def test_limits_are_bounded(self):
        common = dict(seconds_saved_per_order="1", hourly_lkr="1")
        for workloads, prices in (
            ([], ["0"]),
            ([{"monthly_orders": i, "service_messages_by_number": [0]} for i in range(1, 22)], ["0"]),
            ([{"monthly_orders": i, "service_messages_by_number": [0]} for i in range(1, 12)],
             [str(i) for i in range(10)]),
        ):
            with self.subTest(size=(len(workloads), len(prices))), self.assertRaises(ValueError):
                compare(workloads=workloads, subscription_prices_lkr=prices, **common)

    def test_aggregate_only_no_customer_identifiers_in_result(self):
        result = compare(workloads=[{"monthly_orders": 1, "service_messages_by_number": [0]}],
                         subscription_prices_lkr=["0"], seconds_saved_per_order="1", hourly_lkr="1")
        self.assertNotIn("phone_number", result)
        self.assertNotIn("customer_id", str(result))
        self.assertEqual(result["rows"][0]["business_phone_number_count"], 1)


if __name__ == "__main__":
    unittest.main()
