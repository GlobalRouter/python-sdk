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

## Chat 内容透传

`messages[].content[]` 支持 `video`、`video_url`、`input_audio`、`file`
以及上游自定义类型。通用 Chat 链路保留类型和扩展字段；上游模型是否支持由上游判断。
原生协议适配器无法转换的类型会明确报错。

```python
response = client.chat.send(
    model="gemini-3.8-flash",
    messages=[{"role": "user", "content": [
        {"type": "text", "text": "描述视频"},
        {"type": "video_url", "video_url": {"url": "https://example.com/video.mp4"}},
    ]}],
)
```

音频使用 `{"type": "input_audio", "input_audio": {"data": "<base64>", "format": "wav"}}`；
文件使用 `{"type": "file", "file": {"file_id": "<上游文件 ID>"}}` 或
`{"type": "file", "file": {"filename": "test.pdf", "file_data": "<data URL>"}}`。
文件 ID 必须属于实际接收请求的上游，不会自动上传或跨 provider 搬运。

## OpenRouter-Compatible Surface

The default high-level resources use GlobalRouter's `/api/v1/*` OpenRouter-compatible facade.

```python
client = GlobalRouter()

chat = client.chat.send(
    models=["qwen3-32b"],
    messages=[{"role": "user", "content": "Use the first available model"}],
    max_completion_tokens=1024,
    reasoning={"enabled": True, "exclude": True},
)

response = client.responses.create(
    model="qwen3.8-max",
    input="Explain the result briefly",
    max_output_tokens=1024,
    reasoning={"effort": "high", "summary": "auto"},
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

Use `max_completion_tokens` for Chat Completions and `max_output_tokens` for
Responses. `reasoning.enabled`, `reasoning.max_tokens`, and `reasoning.exclude`
are OpenRouter/GlobalRouter compatibility extensions; upstream support still
depends on the selected provider and model.

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
```

Available native resources:

- `client.tasks`
- `client.images`
- `client.audio`
- `client.three_d`

`client.images.generate(...)` 接收对象形式的 `provider` 时调用 `/api/v1/images`，
支持 `provider={"provider_id": "doubao"}` 和顶层 `watermark=False`。
字符串形式或省略 `provider` 时仍使用 `/v1/images/generations`。
同步及异步图片提交均只发送一次；结果未知时请核对原请求，避免重复计费。

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
