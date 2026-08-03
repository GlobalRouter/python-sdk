# GlobalRouter Python SDK

Python SDK for GlobalRouter, a multi-tenant AI model aggregation platform with OpenAI-compatible APIs, OpenRouter-style compatibility endpoints, routing, async multimodal tasks, billing, logs, and administration.

```bash
pip install globalrouter
```

```python
import os

from globalrouter import GlobalRouter

with GlobalRouter(api_key=os.environ["GLOBALROUTER_API_KEY"]) as client:
    response = client.chat.send(
        model="qwen3-32b",
        messages=[{"role": "user", "content": "Hello from GlobalRouter"}],
    )
    print(response.choices[0]["message"]["content"])
```

## OpenRouter-Compatible Surface

The default high-level resources use GlobalRouter's `/api/v1/*` OpenRouter-compatible facade.

```python
client = GlobalRouter()

chat = client.chat.send(
    models=["qwen3-32b"],
    messages=[{"role": "user", "content": "Use the first available model"}],
)

for chunk in client.chat.stream(
    model="qwen3-32b",
    messages=[{"role": "user", "content": "Stream this"}],
):
    print(chunk.choices)

models = client.models.list()
credits = client.credits.get()
providers = client.providers.list()
```

Available OpenRouter-compatible resources:

- `client.chat`
- `client.responses`
- `client.messages`
- `client.embeddings`
- `client.models`
- `client.credits`
- `client.generations`
- `client.keys`
- `client.providers`
- `client.videos`

## Native GlobalRouter Surface

Native resources use GlobalRouter's `/v1/*` APIs for tasks and multimodal generation.

```python
task = client.tasks.create(
    type="image_generation",
    model="seedream-image",
    input={"prompt": "a calm dashboard"},
)

for event in client.tasks.events(task.id):
    print(event)

image_task = client.images.create_task(
    model="jimeng_t2i_v31",
    prompt="a calm dashboard",
)
image_task = client.images.get_task(image_task.id)
```

Available native resources:

- `client.tasks`
- `client.images`
  - `client.images.create_task`
  - `client.images.get_task`
- `client.audio`
  - `client.audio.seed_audio(...)`
  - `await client.audio.seed_audio_async(...)`
- `client.three_d`

## Doubao SeedAudio

```python
response = client.audio.seed_audio(
    {
        "model": "doubao-seed-audio-1-0",
        "text_prompt": "Use @音频1 as a style reference for a calm piano passage",
        "references": [{"audio_url": "https://example.com/reference.mp3"}],
        "audio_config": {"format": "mp3", "enable_subtitle": True},
        "watermark": {"aigc_watermark": False},
    }
)
print(response.url, response.original_duration)
```

`seed_audio` and `seed_audio_async` send `POST /doubao/api/v3/tts/create`.
The request accepts any `Mapping`, so new official SeedAudio fields can be
used without waiting for an SDK release. Configure only the GlobalRouter API
key; do not send a Volcengine `X-Api-Key`.

## Async

Every resource includes async methods with the `_async` suffix.

```python
from globalrouter import GlobalRouter

async with GlobalRouter() as client:
    response = await client.chat.send_async(
        model="qwen3-32b",
        messages=[{"role": "user", "content": "Hello async"}],
    )
```

## Configuration

```python
client = GlobalRouter(
    api_key="sk-...",
    base_url="https://api.globalrouter.com",
    timeout_seconds=30,
    max_retries=2,
)
```

If `api_key` is omitted, the SDK reads `GLOBALROUTER_API_KEY`.

## Errors

```python
from globalrouter import GlobalRouterError

try:
    client.models.list()
except GlobalRouterError as exc:
    print(exc.status_code, exc.code, exc.error_type, exc.request_id)
```

The SDK normalizes both GlobalRouter native error envelopes and OpenRouter-compatible error envelopes into `GlobalRouterError`.

## Webhook Signatures

```python
ok = GlobalRouter.verify_webhook_signature(
    secret="whsec_...",
    payload=b'{"event":"task.succeeded"}',
    signature="t=1778413678,v1=...",
)
```
