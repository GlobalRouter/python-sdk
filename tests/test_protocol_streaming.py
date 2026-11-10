"""Controlled transport contracts, separate from deployment rollback acceptance."""

from __future__ import annotations

import json
import runpy
from collections.abc import AsyncIterator, Iterator
from pathlib import Path
from typing import Any

import httpx
import pytest

from globalrouter import GlobalRouter, GlobalRouterError
from globalrouter._models import APIResponse


class SyncBody(httpx.SyncByteStream):
    def __init__(self, body: bytes) -> None:
        self.body = body
        self.closed = False

    def __iter__(self) -> Iterator[bytes]:
        yield self.body

    def close(self) -> None:
        self.closed = True


class AsyncBody(httpx.AsyncByteStream):
    def __init__(self, body: bytes) -> None:
        self.body = body
        self.closed = False

    async def __aiter__(self) -> AsyncIterator[bytes]:
        yield self.body

    async def aclose(self) -> None:
        self.closed = True


def result(protocol: str) -> dict[str, Any]:
    if protocol == "messages":
        return {
            "id": "msg_1", "content": [
                {"type": "thinking", "thinking": "reason"},
                {"type": "tool_use", "id": "t", "name": "lookup", "input": {"x": None}},
            ], "usage": {"input_tokens": 2, "output_tokens": 1},
        }
    return {"id": "resp_1", "output": [
        {"type": "function_call", "name": "lookup", "arguments": "{}"},
        {"type": "reasoning", "encrypted_content": "  opaque  "},
        {"type": "image_generation_call", "result": "data:image/png;base64,png"},
    ], "usage": {"input_tokens": 2, "output_tokens": 1}}


def wire(protocol: str, media: str, failure: bool = False) -> bytes:
    body = result(protocol)
    if failure:
        event = {"type": "response.failed", "response": {
            "error": {"code": "PROVIDER_FAILED", "message": "controlled"},
        }} if protocol == "responses" else {
            "type": "error", "error": {"code": "PROVIDER_FAILED", "message": "controlled"},
        }
    else:
        event = {"type": "response.completed", "response": body} if protocol == "responses" else {
            "type": "message_start", "message": body,
        }
    if media == "application/json":
        return json.dumps(body).encode()
    return f"event: {event['type']}\ndata: {json.dumps(event)}\n\n".encode()


@pytest.mark.parametrize("protocol", ["messages", "responses"])
@pytest.mark.parametrize("media", ["application/json", "text/event-stream"])
@pytest.mark.parametrize("early_close", [False, True])
def test_sync_new_sse_and_old_json_once_and_close(protocol, media, early_close):
    requests = []
    body = SyncBody(wire(protocol, media))

    def handler(request):
        requests.append(request)
        return httpx.Response(200, headers={"content-type": media}, stream=body)

    with GlobalRouter(api_key="controlled", transport=httpx.MockTransport(handler)) as client:
        resource = getattr(client, protocol)
        kwargs = {"anthropic_version": "2023-06-01"} if protocol == "messages" else {}
        stream = resource.create({"model": "m", "stream": True}, **kwargs)
        first = next(stream)
        expected = result(protocol) if media == "application/json" else (
            {"type": "response.completed", "response": result(protocol)}
            if protocol == "responses" else {"type": "message_start", "message": result(protocol)}
        )
        assert first.model_dump(exclude_unset=True) == expected
        if early_close:
            stream.close()
        else:
            assert list(stream) == []
    assert body.closed
    assert len(requests) == 1
    assert requests[0].url.path == f"/api/v1/{protocol}"
    assert json.loads(requests[0].content) == {"model": "m", "stream": True}
    if protocol == "messages":
        assert requests[0].headers["anthropic-version"] == "2023-06-01"


@pytest.mark.parametrize("protocol", ["messages", "responses"])
@pytest.mark.parametrize("media", ["application/json", "text/event-stream"])
@pytest.mark.parametrize("early_close", [False, True])
async def test_async_new_sse_and_old_json_once_and_close(protocol, media, early_close):
    requests = []
    body = AsyncBody(wire(protocol, media))

    async def handler(request):
        requests.append(request)
        return httpx.Response(200, headers={"content-type": media}, stream=body)

    async with GlobalRouter(
        api_key="controlled", async_transport=httpx.MockTransport(handler),
    ) as client:
        kwargs = {"anthropic_beta": "controlled-beta"} if protocol == "messages" else {}
        stream = await getattr(client, protocol).create_async(
            {"model": "m", "stream": True}, **kwargs,
        )
        first = await stream.__anext__()
        expected = result(protocol) if media == "application/json" else (
            {"type": "response.completed", "response": result(protocol)}
            if protocol == "responses" else {"type": "message_start", "message": result(protocol)}
        )
        assert first.model_dump(exclude_unset=True) == expected
        if early_close:
            await stream.aclose()
        else:
            assert [item async for item in stream] == []
    assert body.closed and len(requests) == 1
    if protocol == "messages":
        assert requests[0].headers["anthropic-beta"] == "controlled-beta"


@pytest.mark.parametrize("protocol", ["messages", "responses"])
def test_sync_error_event_closes_without_retry(protocol):
    requests = []
    body = SyncBody(wire(protocol, "text/event-stream", failure=True))

    def handler(request):
        requests.append(request)
        return httpx.Response(200, headers={"content-type": "text/event-stream"}, stream=body)

    with GlobalRouter(api_key="controlled", transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(GlobalRouterError, match="controlled"):
            list(getattr(client, protocol).create(model="m", stream=True))
    assert body.closed and len(requests) == 1


@pytest.mark.parametrize("protocol", ["messages", "responses"])
async def test_async_error_event_closes_without_retry(protocol):
    requests = []
    body = AsyncBody(wire(protocol, "text/event-stream", failure=True))

    async def handler(request):
        requests.append(request)
        return httpx.Response(200, headers={"content-type": "text/event-stream"}, stream=body)

    async with GlobalRouter(
        api_key="controlled", async_transport=httpx.MockTransport(handler),
    ) as client:
        stream = await getattr(client, protocol).create_async(model="m", stream=True)
        with pytest.raises(GlobalRouterError, match="controlled"):
            [item async for item in stream]
    assert body.closed and len(requests) == 1


@pytest.mark.parametrize("protocol", ["messages", "responses"])
@pytest.mark.parametrize("value", [None, False])
def test_json_null_or_false_preserves_response_object(protocol, value):
    def handler(request):
        return httpx.Response(200, json=result(protocol))

    with GlobalRouter(api_key="controlled", transport=httpx.MockTransport(handler)) as client:
        response = getattr(client, protocol).create({"model": "m", "stream": value})
    assert isinstance(response, APIResponse)
    assert response.model_dump(exclude_unset=True) == result(protocol)


@pytest.mark.parametrize("media", ["application/json", "text/event-stream"])
async def test_documented_sync_async_examples_execute_with_one_request_and_complete_result(
    monkeypatch, capsys, media,
):
    example = runpy.run_path(str(Path(__file__).parents[1] / "examples" / "stream_protocols.py"))
    requests = []
    bodies = []

    def sync_handler(request):
        requests.append(request)
        body = SyncBody(wire("messages", media))
        bodies.append(body)
        return httpx.Response(200, headers={"content-type": media}, stream=body)

    async def async_handler(request):
        requests.append(request)
        body = AsyncBody(wire("responses", media))
        bodies.append(body)
        return httpx.Response(200, headers={"content-type": media}, stream=body)

    def client_factory(**kwargs):
        return GlobalRouter(
            api_key="controlled", transport=httpx.MockTransport(sync_handler),
            async_transport=httpx.MockTransport(async_handler), **kwargs,
        )

    monkeypatch.setenv("GLOBALROUTER_MESSAGES_MODEL", "controlled-messages")
    monkeypatch.setenv("GLOBALROUTER_RESPONSES_MODEL", "controlled-responses")
    example["messages"].__globals__["GlobalRouter"] = client_factory
    example["messages"]()
    await example["responses"]()
    output = capsys.readouterr().out
    for content in ("tool_use", "thinking", "function_call", "  opaque  ", "image_generation_call"):
        assert content in output
    assert len(requests) == 2
    assert all(body.closed for body in bodies)
    assert [request.url.path for request in requests] == [
        "/api/v1/messages", "/api/v1/responses",
    ]
