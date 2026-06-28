from __future__ import annotations

import time
from hashlib import sha256
from hmac import compare_digest
from hmac import new as hmac_new

DEFAULT_WEBHOOK_TIMESTAMP_TOLERANCE_SECONDS = 300


def verify_webhook_signature(
    secret: str,
    payload: bytes,
    signature: str,
    *,
    timestamp_tolerance_seconds: int | None = DEFAULT_WEBHOOK_TIMESTAMP_TOLERANCE_SECONDS,
) -> bool:
    if signature.startswith("sha256="):
        expected = hmac_new(secret.encode("utf-8"), payload, sha256).hexdigest()
        return compare_digest(expected, signature.removeprefix("sha256="))

    parts = dict(item.split("=", 1) for item in signature.split(",") if "=" in item)
    timestamp = parts.get("t")
    provided = parts.get("v1")
    if timestamp is None or provided is None:
        return False

    try:
        timestamp_seconds = int(timestamp)
    except ValueError:
        return False

    if timestamp_tolerance_seconds is not None:
        if timestamp_tolerance_seconds < 0:
            return False
        if abs(time.time() - timestamp_seconds) > timestamp_tolerance_seconds:
            return False

    signed_payload = timestamp.encode("utf-8") + b"." + payload
    expected = hmac_new(secret.encode("utf-8"), signed_payload, sha256).hexdigest()
    return compare_digest(expected, provided)
