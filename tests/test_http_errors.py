import json
import unittest
from unittest.mock import patch

import requests
from rich.panel import Panel

from brinkpy.utils import api_utils


def make_response(status_code: int, body) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response._content = (json.dumps(body) if not isinstance(body, str) else body).encode()
    return response


def printed_panel(printed) -> Panel:
    panels = [call.args[0] for call in printed.call_args_list if call.args and isinstance(call.args[0], Panel)]
    assert len(panels) == 1, f"expected one panel, got {len(panels)}"
    return panels[0]


class HandleOtherHttpErrorsTests(unittest.TestCase):
    def run_handler(self, response, context_msg="App request failed") -> Panel:
        with patch.object(api_utils.console, "print") as printed:
            api_utils.handle_other_http_errors(response, context_msg)
        return printed_panel(printed)

    def test_coded_detail_prints_message_in_error_panel(self):
        message = "Design optimization (SciPy trust-constr) found no solution for case 'default' after 8 attempts."
        panel = self.run_handler(make_response(422, {"detail": {"code": "ConvergenceError", "message": message}}))
        self.assertEqual(panel.title, "Error")
        self.assertEqual(panel.border_style, "red")
        self.assertIn(message, panel.renderable.plain)
        self.assertNotIn("status code", panel.renderable.plain)

    def test_coded_detail_keeps_brackets(self):
        message = "The initial guess d = [1, 1] may be too far from a solution."
        panel = self.run_handler(make_response(422, {"detail": {"code": "ConvergenceError", "message": message}}))
        self.assertIn(message, panel.renderable.plain)

    def test_plain_detail_puts_context_and_status_in_title(self):
        panel = self.run_handler(make_response(500, {"detail": "Something broke"}))
        self.assertEqual(panel.title, "App request failed · status code 500")
        self.assertIn("Something broke", panel.renderable.plain)

    def test_fastapi_validation_422_is_not_treated_as_coded(self):
        detail = [{"loc": ["body", "file"], "msg": "Field required", "type": "missing"}]
        panel = self.run_handler(make_response(422, {"detail": detail}))
        self.assertEqual(panel.title, "App request failed · status code 422")
        self.assertIn("Field required", panel.renderable.plain)

    def test_non_json_body(self):
        panel = self.run_handler(make_response(502, "Bad Gateway"), "Error downloading results file")
        self.assertEqual(panel.title, "Error downloading results file · status code 502")
        self.assertIn("Bad Gateway", panel.renderable.plain)


class HandleRateLimitErrorTests(unittest.TestCase):
    def run_handler(self, response) -> Panel:
        with patch.object(api_utils.console, "print") as printed:
            api_utils.handle_rate_limit_error(response)
        return printed_panel(printed)

    def test_daily_limit_in_yellow_panel(self):
        body = {"endpoint": "/run_app", "limit_type": "per_day", "limit_exceeded": "20 per 1 day", "all_limits": "20/day"}
        panel = self.run_handler(make_response(429, body))
        self.assertEqual(panel.title, "Rate limit exceeded")
        self.assertEqual(panel.border_style, "yellow")
        text = panel.renderable.plain
        self.assertIn("Daily Limit Exceeded: 20 per 1 day", text)
        self.assertIn("You've used up your daily quota", text)

    def test_unparseable_response(self):
        panel = self.run_handler(make_response(429, "Too Many Requests"))
        self.assertEqual(panel.title, "Rate limit exceeded")
        self.assertIn("Unable to parse rate limit response", panel.renderable.plain)


if __name__ == "__main__":
    unittest.main()
