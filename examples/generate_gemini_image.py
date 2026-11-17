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

from globalrouter import GlobalRouter  # noqa: E402, I001


MODEL = "gemini-nano-banana-2.1"
REQUEST_BODY: dict[str, Any] = {
    "contents": [
        {
            "role": "user",
            "parts": [{"text": "生成一张 16:9 的极简产品插图，白色背景，柔和阴影。"}],
        }
    ],
    "generationConfig": {
        "responseModalities": ["TEXT", "IMAGE"],
        "imageConfig": {
            "aspectRatio": "16:9",
            "imageSize": "2K",
        },
    },
}


def main() -> None:
    if os.environ.get("GLOBALROUTER_EXAMPLE_REAL") == "1":
        client = GlobalRouter(
            api_key=os.environ["GLOBALROUTER_API_KEY"],
            base_url=os.environ.get("GLOBALROUTER_BASE_URL", "https://api.globalrouter.com"),
        )
        try:
            response = client.images.generate_content(MODEL, REQUEST_BODY)
            print(
                json.dumps(
                    response.model_dump(mode="json", by_alias=True, exclude_none=True),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        finally:
            client.close()
        return

    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {
                            "role": "model",
                            "parts": [
                                {"text": "Here is the generated image."},
                                {
                                    "inlineData": {
                                        "mimeType": "image/png",
                                        "data": "iVBORw0KGgoAAAANSUhEUg...",
                                    }
                                },
                            ],
                        },
                        "finishReason": "STOP",
                    }
                ],
                "modelVersion": MODEL,
                "responseId": "response_xxx",
                "usageMetadata": {
                    "promptTokenCount": 18,
                    "candidatesTokenCount": 1290,
                    "totalTokenCount": 1308,
                },
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
        response = client.images.generate_content(MODEL, REQUEST_BODY)
    finally:
        client.close()

    print(f"# POST /v1beta/models/{MODEL}:generateContent")
    print("\n# Request JSON")
    print(json.dumps(json.loads(captured[0].content.decode("utf-8")), ensure_ascii=False, indent=2))
    print("\n# cURL")
    print(curl_for_request(captured[0]))
    print("\n# Mock response")
    print(
        json.dumps(
            response.model_dump(mode="json", by_alias=True, exclude_none=True),
            ensure_ascii=False,
            indent=2,
        )
    )


def curl_for_request(request: httpx.Request) -> str:
    lines = [f"curl -X {request.method} {shlex.quote(str(request.url))}"]
    for key, value in request.headers.items():
        if key.lower() in {"accept-encoding", "connection", "host", "content-length"}:
            continue
        if key.lower() == "authorization":
            value = "Bearer ${GLOBALROUTER_API_KEY}"
        lines.append(f"  -H {shlex.quote(f'{key}: {value}')}")
    body = json.dumps(json.loads(request.content.decode("utf-8")), ensure_ascii=False, indent=2)
    lines.append(f"  --data-raw {shlex.quote(body)}")
    return " \\\n".join(lines)


if __name__ == "__main__":
    main()
