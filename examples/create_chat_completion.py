from __future__ import annotations

import json
import os
import shlex
import sys
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from globalrouter import GlobalRouter  # noqa: E402


REQUEST_BODY: dict[str, Any] = {
    "model": "qwen3-32b",
    "messages": [
        {"role": "user", "content": "用三句话介绍 GlobalRouter。"},
    ],
    "stream": False,
}


def main() -> None:
    if os.environ.get("GLOBALROUTER_EXAMPLE_REAL") == "1":
        client = GlobalRouter(
            api_key=os.environ["GLOBALROUTER_API_KEY"],
            base_url=os.environ.get("GLOBALROUTER_BASE_URL", "https://api.globalrouter.com"),
        )
        try:
            response = client.chat.send(REQUEST_BODY)
            print(json.dumps(response.model_dump(mode="json", exclude_none=True), ensure_ascii=False, indent=2))
        finally:
            client.close()
        return

    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            200,
            json={
                "id": "chatcmpl_123",
                "object": "chat.completion",
                "created": 1748372400,
                "model": "qwen3-32b",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": (
                                "GlobalRouter 是统一模型路由层。"
                                "它用同一套 API 连接不同模型和 Provider。"
                                "你可以通过模型 ID、鉴权和参数控制完成聊天、图片与视频生成。"
                            ),
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 18, "completion_tokens": 46, "total_tokens": 64, "cost": 0.0012},
            },
            request=request,
        )

    client = GlobalRouter(
        api_key=os.environ.get("GLOBALROUTER_API_KEY", "sk-local-example"),
        base_url=os.environ.get("GLOBALROUTER_BASE_URL", "http://127.0.0.1:8000"),
        transport=httpx.MockTransport(handler),
        max_retries=0,
    )
    try:
        response = client.chat.send(REQUEST_BODY)
    finally:
        client.close()

    print("# POST /api/v1/chat/completions")
    print("\n# Request JSON")
    print(json.dumps(json.loads(captured[0].content.decode("utf-8")), ensure_ascii=False, indent=2))
    print("\n# cURL")
    print(curl_for_request(captured[0]))
    print("\n# Mock response")
    print(json.dumps(response.model_dump(mode="json", exclude_none=True), ensure_ascii=False, indent=2))


def curl_for_request(request: httpx.Request) -> str:
    body = json.dumps(json.loads(request.content.decode("utf-8")), ensure_ascii=False, indent=2)
    lines = [f"curl -X {request.method} {shlex.quote(str(request.url))}"]
    for key, value in sorted(request.headers.items()):
        if key.lower() == "content-length":
            continue
        if key.lower() == "authorization":
            value = "Bearer ${GLOBALROUTER_API_KEY}"
        lines.append(f"  -H {shlex.quote(f'{key}: {value}')}")
    lines.append(f"  --data-raw {shlex.quote(body)}")
    return " \\\n+".replace("+", "").join(lines)


if __name__ == "__main__":
    main()
