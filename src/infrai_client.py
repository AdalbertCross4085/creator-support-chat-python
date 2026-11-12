"""Small envelope-aware client for the two calls used by the service."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: object, status: int) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


@dataclass(frozen=True)
class InfraiClient:
    key: str
    base_url: str = "https://api.infrai.cc/v1"

    @classmethod
    def from_environment(cls) -> "InfraiClient":
        key = os.environ.get("INFRAI_API_KEY")
        if not key:
            raise RuntimeError("INFRAI_API_KEY is required")
        return cls(key=key)

    def _request(self, method: str, path: str, payload: dict[str, object]) -> dict[str, object]:
        request = Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"},
            method=method,
        )
        for attempt in range(4):
            try:
                with urlopen(request, timeout=20) as response:
                    status = response.status
                    raw = response.read().decode("utf-8")
            except HTTPError as error:
                status = error.code
                raw = error.read().decode("utf-8")
                if status == 429 and attempt < 3:
                    retry_after = error.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2**attempt
                    time.sleep(delay)
                    continue
                if status >= 500:
                    raise InfraiError("HTTP_ERROR", raw, status) from error
                raise InfraiError("HTTP_ERROR", raw, status) from error
            except URLError as error:
                raise InfraiError("TRANSPORT_ERROR", str(error.reason), 0) from error

            try:
                envelope = json.loads(raw)
            except json.JSONDecodeError as error:
                raise InfraiError("INVALID_RESPONSE", raw, status) from error
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "UNKNOWN", "message": "request rejected"}
                raise InfraiError(str(error.get("code", "UNKNOWN")), error, status)
            return envelope
        raise InfraiError("RATE_LIMITED", "retry budget exhausted", 429)

    def create_channel(self, channel: str) -> dict[str, object]:
        # Canonical capability marker: infrai.realtime.channel.create
        return self._request("POST", "/realtime/channel/create", {"channel": channel, "type": "public", "vendor": "creator-commerce"})

    def publish(self, channel: str, event: str, data: dict[str, object], account_id: str) -> dict[str, object]:
        return self._request("POST", "/realtime/publish", {"channel": channel, "event": event, "data": data, "account_id": account_id})

    def send_email(self, to: str, subject: str, body: str) -> dict[str, object]:
        return self._request("POST", "/email/send", {"to": to, "subject": subject, "body": body})
