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


REQUEST_BODY: dict[str, Any] = {
    "model": "doubao-seed-audio-1-0",
    "text_prompt": "Use @音频1 as a style reference for a calm piano passage",
    "references": [{"audio_url": "https://example.com/reference.mp3"}],
    "audio_config": {"format": "mp3", "enable_subtitle": True},
    "watermark": {"aigc_watermark": False},
}


def main() -> None:
    real = os.environ.get("GLOBALROUTER_EXAMPLE_REAL") == "1"
    if real:
        client = GlobalRouter(
            api_key=os.environ["GLOBALROUTER_API_KEY"],
            base_url=os.environ.get(
                "GLOBALROUTER_BASE_URL",
                "https://api.globalrouter.com",
            ),
        )
    else:
        client = GlobalRouter(
            api_key=os.environ.get("GLOBALROUTER_API_KEY", "sk-local-example"),
            base_url="http://127.0.0.1:8000",
            transport=httpx.MockTransport(mock_response),
            max_retries=0,
        )

    try:
        response = client.audio.seed_audio(
            real_request_body() if real else REQUEST_BODY
        )
        print(
            json.dumps(
                response.model_dump(mode="json", exclude_none=True),
                ensure_ascii=False,
                indent=2,
            )
        )
    finally:
        client.close()


def real_request_body() -> dict[str, Any]:
    return {
        "model": "doubao-seed-audio-1-0",
        "text_prompt": (
            "Generate a calm piano passage with a soft, relaxing atmosphere."
        ),
        "audio_config": {"format": "mp3", "enable_subtitle": True},
        "watermark": {"aigc_watermark": False},
    }


def mock_response(request: httpx.Request) -> httpx.Response:
    print(f"# {request.method} {request.url.path}")
    print(json.dumps(json.loads(request.content), ensure_ascii=False, indent=2))
    return httpx.Response(
        200,
        json={
            "audio": "base64-audio",
            "duration": 12.0,
            "original_duration": 12.0,
            "url": "https://example.test/seed-audio.mp3",
            "subtitle": {
                "text": "A calm piano passage",
                "sentences": [
                    {
                        "text": "A calm piano passage",
                        "start_time": 0,
                        "end_time": 12000,
                        "words": [],
                    }
                ],
            },
        },
        request=request,
    )


if __name__ == "__main__":
    main()
