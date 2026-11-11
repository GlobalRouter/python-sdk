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

### Messages

`client.messages.create(...)` and `client.messages.create_async(...)` use
`/api/v1/messages`. Request
objects are forwarded unchanged, so fields used by database-configured generic
Messages models are preserved. Explicit protocol headers are keyword-only
arguments and never enter the JSON body:

```python
response = client.messages.create(
    {
        "model": os.environ["GLOBALROUTER_MESSAGES_MODEL"],
        "messages": [{"role": "user", "content": "Hello"}],
        "max_completion_tokens": 128,
        "vendor_extension": {"enabled": True},
    },
    anthropic_version="2025-01-01",
    anthropic_beta="messages-vendor-beta",
)
```

Unknown fields are forwarded only where the server-side model configuration and
upstream provider permit them; legacy/custom models retain their existing
validation and conversion behavior. The runnable example is
`examples/create_messages.py`.

### Messages / Responses 流与回滚兼容

`messages.create`、`responses.create` 在 `stream=true` 时返回同步迭代器；
`await create_async(...)` 返回异步迭代器。缺省、`false` 或 `null` 返回
`APIResponse`。generic Messages 保留全部 content 块，Responses 保留完整
output 与事件，请按 `type` 遍历，避免固定读取第一项文本。

```python
from contextlib import closing

with closing(client.messages.create(
    model=os.environ["GLOBALROUTER_MESSAGES_MODEL"],
    messages=[{"role": "user", "content": "Hello"}],
    stream=True,
)) as events:
    for event in events:
        print(event.model_dump(exclude_unset=True))
```

异步调用使用 `contextlib.aclosing` 包裹 `await client.responses.create_async(...)`
返回的流；提前退出时应关闭迭代器。图片 Responses 在生成完成后输出
`response.created` 和 `response.completed`，不提供增量图片。
新版 SDK 根据 Content-Type 读取 SSE；回滚服务返回普通 JSON 时，
同一迭代器完整产出一次 JSON 对象。此兼容不会为获取另一种格式再发送生成请求。
客户端既有的 HTTP 故障重试设置仍独立生效；真实验收应关闭或记录这些重试。

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

`client.images.generate(...)` 接收对象形式的 `provider` 时调用 `/api/v1/images`，
支持 `provider={"provider_id": "doubao"}` 和顶层 `watermark=False`。
字符串形式或省略 `provider` 时仍使用 `/v1/images/generations`。
同步及异步图片提交均只发送一次；结果未知时请核对原请求，避免重复计费。

`tasks.create`, `tasks.create_batch`, `tasks.retry`, `videos.create`,
`videos.generate`, and
`three_d.generate` are sent once and are never automatically retried by the SDK.
If their outcome is unknown, query the task first; any caller-initiated retry must
reuse the same `idempotency_key` where the API supports it.

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
key; do not send a Volcengine `X-Api-Key`. GlobalRouter selects the dedicated
`doubao_audio` provider and its upstream credential on the server, so the SDK
does not send a `provider` field.

`client.videos.generate(...)` posts to `/v1/videos/generations`.
`client.videos.generate(...)` and the OpenRouter-compatible
`client.videos.create(...)` at `/api/v1/videos` both support Kling 4.0 video
generation. The runnable `examples/kling_video.py` example reads
`GLOBALROUTER_KLING_MODEL` and performs one create request followed by one task
lookup.

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
