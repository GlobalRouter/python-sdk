from __future__ import annotations

import json
import os
import shlex
import sys
from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from globalrouter import GlobalRouter  # noqa: E402


class Capture:
    def __init__(self) -> None:
        self.requests: list[httpx.Request] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        payload = _request_json(request)
        return httpx.Response(
            200,
            json={
                "id": "example_mock",
                "object": "example.response",
                "status": "mocked",
                "model": payload.get("model") if isinstance(payload, dict) else None,
                "data": {"path": request.url.path},
            },
            request=request,
        )


def example_client(capture: Capture) -> GlobalRouter:
    return GlobalRouter(
        api_key=os.environ.get("GLOBALROUTER_API_KEY", "sk-local-example"),
        base_url=os.environ.get("GLOBALROUTER_BASE_URL", "http://127.0.0.1:8000"),
        transport=httpx.MockTransport(capture.handler),
        max_retries=0,
    )


def run_sdk_examples(
    title: str,
    examples: Mapping[str, dict[str, Any]],
    call: Callable[[GlobalRouter, dict[str, Any]], Any],
) -> None:
    capture = Capture()
    client = example_client(capture)
    try:
        for name, payload in _selected_mapping(examples):
            before = len(capture.requests)
            response = call(client, payload)
            _print_example(title, name, capture.requests[before], response)
    finally:
        client.close()


def run_raw_json_examples(
    title: str,
    method: str,
    path: str,
    examples: Mapping[str, dict[str, Any]],
) -> None:
    capture = Capture()
    client = example_client(capture)
    try:
        for name, payload in _selected_mapping(examples):
            before = len(capture.requests)
            response = client.request(method, path, json_body=payload)
            _print_example(title, name, capture.requests[before], response)
    finally:
        client.close()


def run_raw_path_examples(title: str, examples: Sequence[Mapping[str, Any]]) -> None:
    capture = Capture()
    client = example_client(capture)
    try:
        for item in _selected_sequence(examples):
            before = len(capture.requests)
            response = client.request(
                str(item["method"]),
                str(item["path"]),
                json_body=item.get("json_body"),
            )
            _print_example(title, str(item["name"]), capture.requests[before], response)
    finally:
        client.close()


def _selected_mapping(examples: Mapping[str, dict[str, Any]]) -> Iterable[tuple[str, dict[str, Any]]]:
    selected = os.environ.get("EXAMPLE_NAME")
    if selected:
        if selected not in examples:
            names = ", ".join(examples)
            raise SystemExit(f"unknown EXAMPLE_NAME={selected!r}; available: {names}")
        return [(selected, examples[selected])]
    return examples.items()


def _selected_sequence(examples: Sequence[Mapping[str, Any]]) -> Iterable[Mapping[str, Any]]:
    selected = os.environ.get("EXAMPLE_NAME")
    if selected:
        for item in examples:
            if item["name"] == selected:
                return [item]
        names = ", ".join(str(item["name"]) for item in examples)
        raise SystemExit(f"unknown EXAMPLE_NAME={selected!r}; available: {names}")
    return examples


def _print_example(title: str, name: str, request: httpx.Request, response: Any) -> None:
    print(f"\n## {title}: {name}")
    print("\n# Request JSON")
    print(json.dumps(_request_json(request), ensure_ascii=False, indent=2))
    print("\n# cURL")
    print(curl_for_request(request))
    print("\n# Mock response")
    print(json.dumps(_response_json(response), ensure_ascii=False, indent=2))


def _request_json(request: httpx.Request) -> Any:
    if not request.content:
        return None
    return json.loads(request.content.decode("utf-8"))


def _response_json(response: Any) -> Any:
    if isinstance(response, httpx.Response):
        return response.json()
    if hasattr(response, "model_dump"):
        return response.model_dump(mode="json")
    return response


def curl_for_request(request: httpx.Request) -> str:
    lines = [f"curl -X {request.method} {shlex.quote(str(request.url))}"]
    for key, value in request.headers.items():
        if key.lower() in {"accept-encoding", "connection", "host", "content-length"}:
            continue
        if key.lower() == "authorization":
            value = "Bearer ${GLOBALROUTER_API_KEY}"
        lines.append(f"  -H {shlex.quote(f'{key}: {value}')}")
    if request.content:
        body = json.dumps(_request_json(request), ensure_ascii=False, indent=2)
        lines.append(f"  --data-raw {shlex.quote(body)}")
    return " \\\n".join(lines)
