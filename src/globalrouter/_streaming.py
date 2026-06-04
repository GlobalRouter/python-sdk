from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

from globalrouter._errors import error_from_stream_payload

T = TypeVar("T", bound=BaseModel)


def iter_sse_models(response: httpx.Response, model: type[T]) -> Iterator[T]:
    for line in response.iter_lines():
        if not line.startswith("data: "):
            continue
        data = line.removeprefix("data: ").strip()
        if data == "[DONE]":
            break
        payload = _json_from_text(data)
        if isinstance(payload, dict) and "error" in payload:
            raise error_from_stream_payload(payload)
        yield model.model_validate(payload)


async def aiter_sse_models(response: httpx.Response, model: type[T]) -> AsyncIterator[T]:
    async for line in response.aiter_lines():
        if not line.startswith("data: "):
            continue
        data = line.removeprefix("data: ").strip()
        if data == "[DONE]":
            break
        payload = _json_from_text(data)
        if isinstance(payload, dict) and "error" in payload:
            raise error_from_stream_payload(payload)
        yield model.model_validate(payload)


def _json_from_text(data: str) -> Any:
    return httpx.Response(200, content=data).json()
