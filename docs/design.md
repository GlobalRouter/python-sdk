# GlobalRouter Python SDK V1 Design

## Goals

The Python SDK provides a first-party, typed client for GlobalRouter while keeping the public developer experience close to OpenRouter's Python SDK style: a single `GlobalRouter` client, resource namespaces, sync and async calls, streaming iterators, and flexible request dictionaries for provider-specific fields.

V1 is intentionally handwritten. The backend OpenAPI schema remains useful for validation and future generation, but the first SDK prioritizes stable ergonomics and clear naming over generated breadth.

## Public API

```python
from globalrouter import GlobalRouter, GlobalRouterError

with GlobalRouter() as client:
    response = client.chat.send(
        model="qwen3-32b",
        messages=[{"role": "user", "content": "hello"}],
    )
```

The client exposes two groups:

- OpenRouter-compatible `/api/v1/*`: `chat`, `responses`, `messages`, `embeddings`, `models`, `credits`, `generations`, `keys`, `providers`, `videos`.
- Native GlobalRouter `/v1/*`: `tasks`, `images`, `audio`, `three_d`.

Every resource has sync methods and async variants ending in `_async`. Streaming chat and task events are exposed as iterators.

## Request and Response Shape

Requests accept either a mapping as the first positional argument or keyword fields. This keeps examples concise while allowing new API fields to pass through before the SDK adds first-class typed parameters.

Responses use small Pydantic v2 models with `extra="allow"`. The SDK models stable top-level fields such as `id`, `data`, `choices`, `usage`, and `status`, while preserving unknown fields from the API.

## Transport

The SDK uses `httpx.Client` and `httpx.AsyncClient` internally.

Defaults:

- `base_url`: `https://api.globalrouter.ai`
- `timeout_seconds`: `30`
- `max_retries`: `2`
- `api_key`: explicit argument or `GLOBALROUTER_API_KEY`

Retries apply to transport errors and HTTP `5xx` responses. Client and auth errors are never retried.

## Errors

Both API envelopes normalize into `GlobalRouterError`:

- Native GlobalRouter: `error.code`, `error.message`, `error.type`, `error.request_id`
- OpenRouter-compatible: `error.message`, HTTP numeric `error.code`, `error.metadata.router_code`, `error.metadata.type`, `error.metadata.request_id`

`GlobalRouterError` stores `status_code`, `code`, `message`, `error_type`, `request_id`, the original object-valued `error.metadata`, and the raw `httpx.Response` when available.

## Streaming

SSE streams parse `data: ...` frames and stop on `[DONE]`. JSON frames are validated into `ChatCompletionChunk` for chat streams and `APIResponse` for task events. Stream error frames are raised as `GlobalRouterError`.

## Versioning

V1 starts at package version `0.1.0`. The SDK does not publish to PyPI in this implementation pass, but package metadata is ready for a later release.
