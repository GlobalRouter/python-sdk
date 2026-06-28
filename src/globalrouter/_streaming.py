from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

from globalrouter._errors import error_from_stream_payload

T = TypeVar("T", bound=BaseModel)


def iter_sse_models(response: httpx.Response, model: type[T]) -> Iterator[T]:
    data_lines: list[str] = []
    for line in response.iter_lines():
        if line == "":
            if not data_lines:
                continue
            item = _model_from_sse_data(data_lines, model)
            data_lines = []
            if item is None:
                break
            yield item
            continue

        data = _sse_data_value(line)
        if data is not None:
            data_lines.append(data)

    if data_lines:
        item = _model_from_sse_data(data_lines, model)
        if item is not None:
            yield item


async def aiter_sse_models(response: httpx.Response, model: type[T]) -> AsyncIterator[T]:
    data_lines: list[str] = []
    async for line in response.aiter_lines():
        if line == "":
            if not data_lines:
                continue
            item = _model_from_sse_data(data_lines, model)
            data_lines = []
            if item is None:
                break
            yield item
            continue

        data = _sse_data_value(line)
        if data is not None:
            data_lines.append(data)

    if data_lines:
        item = _model_from_sse_data(data_lines, model)
        if item is not None:
            yield item


def _sse_data_value(line: str) -> str | None:
    if not line.startswith("data:"):
        return None
    value = line.removeprefix("data:")
    if value.startswith(" "):
        value = value[1:]
    return value


def _model_from_sse_data(data_lines: list[str], model: type[T]) -> T | None:
    data = "\n".join(data_lines)
    if data.strip() == "[DONE]":
        return None
    payload = _json_from_text(data)
    if isinstance(payload, dict) and "error" in payload:
        raise error_from_stream_payload(payload)
    return model.model_validate(payload)


def _json_from_text(data: str) -> Any:
    return httpx.Response(200, content=data).json()
