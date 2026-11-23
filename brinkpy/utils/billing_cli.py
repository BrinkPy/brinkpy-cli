"""
Subscription commands: start a subscription (Stripe Checkout), manage it (Stripe customer portal), and show its
status. The API decides the plan (Academic for a verified university email, Professional otherwise) and the price.
"""

import webbrowser
from datetime import datetime

import requests
from rich.console import Console
from rich.table import Table

from brinkpy.utils.api_utils import get_api_url
from brinkpy.utils.auth_cli import get_token
from brinkpy.utils.icons import ICON_ASK, ICON_ERR, ICON_INFO, ICON_OK, ICON_WARN

console = Console()

SUPPORT_EMAIL = "brinkpy.app@gmail.com"
PRICING_URL = "https://brinkpy.app/#pricing"

# Run refusals from the API that subscribing (or managing the subscription) resolves
SUBSCRIPTION_CODES = frozenset({"trial_ended", "subscription_not_active", "subscription_required", "subscription_expired"})

PLAN_NAMES = {"academic": "Academic", "professional": "Professional"}
INTERVAL_NAMES = {"month": "month", "year": "year"}


class BillingError(Exception):
    """A billing request failed. The message is ready to show, and action (if any) says what to do."""

    def __init__(self, message: str, action: str | None = None, code: str | None = None, status: int | None = None):
        super().__init__(message)
        self.action = action
        self.code = code
        self.status = status


def error_detail(response: requests.Response) -> tuple[str, str | None, str | None]:
    """(message, action, code) from an API error response."""
    try:
        detail = response.json().get("detail")
    except (ValueError, AttributeError):
        return (response.text or f"HTTP {response.status_code}").strip(), None, None
    if isinstance(detail, dict):
        message = detail.get("message") or detail.get("detail") or str(detail)
        return str(message), detail.get("action"), detail.get("code")
    return str(detail if detail is not None else f"HTTP {response.status_code}"), None, None


def billing_request(method: str, path: str, json: dict | None = None) -> dict:
    """Signed-in request to a billing endpoint. Raises BillingError with a message for the user."""
    token = get_token()
    if not token:
        raise BillingError("You are not signed in.", "Run 'brinkpy user auth' and try again.")
    url = f"{get_api_url()}{path}"
    try:
        response = requests.request(method, url, headers={"Authorization": f"Bearer {token}"}, json=json, timeout=30)
    except requests.RequestException as e:
        raise BillingError(f"Could not reach the Brinkpy API: {e}", "Check your connection and try again.") from e
    if response.status_code >= 400:
        message, action, code = error_detail(response)
        raise BillingError(message, action, code, response.status_code)
    try:
        return response.json()
    except ValueError as e:
        raise BillingError("The Brinkpy API returned an unexpected response.") from e


def print_billing_error(error: BillingError) -> None:
    console.print(f"{ICON_ERR} {error}")
    if error.action:
        console.print(f"{ICON_INFO} {error.action}")


def format_price(amount: float, currency: str) -> str:
    symbol = "$" if currency.lower() == "usd" else ""
    suffix = "" if symbol else f" {currency.upper()}"
    return f"{symbol}{amount:,.2f}{suffix}"


def checkout_summary(session: dict) -> list[str]:
    """Lines describing the plan and price the API chose, shown before the checkout page opens."""
    plan = session.get("plan", "")
    interval = INTERVAL_NAMES.get(session.get("interval", ""), session.get("interval", ""))
    price = format_price(float(session.get("amount", 0)), session.get("currency", "usd"))
    tax = "tax included" if session.get("tax_included") else "plus tax where it applies"
    lines = [f"Plan: Brinkpy {PLAN_NAMES.get(plan, plan)}, {price} per {interval} ({tax})"]
    if plan == "academic":
        lines.append("You qualify for the Academic plan through the verified university email of your account.")
    else:
        lines.append(
            "Students and teachers get the Academic plan when they sign in with a university email address. "
            f"If you qualify but signed up with another email, write to {SUPPORT_EMAIL}."
        )
    return lines


def open_url(url: str, what: str, open_browser: bool) -> None:
    console.print(f"{ICON_INFO} {what}: {url}")
    if not open_browser:
        return
    if webbrowser.open(url):
        console.print(f"{ICON_OK} Opened in your web browser.")
    else:
        console.print(f"{ICON_WARN} Could not open your web browser. Open the link above.")


def subscribe(yearly: bool = False, open_browser: bool = True) -> bool:
    """Starts a subscription: shows the plan and price, then opens Stripe Checkout. Returns True on success."""
    try:
        session = billing_request("POST", "/billing/checkout-session", json={"interval": "year" if yearly else "month"})
    except BillingError as e:
        print_billing_error(e)
        return False
    for line in checkout_summary(session):
        console.print(f"{ICON_INFO} {line}")
    open_url(session["checkout_url"], "Checkout page", open_browser)
    console.print(f"{ICON_INFO} Your subscription starts when the payment on that page is complete.")
    return True


def manage(open_browser: bool = True) -> bool:
    """Opens the Stripe customer portal, where the payment method can be updated and the subscription canceled."""
    try:
        portal = billing_request("POST", "/billing/portal-session")
    except BillingError as e:
        print_billing_error(e)
        return False
    open_url(portal["portal_url"], "Subscription management page", open_browser)
    return True


def _date(value: str | None) -> str:
    if not value:
        return "-"
    try:
        # In the user's time zone, as Stripe's pages show it: a period ending at 05:56 UTC ends the evening before
        # in the Americas
        d = datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone()
        return f"{d:%B} {d.day}, {d.year}"  # %-d doesn't work on Windows
    except ValueError:
        return value


STATUS_NAMES = {
    "active": "Active",
    "trialing": "Active (trial)",
    "past_due": "Payment failed, retrying",
    "canceled": "Canceled",
    "unpaid": "Unpaid",
    "incomplete": "Payment not completed",
    "incomplete_expired": "Payment not completed",
    "paused": "Paused",
}


def status_table(status: dict) -> Table:
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold")
    table.add_column()
    sub_status = status.get("subscription_status")
    if sub_status:
        plan = PLAN_NAMES.get(status.get("plan") or "", status.get("plan") or "-")
        interval = status.get("interval")
        table.add_row("Plan", f"{plan}, billed {'yearly' if interval == 'year' else 'monthly'}" if interval else plan)
        table.add_row("Status", STATUS_NAMES.get(sub_status, sub_status))
        if sub_status in {"active", "trialing", "past_due"}:
            label = "Ends on" if status.get("cancel_at_period_end") else "Renews on"
            table.add_row(label, _date(status.get("current_period_end")))
    else:
        table.add_row("Subscription", "None")
        table.add_row("Plan offered", PLAN_NAMES.get(status.get("plan_offered", ""), status.get("plan_offered", "-")))
    if status.get("enforced"):
        if not sub_status or sub_status not in {"active", "trialing", "past_due"}:
            trial_end = status.get("trial_ends_at")
            reason = status.get("access_reason")
            if reason == "trial":
                table.add_row("Free trial", f"until {_date(trial_end)}")
            elif reason == "trial_ended":
                table.add_row("Free trial", f"ended on {_date(trial_end)}")
        table.add_row("Can run problems", "Yes" if status.get("access") else "No")
    else:
        table.add_row("Can run problems", "Yes (Brinkpy is free to use at this time)")
    return table


def show_status() -> bool:
    try:
        status = billing_request("GET", "/billing/status")
    except BillingError as e:
        print_billing_error(e)
        return False
    console.print(status_table(status))
    if status.get("enforced") and not status.get("access"):
        console.print(f"{ICON_INFO} Run 'brinkpy user subscribe' to choose a plan. See {PRICING_URL}")
    return True


def handle_run_refused(response: requests.Response) -> bool:
    """
    For a run the API refused with 403: if subscribing would resolve it, prints the reason and offers checkout.
    Returns False when the refusal is not about the subscription, so the caller handles it as any other error.
    """
    message, action, code = error_detail(response)
    if (code or "").lower() not in SUBSCRIPTION_CODES:
        return False
    console.print(f"{ICON_WARN} {message}")
    if code == "subscription_not_active":
        console.print(f"{ICON_INFO} {action or 'Run brinkpy user billing to update your payment method.'}")
        return True
    answer = console.input(f"{ICON_ASK} Open the checkout page to subscribe now? [Y/n]: ").strip().lower()
    if answer not in {"", "y", "yes"}:
        console.print(f"{ICON_INFO} You can subscribe later with 'brinkpy user subscribe'. See {PRICING_URL}")
        return True
    period = console.input(f"{ICON_ASK} Billed monthly or yearly? [M/y]: ").strip().lower()
    subscribe(yearly=period in {"y", "yearly", "year"})
    return True
