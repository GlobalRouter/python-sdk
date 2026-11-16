from __future__ import annotations

import json
import os
from typing import Any

import httpx

from globalrouter import GlobalRouter

BODY_REQUEST: dict[str, Any] = {
    "model": "wan3.0-video",
    "prompt": "A quiet city rooftop at sunset, slow cinematic push-in",
    "provider": {
        "provider_id": "ali",
        "options": {
            "ali": {
                "dataInspection": {
                    "input": "disable",
                    "output": "disable",
                }
            }
        },
    },
}

HEADER_REQUEST: dict[str, Any] = {
    "model": "wan3.0-video",
    "prompt": "A quiet city rooftop at sunset, slow cinematic push-in",
}

DATA_INSPECTION_HEADER = "X-DashScope-DataInspection"
DATA_INSPECTION_HEADER_VALUE = '{"input":"disable","output":"disable"}'


def main() -> None:
    mode = os.environ.get("ALI_DATA_INSPECTION_MODE", "body").strip().lower()
    if mode not in {"body", "header"}:
        raise SystemExit("ALI_DATA_INSPECTION_MODE must be body or header")

    real = os.environ.get("GLOBALROUTER_EXAMPLE_REAL") == "1"
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            202,
            json={
                "id": "job_ali_data_inspection",
                "polling_url": "/api/v1/videos/job_ali_data_inspection",
                "status": "pending",
            },
            request=request,
        )

    client = GlobalRouter(
        api_key=os.environ.get("GLOBALROUTER_API_KEY", "sk-local-example"),
        base_url=os.environ.get(
            "GLOBALROUTER_BASE_URL",
            "https://api.globalrouter.com",
        ),
        transport=None if real else httpx.MockTransport(handler),
        max_retries=0,
    )
    try:
        if mode == "body":
            response = client.videos.create(BODY_REQUEST)
        else:
            response = client.request_once(
                "POST",
                "/api/v1/videos",
                json_body=HEADER_REQUEST,
                headers={DATA_INSPECTION_HEADER: DATA_INSPECTION_HEADER_VALUE},
            )
    finally:
        client.close()

    if real:
        payload = (
            response.model_dump(mode="json", exclude_none=True)
            if hasattr(response, "model_dump")
            else response.json()
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    request = captured[0]
    print(f"# POST {request.url.path}")
    print(f"# mode: {mode}")
    if mode == "body":
        print("# request body")
        print(json.dumps(json.loads(request.content), indent=2))
    else:
        print(f"# {DATA_INSPECTION_HEADER}: {request.headers[DATA_INSPECTION_HEADER]}")
        print("# request body")
        print(json.dumps(json.loads(request.content), indent=2))


if __name__ == "__main__":
    main()
