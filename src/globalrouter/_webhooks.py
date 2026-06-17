from __future__ import annotations

from hashlib import sha256
from hmac import compare_digest
from hmac import new as hmac_new


def verify_webhook_signature(secret: str, payload: bytes, signature: str) -> bool:
    if signature.startswith("sha256="):
        expected = hmac_new(secret.encode("utf-8"), payload, sha256).hexdigest()
        return compare_digest(expected, signature.removeprefix("sha256="))

    parts = dict(item.strip().split("=", 1) for item in signature.split(",") if "=" in item)
    timestamp = parts.get("t")
    provided = parts.get("v1")
    if timestamp is None or provided is None:
        return False

    signed_payload = timestamp.encode("utf-8") + b"." + payload
    expected = hmac_new(secret.encode("utf-8"), signed_payload, sha256).hexdigest()
    return compare_digest(expected, provided)
