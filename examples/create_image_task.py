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
    "model": "jimeng_t2i_v31",
    "prompt": "生成 4 张电商商品图，白底，高级感",
    "input_references": [
        {
            "type": "image_url",
            "image_url": {"url": "https://example.com/reference.png"},
        }
    ],
    "n": 4,
    "size": "1024x1024",
    "provider": {
        "provider_id": "doubao_gr",
        "options": {
            "doubao_gr": {
                "watermark": False,
                "force_single": False,
            },
        },
    },
    "metadata": {
        "client_request_id": "client-001",
    },
}


def main() -> None:
    idempotency_key = "client-image-task-001"
    if os.environ.get("GLOBALROUTER_EXAMPLE_REAL") == "1":
        client = GlobalRouter(
            api_key=os.environ["GLOBALROUTER_API_KEY"],
            base_url=os.environ.get("GLOBALROUTER_BASE_URL", "https://api.globalrouter.com"),
        )
        try:
            response = client.images.create_task(REQUEST_BODY, idempotency_key=idempotency_key)
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
                "id": "imgtask_xxx",
                "object": "image.task",
                "status": "queued",
                "model": "jimeng_t2i_v31",
                "provider": "doubao_gr",
                "polling_url": "/api/v1/image-tasks/imgtask_xxx",
                "created_at": 1770000000,
                "updated_at": 1770000000,
                "data": [],
                "usage": {"billing_status": "unreserved"},
                "metadata": {"client_request_id": "client-001"},
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
        response = client.images.create_task(REQUEST_BODY, idempotency_key=idempotency_key)
    finally:
        client.close()

    print("# POST /api/v1/image-tasks")
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
