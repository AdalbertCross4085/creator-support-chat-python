"""Typed domain events for the creator support channel."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .infrai_client import InfraiClient


@dataclass(frozen=True)
class SupportEvent:
    kind: str
    detail: str


@dataclass(frozen=True)
class VisitorSession:
    visitor_id: str
    subscriber_id: str
    transcript: tuple[str, ...]


def publish_session(client: InfraiClient, session: VisitorSession) -> list[dict[str, object]]:
    events = [
        SupportEvent("digital-asset-delivery", "download link issued"),
        SupportEvent("subscriber-update", f"subscriber {session.subscriber_id} notified"),
        SupportEvent("content-processing", "content review queued"),
    ]
    return [
        client.publish("creator-support", event.kind, asdict(event), session.subscriber_id)
        for event in events
    ]

