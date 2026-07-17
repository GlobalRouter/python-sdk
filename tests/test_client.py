from __future__ import annotations

import json
from collections.abc import Iterator
from hashlib import sha256
from hmac import new as hmac_new
from typing import Any

import httpx
import pytest
from pydantic import BaseModel

from globalrouter import GlobalRouter, GlobalRouterError
from globalrouter._streaming import aiter_sse_models, iter_sse_models


class SSEItem(BaseModel):
    id: str


def test_default_base_url_uses_production_api_domain(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GLOBALROUTER_API_KEY", "sk-test-local")

    with GlobalRouter() as client:
        assert client.base_url == "https://api.globalrouter.com"


def test_openrouter_surface_headers_and_resources(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GLOBALROUTER_API_KEY", "sk-test-local")
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/api/v1/chat/completions":
            return httpx.Response(
                200,
                json={
                    "id": "chat_1",
                    "object": "chat.completion",
                    "model": "mock-chat",
                    "choices": [{"message": {"content": "hi"}}],
                },
            )
        if request.url.path == "/api/v1/responses":
            return httpx.Response(200, json={"id": "resp_1", "object": "response"})
        if request.url.path == "/api/v1/messages":
            return httpx.Response(200, json={"id": "msg_1", "type": "message"})
        if request.url.path == "/api/v1/embeddings":
            return httpx.Response(200, json={"object": "list", "data": [{"embedding": [0.1]}]})
        if request.url.path == "/api/v1/models":
            return httpx.Response(200, json={"object": "list", "data": [{"id": "qwen3-32b"}]})
        if request.url.path == "/api/v1/models/count":
            return httpx.Response(200, json={"data": {"count": 1}})
        if request.url.path == "/api/v1/models/openrouter/owl-alpha/endpoints":
            return httpx.Response(200, json={"data": [{"model_id": "openrouter/owl-alpha"}]})
        if request.url.path == "/api/v1/credits":
            return httpx.Response(200, json={"data": {"total_credits": 10}})
        if request.url.path == "/api/v1/generation":
            return httpx.Response(200, json={"data": {"id": request.url.params["id"]}})
        if request.url.path == "/api/v1/key":
            return httpx.Response(200, json={"data": {"id": "key_1"}})
        if request.url.path == "/api/v1/keys":
            if request.method == "POST":
                return httpx.Response(200, json={"data": {"id": "key_2", "api_key": "sk-new"}})
            return httpx.Response(200, json={"data": [{"id": "key_1"}]})
        if request.url.path == "/api/v1/keys/key_2":
            if request.method == "PATCH":
                return httpx.Response(200, json={"data": {"id": "key_2", "name": "renamed"}})
            if request.method == "DELETE":
                return httpx.Response(200, json={"id": "key_2", "deleted": True})
            return httpx.Response(200, json={"data": {"id": "key_2"}})
        if request.url.path == "/api/v1/providers":
            return httpx.Response(200, json={"data": [{"id": "doubao"}]})
        if request.url.path == "/api/v1/videos":
            assert request.headers["idempotency-key"] == "idem_1"
            return httpx.Response(
                202,
                json={"id": "task_video", "object": "video.generation", "status": "queued"},
            )
        if request.url.path == "/api/v1/videos/task_video":
            return httpx.Response(
                200,
                json={"id": "task_video", "object": "video.generation", "status": "completed"},
            )
        if request.url.path == "/api/v1/videos/task_video/content":
            return httpx.Response(200, json={"data": [{"url": "https://example.test/v.mp4"}]})
        if request.url.path == "/api/v1/videos/models":
            return httpx.Response(200, json={"data": [{"id": "seedance-video"}]})
        return httpx.Response(404, json={"error": {"message": "missing"}})

    with GlobalRouter(base_url="http://testserver", transport=httpx.MockTransport(handler)) as c:
        assert c.chat.send(model="mock-chat", messages=[]).id == "chat_1"
        assert c.responses.create(model="mock-chat", input="hello").id == "resp_1"
        assert c.messages.create(model="mock-chat", messages=[]).id == "msg_1"
        assert c.embeddings.create(model="mock-embedding", input="hello").data
        assert c.models.list().data[0]["id"] == "qwen3-32b"
        assert c.models.count().data["count"] == 1
        assert c.models.endpoints("openrouter", "owl-alpha").data[0]["model_id"]
        assert c.credits.get().data["total_credits"] == 10
        assert c.generations.get("req_1").data["id"] == "req_1"
        assert c.keys.current().data["id"] == "key_1"
        assert c.keys.list(include_disabled=True).data[0]["id"] == "key_1"
        assert c.keys.get("key_2").data["id"] == "key_2"
        assert c.keys.create(name="child").data["api_key"] == "sk-new"
        assert c.keys.update("key_2", name="renamed").data["name"] == "renamed"
        assert c.keys.delete("key_2").deleted is True
        assert c.providers.list().data[0]["id"] == "doubao"
        assert c.videos.create(model="seedance-video", prompt="demo", idempotency_key="idem_1").id
        assert c.videos.get("task_video").status == "completed"
        assert c.videos.content("task_video").data[0]["url"]
        assert c.videos.models().data[0]["id"] == "seedance-video"

    assert requests
    assert all(request.headers["authorization"] == "Bearer sk-test-local" for request in requests)


def test_native_surface_and_sse_streaming() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/v1/chat/completions":
            assert json.loads(request.content)["stream"] is True
            return httpx.Response(
                200,
                content=_sse_lines(
                    [
                        {"id": "chunk_1", "choices": [{"delta": {"content": "hi"}}]},
                        "[DONE]",
                    ]
                ),
            )
        if request.url.path == "/v1/tasks" and request.method == "GET":
            assert request.url.params.get("metadata.project_id") == "project_1"
            return httpx.Response(200, json={"id": "task_1", "status": "queued"})
        if request.url.path == "/v1/tasks":
            return httpx.Response(200, json={"id": "task_1", "status": "queued"})
        if request.url.path == "/v1/tasks/batch":
            return httpx.Response(200, json={"data": [{"id": "task_1"}]})
        if request.url.path == "/v1/tasks/batch/batch_1":
            return httpx.Response(200, json={"data": [{"id": "task_1"}]})
        if request.url.path == "/v1/tasks/task_1":
            assert request.url.params.get("wait") == "1"
            return httpx.Response(200, json={"id": "task_1", "status": "succeeded"})
        if request.url.path == "/v1/tasks/task_1/events":
            return httpx.Response(
                200,
                content=_sse_lines([{"id": "event_1", "status": "running"}, "[DONE]"]),
            )
        if request.url.path == "/v1/tasks/task_1/cancel":
            return httpx.Response(200, json={"id": "task_1", "status": "canceled"})
        if request.url.path == "/v1/tasks/task_1/retry":
            return httpx.Response(200, json={"id": "task_1", "status": "queued"})
        if request.url.path == "/api/v1/images":
            return httpx.Response(200, json={"data": [{"url": "https://example.test/i.png"}]})
        if request.url.path == "/api/v1/image-tasks":
            assert request.headers["idempotency-key"] == "client-image-task-001"
            assert "idempotency_key" not in json.loads(request.content)
            return httpx.Response(
                200,
                json={
                    "id": "imgtask_1",
                    "object": "image.task",
                    "status": "queued",
                    "model": "jimeng_t2i_v31",
                },
            )
        if request.url.path == "/v1/audio/speech":
            return httpx.Response(200, json={"data": [{"url": "https://example.test/a.mp3"}]})
        if request.url.path == "/v1/audio/transcriptions":
            return httpx.Response(200, json={"text": "hello"})
        if request.url.path == "/v1/3d/generations":
            return httpx.Response(200, json={"id": "task_3d"})
        return httpx.Response(404, json={"error": {"message": "missing"}})

    client = GlobalRouter(
        api_key="sk-test-local",
        base_url="http://testserver",
        transport=httpx.MockTransport(handler),
    )
    try:
        assert list(client.chat.stream(model="mock-chat", messages=[]))[0].id == "chunk_1"
        assert client.tasks.create(type="image_generation", model="seedream-image").id == "task_1"
        assert client.tasks.create_batch([{"type": "image_generation"}]).data[0]["id"] == "task_1"
        assert client.tasks.get_batch("batch_1").data[0]["id"] == "task_1"
        assert client.tasks.list(metadata_project_id="project_1").id == "task_1"
        assert client.tasks.get("task_1", wait=True).status == "succeeded"
        assert list(client.tasks.events("task_1"))[0].id == "event_1"
        assert client.tasks.cancel("task_1").status == "canceled"
        assert client.tasks.retry("task_1").status == "queued"
        assert client.images.generate(model="seedream-image", prompt="hi").data
        assert client.images.create_task(
            model="jimeng_t2i_v31",
            prompt="hi",
            idempotency_key="client-image-task-001",
        ).id == "imgtask_1"
        assert client.audio.speech(model="tts", input="hi").data
        assert client.audio.transcription(model="asr", file_url="https://a.test").text == "hello"
        assert client.three_d.generate(model="tripo-3d", prompt="mesh").id == "task_3d"
    finally:
        client.close()


def test_chat_stream_error_frame_preserves_string_code() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/chat/completions"
        assert json.loads(request.content)["stream"] is True
        return httpx.Response(
            200,
            content=_sse_lines(
                [
                    {
                        "error": {
                            "code": "ROUTER_RATE_LIMITED",
                            "message": "limited",
                            "type": "rate_limit_error",
                            "request_id": "req_stream_1",
                        }
                    }
                ]
            ),
        )

    client = GlobalRouter(
        api_key="sk-test-local",
        base_url="http://testserver",
        transport=httpx.MockTransport(handler),
    )
    try:
        with pytest.raises(GlobalRouterError) as exc_info:
            list(client.chat.stream(model="mock-chat", messages=[]))
    finally:
        client.close()

    assert exc_info.value.status_code == 0
    assert exc_info.value.code == "ROUTER_RATE_LIMITED"
    assert exc_info.value.message == "limited"
    assert exc_info.value.error_type == "rate_limit_error"
    assert exc_info.value.request_id == "req_stream_1"


@pytest.mark.asyncio
async def test_async_chat_and_models() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/v1/chat/completions":
            return httpx.Response(
                200,
                json={
                    "id": "chat_async",
                    "object": "chat.completion",
                    "model": "mock-chat",
                    "choices": [],
                },
            )
        if request.url.path == "/api/v1/models":
            return httpx.Response(200, json={"object": "list", "data": [{"id": "mock-chat"}]})
        return httpx.Response(404)

    async with GlobalRouter(
        api_key="sk-test-local",
        base_url="http://testserver",
        async_transport=httpx.MockTransport(handler),
    ) as client:
        assert (await client.chat.send_async(model="mock-chat", messages=[])).id == "chat_async"
        assert (await client.models.list_async()).data[0]["id"] == "mock-chat"


@pytest.mark.asyncio
async def test_async_streaming_error_normalization() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return _streaming_error_response()

    async with GlobalRouter(
        api_key="sk-test-local",
        base_url="http://testserver",
        async_transport=httpx.MockTransport(handler),
    ) as client:
        with pytest.raises(GlobalRouterError) as exc_info:
            [item async for item in client.chat.stream_async(model="mock-chat", messages=[])]

    assert exc_info.value.status_code == 401
    assert exc_info.value.message == "Unauthorized"
    assert exc_info.value.code == "AUTH_REQUIRED"
    assert exc_info.value.request_id == "req_stream_1"


def test_error_normalization_and_retries() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(500, json={"error": {"message": "temporary"}})
        return httpx.Response(
            429,
            json={
                "error": {
                    "message": "Too many requests",
                    "code": 429,
                    "metadata": {
                        "type": "rate_limit_error",
                        "router_code": "ROUTER_RATE_LIMITED",
                        "request_id": "req_1",
                    },
                }
            },
        )

    client = GlobalRouter(
        api_key="sk-test-local",
        base_url="http://testserver",
        transport=httpx.MockTransport(handler),
    )
    try:
        with pytest.raises(GlobalRouterError) as exc_info:
            client.models.list()
    finally:
        client.close()

    assert attempts == 2
    assert exc_info.value.status_code == 429
    assert exc_info.value.code == "ROUTER_RATE_LIMITED"
    assert exc_info.value.error_type == "rate_limit_error"
    assert exc_info.value.request_id == "req_1"


def test_webhook_signature_verification(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = b'{"event":"task.succeeded"}'
    legacy = "sha256=0f2d86d81b7a8c4d936d190496d299da981be5857b083120430ea9b01e6d99f7"
    timestamp = "1778413678"
    digest = hmac_new(b"secret", timestamp.encode() + b"." + payload, sha256).hexdigest()
    monkeypatch.setattr("globalrouter._webhooks.time.time", lambda: int(timestamp) + 60)

    assert GlobalRouter.verify_webhook_signature("secret", payload, legacy) is True
    assert GlobalRouter.verify_webhook_signature("secret", payload, f"t={timestamp},v1={digest}")
    assert GlobalRouter.verify_webhook_signature("secret", payload, "sha256=bad") is False


def test_sse_parser_buffers_split_data_fields() -> None:
    response = httpx.Response(
        200,
        content=b'data: {"id": "split"\ndata: }\n\n',
    )

    assert list(iter_sse_models(response, SSEItem)) == [SSEItem(id="split")]


@pytest.mark.asyncio
async def test_async_sse_parser_buffers_split_data_fields() -> None:
    response = httpx.Response(
        200,
        content=b'data: {"id": "split"\ndata: }\n\n',
    )

    assert [item async for item in aiter_sse_models(response, SSEItem)] == [SSEItem(id="split")]


def test_stream_retries_5xx_before_returning_response() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(500, content=b'{"error":{"message":"temp"}}')
        return httpx.Response(200, content=b'data: {"id": "retry_ok"}\n\ndata: [DONE]\n\n')

    client = GlobalRouter(
        api_key="sk-test-local",
        base_url="http://testserver",
        max_retries=1,
        transport=httpx.MockTransport(handler),
    )
    try:
        response = client.stream("POST", "/api/v1/chat/completions", json_body={"stream": True})
        assert list(iter_sse_models(response, SSEItem)) == [SSEItem(id="retry_ok")]
    finally:
        client.close()

    assert attempts == 2


@pytest.mark.asyncio
async def test_async_stream_retries_5xx_before_returning_response() -> None:
    attempts = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(500, content=b'{"error":{"message":"temp"}}')
        return httpx.Response(200, content=b'data: {"id": "retry_ok"}\n\ndata: [DONE]\n\n')

    async with GlobalRouter(
        api_key="sk-test-local",
        base_url="http://testserver",
        max_retries=1,
        async_transport=httpx.MockTransport(handler),
    ) as client:
        response = await client.stream_async(
            "POST",
            "/api/v1/chat/completions",
            json_body={"stream": True},
        )
        assert [item async for item in aiter_sse_models(response, SSEItem)] == [
            SSEItem(id="retry_ok")
        ]

    assert attempts == 2


def _sse_lines(items: list[dict[str, Any] | str]) -> Iterator[bytes]:
    for item in items:
        payload = item if isinstance(item, str) else json.dumps(item)
        yield f"data: {payload}\n\n".encode()


def _streaming_error_response() -> httpx.Response:
    return httpx.Response(
        401,
        stream=httpx.ByteStream(
            json.dumps(
                {
                    "error": {
                        "message": "Unauthorized",
                        "code": "unauthorized",
                        "metadata": {
                            "type": "authentication_error",
                            "router_code": "AUTH_REQUIRED",
                            "request_id": "req_stream_1",
                        },
                    }
                }
            ).encode()
        ),
    )
