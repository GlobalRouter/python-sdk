"""Laid Dreamina 创建与查询；默认 MockTransport，不发起付费请求。

GLOBALROUTER_EXAMPLE_REAL=1 时才连接海外站点（会产生实际费用）。
GLOBALROUTER_ASSET_URI 可选：使用同租户、同 Laid 账号线路且 Active 的
asset://gr/<local_asset_id>；不能使用上游裸 asset:// ID。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from globalrouter import GlobalRouter  # noqa: E402


def main() -> None:
    payload = {
        "model": "dreamina-seedance-2-0-260128",  # 公共模型，不是上游 doubao ID
        "provider": {"provider_id": "laid"},  # Dreamina 必填，注意不是 lai
        "prompt": "A quiet city rooftop at sunset, slow cinematic push-in",
        "resolution": "720p",
        "duration": 5,
    }
    if uri := os.environ.get("GLOBALROUTER_ASSET_URI"):
        payload["input_references"] = [{"type": "image_url", "image_url": {"url": uri}}]

    real = os.environ.get("GLOBALROUTER_EXAMPLE_REAL") == "1"
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        if request.method == "POST":
            assert request.url.path == "/api/v1/videos"
            assert json.loads(request.content)["provider"] == {"provider_id": "laid"}
            return httpx.Response(202, json={"id": "job_mock_dreamina", "status": "pending"})
        assert request.method == "GET"
        assert request.url.path == "/api/v1/videos/job_mock_dreamina"
        assert not request.url.query  # 查询只需要平台任务 ID，不再传 provider
        return httpx.Response(200, json={"id": "job_mock_dreamina", "status": "completed"})

    client = GlobalRouter(
        api_key=os.environ["GLOBALROUTER_API_KEY"] if real else "sk-local-example",
        base_url=os.environ.get("GLOBALROUTER_BASE_URL", "https://api.globalrouter.ai"),
        transport=None if real else httpx.MockTransport(handler),
        max_retries=0,
    )
    try:
        created = client.videos.create(payload)
        print(created.model_dump_json(indent=2))
        # 只查询一次；真实生成通常仍在排队/执行，应稍后使用同一个平台 ID 查询。
        queried = client.videos.get(created.id)
        print(queried.model_dump_json(indent=2))
        if not real:
            assert len(captured) == 2
            print("Mock 创建/查询已通过；未调用上游。")
    finally:
        client.close()


if __name__ == "__main__":
    main()
