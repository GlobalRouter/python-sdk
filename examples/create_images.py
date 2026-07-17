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
    "model": "seedream-image",
    "prompt": "生成一张简洁的模型网关架构图。",
    "input_references": [
        {
            "type": "image_url",
            "image_url": {"url": "https://example.com/reference.png"},
        }
    ],
    "provider": {
        "provider_id": "doubao",
        "options": {
            "doubao": {"some_provider_option": "value"},
        },
    },
    "background": "transparent",
    "aspect_ratio": "1:1",
    "resolution": "2K",
    "output_compression": 90,
    "output_format": "png",
    "quality": "high",
    "seed": 42,
    "stream": False,
    "n": 1,
}


def main() -> None:
    if os.environ.get("GLOBALROUTER_EXAMPLE_REAL") == "1":
        client = GlobalRouter(
            api_key=os.environ["GLOBALROUTER_API_KEY"],
            base_url=os.environ.get("GLOBALROUTER_BASE_URL", "https://api.globalrouter.com"),
        )
        try:
            response = client.images.generate(REQUEST_BODY)
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
                "created": 1748372400,
                "data": [{"b64_json": "iVBORw0KGgoAAAANSUhEUg...", "media_type": "image/png"}],
                "usage": {"prompt_tokens": 0, "completion_tokens": 4175, "total_tokens": 4175, "cost": 0.04},
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
        response = client.images.generate(REQUEST_BODY)
    finally:
        client.close()

    print("# POST /api/v1/images")
    print("\n# Request JSON")
    print(json.dumps(json.loads(captured[0].content.decode("utf-8")), ensure_ascii=False, indent=2))
    print("\n# cURL")
    print(curl_for_request(captured[0]))
    print("\n# Mock response")
    print(json.dumps(response.model_dump(mode="json", exclude_none=True), ensure_ascii=False, indent=2))


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
