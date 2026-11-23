---
title: "Plans and Subscription"
description: "Brinkpy's Academic and Professional plans, the 14-day free trial, how students and teachers qualify for the Academic plan, and how to subscribe, check, manage, or cancel a subscription from the CLI."
---

# Plans and Subscription

Brinkpy is free to use at this time. This page describes the paid plans that will start later, and the CLI commands for subscribing and managing a subscription.

!!! info "Paid plans are not active yet"
    Until paid plans start, every signed-in user can run problems free of charge, and the commands on this page are not shown in the CLI. We will announce the start date at least 30 days in advance. The commands become available in the CLI release that starts the paid plans.

## Plans

| Plan | For | Monthly | Yearly | Tax |
|---|---|---|---|---|
| Academic | Students and teachers, with a verified university email address | $8 | $80 | Included in the price |
| Professional | Everyone else | $25 | $250 | Added at checkout where it applies |

Prices are in US dollars. The payment page may show them in your local currency. Both plans include the same features. A yearly subscription costs less than 12 monthly payments.

## Free Trial

Every new user can use Brinkpy free for 14 days from their first run, without a payment method. Users who already use Brinkpy when the paid plans start get 14 days from the start date.

## Who Qualifies for the Academic Plan

Brinkpy offers the Academic plan automatically when the email address of your Brinkpy account is verified and belongs to a university or other academic institution, for example an address ending in `.edu`, `.ac.uk`, or `.edu.mx`. You don't need to send any proof.

- **Verify your email address.** When you sign up, Auth0 sends you an email with a verification link. The Academic plan is offered only after you click it.
- **Signed up with a personal email?** Create a second account with your university email address. Run `brinkpy user auth --force`, select **Sign up**, and use your university address (see [User Authentication](auth.md)).
- **Your institution isn't recognized?** Some universities use addresses that don't follow these patterns. Write to brinkpy.app@gmail.com from your university address, and we'll add your institution.
- **Teachers:** if you use Brinkpy in a course, write to brinkpy.app@gmail.com. We can give your students a promotion code for the course. They enter it on the payment page.

## Subscribe

Choose monthly or yearly billing:

```bash
brinkpy user subscribe
brinkpy user subscribe --yearly
```

Brinkpy shows the plan and price for your account, then opens the payment page in your web browser. For example:

```text
ℹ️  Plan: Brinkpy Academic, $8.00 per month (tax included)
ℹ️  You qualify for the Academic plan through the verified university email of your account.
ℹ️  Checkout page: https://checkout.stripe.com/...
✅ Opened in your web browser.
ℹ️  Your subscription starts when the payment on that page is complete.
```

| Option | Description |
|---|---|
| `--yearly`, `-y` | Bill yearly instead of monthly |
| `--open-browser` / `--no-open-browser` | Open the payment page in your web browser (default), or only print its link |

Payments are processed by [Stripe](https://stripe.com), which sells the subscription as the merchant of record through its Link service. Stripe collects any sales tax or value-added tax and sends your receipts and invoices. Brinkpy never receives your card details. If you have a promotion code, enter it on the payment page.

## Check Your Subscription

```bash
brinkpy user status
```

It shows your plan, the subscription status, and the next renewal date. For example:

```text
  Plan                Academic, billed monthly
  Status              Active
  Renews on           December 22, 2026
  Can run problems    Yes
```

If you have canceled, **Ends on** replaces **Renews on**. Without a subscription, it shows the plan your account qualifies for and how long your free trial lasts.

## Manage or Cancel

```bash
brinkpy user billing
```

This opens Stripe's subscription page in your web browser, where you can:

- Update your payment method or billing information.
- See and download your invoices.
- Cancel your subscription.

When you cancel, you keep access until the end of the period you paid for, and you are not charged again. The command accepts `--no-open-browser` to print the link instead of opening it. You can also manage your subscription at [link.com](https://link.com), with the email address you used to pay.

## Failed Payments

If a renewal payment fails, Stripe tries again over the following days and emails you. You can keep running problems while it retries, and `brinkpy user status` shows **Payment failed, retrying**. Update your payment method with `brinkpy user billing`. If the payment still fails after the last retry, the subscription is canceled and your access stops. You can subscribe again at any time.

## When a Run Is Refused

After your free trial, `analyze`, `design`, and `simulate` need a subscription.

- **Trial ended:** Brinkpy says so and offers to open the payment page. Answer the prompts to subscribe monthly or yearly.
- **Subscription not active:** Brinkpy points you to `brinkpy user billing`, to update your payment method, or to `brinkpy user subscribe`, to subscribe again.

## Refunds

See the [Refund Policy](legal/refunds.md).
