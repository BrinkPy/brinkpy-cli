import json
import os
import unittest
from unittest.mock import patch

import requests

from brinkpy.utils import billing_cli


def make_response(status_code: int, body) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response._content = (json.dumps(body) if not isinstance(body, str) else body).encode()
    return response


def table_rows(table) -> dict:
    labels, values = (list(column.cells) for column in table.columns)
    return dict(zip(labels, values))


class ErrorDetailTests(unittest.TestCase):
    def test_coded_detail(self):
        response = make_response(403, {"detail": {"code": "trial_ended", "message": "Trial ended.", "action": "Run x."}})
        self.assertEqual(billing_cli.error_detail(response), ("Trial ended.", "Run x.", "trial_ended"))

    def test_plain_detail_and_non_json(self):
        self.assertEqual(billing_cli.error_detail(make_response(503, {"detail": "Down"})), ("Down", None, None))
        self.assertEqual(billing_cli.error_detail(make_response(502, "Bad gateway")), ("Bad gateway", None, None))


class CheckoutSummaryTests(unittest.TestCase):
    def test_academic(self):
        lines = billing_cli.checkout_summary(
            {"plan": "academic", "interval": "month", "amount": 8.0, "currency": "usd", "tax_included": True}
        )
        self.assertEqual(lines[0], "Plan: Brinkpy Academic, $8.00 per month (tax included)")
        self.assertIn("university email", lines[1])

    def test_professional_explains_how_to_get_academic(self):
        lines = billing_cli.checkout_summary(
            {"plan": "professional", "interval": "year", "amount": 250.0, "currency": "usd", "tax_included": False}
        )
        self.assertEqual(lines[0], "Plan: Brinkpy Professional, $250.00 per year (plus tax where it applies)")
        self.assertIn("Students and teachers", lines[1])
        self.assertIn(billing_cli.SUPPORT_EMAIL, lines[1])


class SubscribeTests(unittest.TestCase):
    def test_sends_interval_and_opens_checkout(self):
        session = {"checkout_url": "https://checkout.stripe.com/x", "plan": "academic", "interval": "year",
                   "amount": 80.0, "currency": "usd", "tax_included": True}
        with patch.object(billing_cli, "billing_request", return_value=session) as request, \
                patch.object(billing_cli.webbrowser, "open", return_value=True) as opened, \
                patch.object(billing_cli.console, "print"):
            self.assertTrue(billing_cli.subscribe(yearly=True))
        request.assert_called_once_with("POST", "/billing/checkout-session", json={"interval": "year"})
        opened.assert_called_once_with("https://checkout.stripe.com/x")

    def test_already_subscribed_prints_action(self):
        error = billing_cli.BillingError("You already have a Brinkpy subscription.", "Run 'brinkpy user billing'.",
                                         "already_subscribed", 409)
        with patch.object(billing_cli, "billing_request", side_effect=error), \
                patch.object(billing_cli.console, "print") as printed:
            self.assertFalse(billing_cli.subscribe())
        output = " ".join(str(c.args[0]) for c in printed.call_args_list)
        self.assertIn("already have", output)
        self.assertIn("brinkpy user billing", output)


class StatusTableTests(unittest.TestCase):
    def test_not_enforced(self):
        rows = table_rows(billing_cli.status_table(
            {"enforced": False, "access": True, "access_reason": "not_enforced", "plan_offered": "professional"}
        ))
        self.assertEqual(rows["Subscription"], "None")
        self.assertEqual(rows["Plan offered"], "Professional")
        self.assertTrue(rows["Can run problems"].startswith("Yes"))

    def test_active_subscription(self):
        rows = table_rows(billing_cli.status_table({
            "enforced": True, "access": True, "access_reason": "subscription", "plan_offered": "academic",
            "subscription_status": "active", "plan": "academic", "interval": "year",
            "current_period_end": "2027-11-23T18:00:00Z", "cancel_at_period_end": False,
        }))
        self.assertEqual(rows["Plan"], "Academic, billed yearly")
        self.assertEqual(rows["Renews on"], "November 23, 2027")

    def test_canceled_at_period_end_and_trial_ended(self):
        rows = table_rows(billing_cli.status_table({
            "enforced": True, "access": True, "access_reason": "subscription", "subscription_status": "active",
            "plan": "professional", "interval": "month", "current_period_end": "2027-01-05T18:00:00+00:00",
            "cancel_at_period_end": True,
        }))
        self.assertEqual(rows["Ends on"], "January 5, 2027")
        rows = table_rows(billing_cli.status_table({
            "enforced": True, "access": False, "access_reason": "trial_ended", "plan_offered": "academic",
            "trial_ends_at": "2027-03-01T18:00:00Z",
        }))
        self.assertEqual(rows["Free trial"], "ended on March 1, 2027")
        self.assertEqual(rows["Can run problems"], "No")


class LocalDateTests(unittest.TestCase):
    def test_dates_are_shown_in_the_local_time_zone(self):
        # 05:56 UTC on December 23 is December 22 in El Paso, as Stripe's portal shows it
        with patch.dict("os.environ", {"TZ": "America/Denver"}):
            import time

            time.tzset()
            try:
                self.assertEqual(billing_cli._date("2026-12-23T05:56:43+00:00"), "December 22, 2026")
            finally:
                del os.environ["TZ"]
                time.tzset()


class RunRefusedTests(unittest.TestCase):
    def test_other_refusals_are_left_to_the_caller(self):
        response = make_response(403, {"detail": "Not authenticated"})
        self.assertFalse(billing_cli.handle_run_refused(response))

    def test_trial_ended_offers_checkout(self):
        response = make_response(403, {"detail": {"code": "trial_ended", "message": "Trial ended.", "action": "x"}})
        with patch.object(billing_cli.console, "input", side_effect=["y", "y"]), \
                patch.object(billing_cli.console, "print"), \
                patch.object(billing_cli, "subscribe") as subscribe:
            self.assertTrue(billing_cli.handle_run_refused(response))
        subscribe.assert_called_once_with(yearly=True)

    def test_inactive_subscription_points_to_billing(self):
        response = make_response(403, {"detail": {"code": "subscription_not_active", "message": "Not active.",
                                                  "action": "Run 'brinkpy user billing'."}})
        with patch.object(billing_cli.console, "print") as printed, \
                patch.object(billing_cli.console, "input") as asked:
            self.assertTrue(billing_cli.handle_run_refused(response))
        asked.assert_not_called()
        self.assertIn("brinkpy user billing", " ".join(str(c.args[0]) for c in printed.call_args_list))


if __name__ == "__main__":
    unittest.main()
