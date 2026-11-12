"""Leave handling: email only when there is a useful transcript."""

from __future__ import annotations

from .infrai_client import InfraiClient
from .support_chat import VisitorSession


def send_leave_summary(client: InfraiClient, session: VisitorSession, support_address: str) -> str | None:
    lines = [line.strip() for line in session.transcript if line.strip()]
    if not lines:
        return None
    response = client.send_email(
        support_address,
        f"Support transcript from {session.visitor_id}",
        "\n".join(lines),
    )
    data = response.get("data") or {}
    message_id = data.get("message_id")
    if not isinstance(message_id, str):
        raise ValueError("email response did not include message_id")
    return message_id

