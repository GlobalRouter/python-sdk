import json

import httpx
import pytest

from globalrouter import GlobalRouter


@pytest.mark.parametrize("stream", [False, True])
def test_chat_preserves_media_types_and_extensions(stream: bool) -> None:
    content = [
        {"type": "video", "video": {"url": "https://example.test/a.mp4"}},
        {"type": "video_url", "video_url": {"url": "https://example.test/b.mp4"}, "fps": 2},
        {"type": "input_audio", "input_audio": {"data": "UklGRg==", "format": "wav"}},
        {"type": "file", "file": {"file_id": "file-test"}},
        {"type": "custom_input", "custom": {"enabled": False}},
    ]
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(json.loads(request.content))
        result = {"id": "chat-test", "model": "gemini-3.8-flash", "choices": []}
        if stream:
            return httpx.Response(
                200,
                text=f"data: {json.dumps(result)}\n\ndata: [DONE]\n\n",
                headers={"content-type": "text/event-stream"},
            )
        return httpx.Response(200, json=result)

    with GlobalRouter(
        api_key="test-key", base_url="https://router.test",
        transport=httpx.MockTransport(handler),
    ) as client:
        params = {
            "model": "gemini-3.8-flash",
            "messages": [{"role": "user", "content": content}],
        }
        if stream:
            assert list(client.chat.stream(params))
        else:
            assert client.chat.send(params).id == "chat-test"
    assert len(seen) == 1
    assert seen[0]["messages"][0]["content"] == content
