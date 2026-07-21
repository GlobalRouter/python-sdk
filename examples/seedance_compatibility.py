from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from globalrouter import GlobalRouter  # noqa: E402, I001


MODEL = "doubao-seedance-2-0-260128"


def create_compatibility_resources(client: GlobalRouter) -> dict[str, Any]:
    video = client.seedance.create_video_generation(
        model=MODEL,
        content=[{"type": "text", "text": "A quiet product demo"}],
    )
    group = client.seedance.create_asset_group(
        model=MODEL,
        Name="product references",
        Description="assets used by this example",
    )
    asset = client.seedance.create_asset(
        model=MODEL,
        Name="product reference",
        URL="https://cdn.example.test/reference.png",
        AssetType="Image",
        GroupId=group.data["id"],
    )
    return {"video": video.data, "asset_group": group.data, "asset": asset.data}


def mock_handler(captured: list[httpx.Request]) -> Any:
    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        if request.method == "POST" and request.url.path == "/v1/video/generations":
            payload = {"id": "task_example_123", "status": "queued"}
        elif request.method == "POST" and request.url.path == "/api/v3/assets/groups":
            payload = {"id": "group_example_123"}
        elif request.method == "POST" and request.url.path == "/api/v3/assets":
            payload = {
                "id": "asset_example_123",
                "url": "https://cdn.example.test/reference.png",
            }
        else:
            raise AssertionError(f"Unexpected mock request: {request.method} {request.url.path}")
        return httpx.Response(200, json={"code": "success", "message": "", "data": payload})

    return handler


def main() -> None:
    if os.environ.get("GLOBALROUTER_EXAMPLE_REAL") == "1":
        client = GlobalRouter(
            api_key=os.environ["GLOBALROUTER_API_KEY"],
            base_url=os.environ.get("GLOBALROUTER_BASE_URL", "https://api.globalrouter.com"),
        )
        captured: list[httpx.Request] | None = None
    else:
        captured = []
        client = GlobalRouter(
            api_key=os.environ.get("GLOBALROUTER_API_KEY", "sk-local-example"),
            base_url=os.environ.get("GLOBALROUTER_BASE_URL", "http://127.0.0.1:8000"),
            transport=httpx.MockTransport(mock_handler(captured)),
            max_retries=0,
        )

    try:
        result = create_compatibility_resources(client)
    finally:
        client.close()

    if captured is not None:
        print("# Mock request JSON (authorization headers are not printed)")
        for request in captured:
            print(f"{request.method} {request.url.path}")
            print(json.dumps(json.loads(request.content), ensure_ascii=False, indent=2))

    print("# Compatibility responses")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
