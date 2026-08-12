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

### Image generation

`client.images` uses the `/api/v1/images` contract. Image-generation parameters are
sent unchanged, including provider selection and reference images.

```python
reference_url = "https://assets.example.test/reference.jpg"

image = client.images.generate(
    model="gpt-image-2",
    prompt="Edit the character outfit while preserving facial features.",
    n=1,
    size="1792x1024",
    provider={"provider_id": "ghyz"},
    input_references=[
        {
            "type": "image_url",
            "image_url": {"url": reference_url},
        }
    ],
)
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
- `client.images`

## Native GlobalRouter Surface

Native resources use GlobalRouter's `/v1/*` APIs for tasks and resource-specific
multimodal generation.

```python
task = client.tasks.create(
    type="image_generation",
    model="seedream-image",
    input={"prompt": "a calm dashboard"},
)

for event in client.tasks.events(task.id):
    print(event)
```

Available native resources:

- `client.tasks`
- `client.audio`
- `client.three_d`

`tasks.create`, `tasks.create_batch`, `tasks.retry`, `videos.create`, and
`three_d.generate` are sent once and are never automatically retried by the SDK.
If their outcome is unknown, query the task first; any caller-initiated retry must
reuse the same `idempotency_key` where the API supports it.

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
    base_url="https://api.globalrouter.ai",
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
    print(exc.status_code, exc.code, exc.error_type, exc.request_id, exc.metadata)
```

The SDK normalizes both GlobalRouter native error envelopes and OpenRouter-compatible error envelopes into `GlobalRouterError`.
For OpenRouter-compatible errors, `exc.metadata` preserves the original `error.metadata` object.

## Webhook Signatures

```python
ok = GlobalRouter.verify_webhook_signature(
    secret="whsec_...",
    payload=b'{"event":"task.succeeded"}',
    signature="t=1778413678,v1=...",
)
```
