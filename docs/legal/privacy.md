---
title: "Privacy Policy"
description: "What information Brinkpy CLI, the Brinkpy API, and the brinkpy.app website collect, how it is used and shared, how long it is kept, and how to have it deleted."
---

# Privacy Policy

Last updated: November 22, 2026

This policy explains what information Brinkpy collects, why, who it is shared with, and how long it is kept. Brinkpy means Brinkpy CLI, the Brinkpy API that the CLI sends problems to, and the website at brinkpy.app. Brinkpy is developed and operated by Cesar Carrasco ("we", "us"). We do not sell your information, and we do not use it for advertising.

## Information We Collect

### Your Account

Sign-in is handled by Auth0, an identity service. When you create an account, Auth0 stores your email address, whether it has been verified, a name and nickname, and a profile picture if your sign-in method provides one. Auth0 also records sign-ins, including the time and the IP address. We use your email address to identify your account, to decide whether you qualify for the Academic plan, and to contact you about your account and about changes to Brinkpy, such as the start of paid plans.

### Your Runs

When you run `analyze`, `design`, or `simulate`, the CLI uploads your problem file and the run options to the API. The API uses them only to run your request.

- The uploaded problem file is deleted when the run finishes.
- Result files (Excel, PDF, and pickle) are deleted when the CLI downloads them. If they are not downloaded, they are deleted 2 minutes after the run, and any file left over for an unexpected reason is deleted within an hour.
- The results the CLI saves in your project folder stay on your computer. We do not keep a copy.

To operate and protect the service, the API records each request in its logs: your account's user ID, your IP address, the time, the name of the problem file, a request ID, the run options, and how long the run took and how much memory it used. If a run fails, the log includes the error message, which may quote a line of your problem file. Your IP address is also used to limit how many requests can be sent in a period of time. Our hosting provider keeps these logs for a limited period that depends on our hosting plan, and then deletes them.

### Payments

When paid plans are available, subscriptions are sold through Stripe, which acts as the merchant of record. Stripe collects your payment details, billing address, and email address, under the [Stripe Privacy Policy](https://stripe.com/privacy). We do not receive your full card details. We receive and store your plan, the subscription status and renewal date, and the Stripe customer and subscription identifiers, linked to your account's user ID.

### The Website

The website does not use analytics, does not show advertising, and does not set cookies for tracking. It stores display preferences, such as the light or dark color scheme, in your browser. The website's fonts are served from brinkpy.app itself. Cloudflare hosts the website and receives your IP address and the pages you request, to deliver and protect the site.

### On Your Computer

The CLI stores your sign-in tokens in a file on your computer (see [User Authentication](../auth.md)). Deleting the file signs you out. The CLI sends your information only to Auth0 and to the API.

## Who We Share It With

We share information only with the services that run Brinkpy, and only as needed for them to do so:

| Service | What it does | Information |
|---|---|---|
| Auth0 (Okta) | Sign-in | Account information |
| Railway | Hosts the API, its logs, and the subscription database | Uploaded problems during a run, request logs, subscription records |
| Stripe | Sells subscriptions as merchant of record, collects tax | Payment and billing information |
| Cloudflare | Hosts the website | Website visits |

We may also disclose information when the law requires it, or to protect the security of Brinkpy and its users.

These services are in the United States or process information there. By using Brinkpy, your information is processed in the United States.

## How Long We Keep It

| Information | Kept |
|---|---|
| Uploaded problem files | Until the run finishes |
| Result files on the server | Until downloaded, or 2 minutes after the run |
| Request logs | For the period our hosting provider keeps logs, then deleted |
| Account information | Until you ask us to close your account |
| Subscription records | While your account is open, and afterward as long as tax and accounting law requires |

## Your Choices and Rights

You can ask us to:

- Tell you what information we hold about you.
- Correct it.
- Close your account and delete your information, except what the law requires us to keep, such as payment records.

Write to brinkpy.app@gmail.com from the email address of your account. We will answer within 30 days. Depending on where you live, you may have other rights under local law, such as the right to object to some uses or to complain to a data protection authority. We will honor them as the law requires.

## Children

Brinkpy is not intended for children under 13, and we do not knowingly collect information from them. If you believe a child under 13 has created an account, write to us and we will delete it.

## Security

The connection between the CLI and the API, and between your browser and the website, is encrypted. Problem files run in isolated processes with restricted access. No system is perfectly secure, but we take reasonable measures to protect your information.

## Changes to This Policy

We may update this policy. We will post the new version on this page with a new date, and for material changes we will notify you by email or in the CLI before they take effect.

## Contact

Questions about this policy or your information: brinkpy.app@gmail.com
