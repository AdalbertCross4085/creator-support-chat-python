from dataclasses import dataclass

from src.leave_summary import send_leave_summary
from src.support_chat import VisitorSession


@dataclass
class FakeClient:
    sent: list[tuple[str, str, str]]

    def send_email(self, to: str, subject: str, body: str) -> dict[str, object]:
        self.sent.append((to, subject, body))
        return {"ok": True, "data": {"message_id": "msg-1"}}


def test_leave_with_transcript_sends_one_message_and_empty_leave_does_not() -> None:
    client = FakeClient([])
    session = VisitorSession("visitor-17", "subscriber-42", ("Need the download", "All set"))
    assert send_leave_summary(client, session, "support@example.com") == "msg-1"
    assert client.sent[0][2] == "Need the download\nAll set"

    empty = VisitorSession("visitor-18", "subscriber-43", ("", "  "))
    assert send_leave_summary(client, empty, "support@example.com") is None
    assert len(client.sent) == 1

