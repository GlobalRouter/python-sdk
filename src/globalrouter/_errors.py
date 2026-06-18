from __future__ import annotations

from typing import Any, Optional

import httpx


class GlobalRouterError(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        error_type: str,
        request_id: Optional[str] = None,
        response: Optional[httpx.Response] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.error_type = error_type
        self.request_id = request_id
        self.response = response


def error_from_response(response: httpx.Response) -> GlobalRouterError:
    body: Any
    try:
        body = response.json()
    except ValueError:
        body = {}

    error = body.get("error", {}) if isinstance(body, dict) else {}
    metadata = error.get("metadata", {}) if isinstance(error, dict) else {}
    if not isinstance(metadata, dict):
        metadata = {}

    message = _string(error.get("message")) or response.text or "GlobalRouter request failed"
    code = (
        _string(metadata.get("router_code"))
        or _string(error.get("code"))
        or "GLOBALROUTER_HTTP_ERROR"
    )
    error_type = (
        _string(metadata.get("type"))
        or _string(error.get("type"))
        or "router_error"
    )
    request_id = _string(metadata.get("request_id")) or _string(error.get("request_id"))

    return GlobalRouterError(
        status_code=response.status_code,
        code=code,
        message=message,
        error_type=error_type,
        request_id=request_id,
        response=response,
    )


def error_from_stream_payload(payload: dict[str, Any]) -> GlobalRouterError:
    error = payload.get("error", {})
    error_body = error if isinstance(error, dict) else {}
    metadata = error_body.get("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    return GlobalRouterError(
        status_code=_stream_status_code(error_body),
        code=(
            _string(metadata.get("router_code"))
            or _string(error_body.get("code"))
            or "GLOBALROUTER_STREAM_ERROR"
        ),
        message=_string(error_body.get("message")) or "GlobalRouter stream failed",
        error_type=_string(metadata.get("type")) or "router_error",
        request_id=_string(metadata.get("request_id")),
        response=None,
    )


def _stream_status_code(error: dict[str, Any]) -> int:
    for key in ("status_code", "status", "code"):
        value = _int(error.get(key))
        if value is not None:
            return value
    return 0


def _int(value: Any) -> Optional[int]:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    return None


def _string(value: Any) -> Optional[str]:
    if value is None:
        return None
    return str(value)
