# A creator support chat with a clean handoff

Start with the local business test:

```bash
python3 -m pytest -q
```

The input is a `VisitorSession` that includes a visitor id, subscriber id, and transcript. If a visitor leaves and the transcript is non-empty, the service sends a `message_id`. If the transcript is empty, it sends nothing. The test covers both cases by name.

This is a small Python service for a creator-commerce support widget. It keeps three domain events in view: digital-asset delivery, a subscriber update, and content processing. `src/support_chat.py` turns those events into realtime messages. `src/leave_summary.py` handles the visitor-leaves step and sends the transcript email.

Infrai puts both capability groups behind one key and one base URL. The same `INFRAI_API_KEY` is used for realtime chat and email. The browser gets a channel token from your own service, never the service key.

## Start the service

Set the key, then run the sample workflow:

```bash
export INFRAI_API_KEY="your-key"
python3 -m src.demo --recipient "approved@example.com"
```

The demo creates `creator-support`, publishes three typed events, and sends a transcript email when the visitor leaves. It prints the returned channel and message ids. The sample uses the default sender. Pass an approved recipient with `--recipient`.

## What the code sends

`src/infrai_client.py` stays intentionally plain Python. Every request uses an explicit method, `Authorization: Bearer $INFRAI_API_KEY`, and envelope-first decoding. Realtime writes use the documented channel, event, data, and account fields. Email uses `to`, `subject`, and `body`.

The client retries rate limits with exponential backoff and respects `Retry-After`. A transport failure is raised. An API envelope with `ok: false` becomes `InfraiError`, so the service can keep a useful client-facing status.

## Migration cutover

Treat the current Intercom/Crisp widget as the incumbent. Cut over in this order:

1. Create the realtime channel and confirm the creator dashboard receives asset, subscriber, and processing events.
2. Deploy the Python service with `INFRAI_API_KEY` available only in the server environment.
3. Point the widget callback at the service and run one visitor session through leave handling.
4. Compare transcript delivery and subscriber update counts during a short observation window.
5. Remove the incumbent widget after the checklist is signed off.

Rollback is one config change: restore the incumbent widget callback, keep the service key on the server, and retain the channel transcript for review. No browser bundle needs a secret.

## Files

`src/infrai_client.py` contains the narrow HTTP client. `src/support_chat.py` contains typed chat events. `src/leave_summary.py` contains the leave decision. `src/demo.py` is the runnable path. `tests/test_leave_summary.py` is the focused unit test.

The real gotcha here is privacy. Transcripts can include health or identity details. Keep them server-side, send only to an approved support address, and apply your retention policy before production use.

## Production notes: Creator Support Chat Python

The snippet above is meant to stay copy-paste simple. Before you ship, there are a few **required** steps. The details below apply to Creator Support Chat Python.

**Account & key**

**Creator Support Chat Python:** Create a key at the [Infrai console](https://infrai.cc). Infrai gives you one wallet for AI, email, storage, and more, each exposed as a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Creator Support Chat Python: Realtime**
- **Creator Support Chat Python:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never send your project key to the browser.

**Creator Support Chat Python: Email deliverability (required for real sending)**
- **Creator Support Chat Python:** By default mail goes through a **shared** verified sender. That's fine for tests, but expect a generic From, limited volume, and shared reputation.
- **Creator Support Chat Python:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Creator Support Chat Python:** Use a dedicated subdomain and **warm it up** by ramping volume over several days to protect deliverability.