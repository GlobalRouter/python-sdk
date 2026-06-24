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
        metadata: Optional[dict[str, Any]] = None,
        response: Optional[httpx.Response] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.error_type = error_type
        self.request_id = request_id
        self.metadata = dict(metadata or {})
        self.response = response


def error_from_response(response: httpx.Response) -> GlobalRouterError:
    body: Any
    try:
        body = response.json()
    except ValueError:
        body = {}

    error = body.get("error", {}) if isinstance(body, dict) else {}
    metadata = _error_metadata(error)

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
        metadata=metadata,
        response=response,
    )


def error_from_stream_payload(payload: dict[str, Any]) -> GlobalRouterError:
    error = payload.get("error", {})
    metadata = _error_metadata(error)
    return GlobalRouterError(
        status_code=int(error.get("code") or 0) if isinstance(error, dict) else 0,
        code=_string(metadata.get("router_code")) or "GLOBALROUTER_STREAM_ERROR",
        message=_string(error.get("message")) or "GlobalRouter stream failed",
        error_type=_string(metadata.get("type")) or "router_error",
        request_id=_string(metadata.get("request_id")),
        metadata=metadata,
        response=None,
    )


def _error_metadata(error: Any) -> dict[str, Any]:
    metadata = error.get("metadata", {}) if isinstance(error, dict) else {}
    if not isinstance(metadata, dict):
        return {}
    return dict(metadata)


def _string(value: Any) -> Optional[str]:
    if value is None:
        return None
    return str(value)
