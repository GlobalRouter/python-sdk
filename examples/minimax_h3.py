"""MiniMax-H3: GR 原生接口与 OpenRouter 视频接口的创建、查询示例。"""

import json
import os
import urllib.request

BASE_URL = os.environ.get("GLOBALROUTER_BASE_URL", "https://api.globalrouter.com").rstrip("/")
API_KEY = os.environ["GLOBALROUTER_API_KEY"]


def call(path: str, body: dict | None = None) -> dict:
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        BASE_URL + path, data=data,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        method="POST" if body is not None else "GET",
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def main() -> None:
    native = call("/v2/video_generation", {
        "model": "MiniMax-H3",
        "content": [{"type": "text", "text": "黄昏海边，镜头缓缓推进"}],
        "resolution": "768P", "duration": 5, "ratio": "16:9",
    })
    print("原生创建", native)
    print("原生查询", call(f"/v2/query/video_generation/{native['task_id']}"))

    compatible = call("/api/v1/videos", {
        "model": "MiniMax-H3", "prompt": "黄昏海边，镜头缓缓推进",
        "resolution": "2K", "duration": 5, "aspect_ratio": "16:9",
    })
    print("OpenRouter 创建", compatible)
    print("OpenRouter 查询", call(f"/api/v1/videos/{compatible['id']}"))
    # 异步任务需持续轮询直到终态；成功前不会有视频 URL。


if __name__ == "__main__":
    main()