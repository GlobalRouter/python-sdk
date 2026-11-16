# GlobalRouter Python SDK examples

These examples follow the public GlobalRouter docs at:

```text
https://test-global-router.xiaoniuds.com/zh-CN/docs
```

They use `httpx.MockTransport` by default, so running them prints the SDK request and a mock response without calling GlobalRouter.

Run from `gr_sdk_demo/py_sdk`:

```bash
python examples/create_chat_completion.py
python examples/create_images.py
python examples/create_image_task.py
python examples/create_video.py
python examples/create_ali_video_data_inspection.py
python examples/create_seed_audio.py
```

## Files

- `create_chat_completion.py` -> `POST /api/v1/chat/completions`, via `client.chat.send(...)`.
- `create_images.py` -> `POST /api/v1/images`, via `client.images.generate(...)`.
- `create_image_task.py` -> `POST /api/v1/image-tasks`, via `client.images.create_task(...)`.
- `create_video.py` -> `POST /api/v1/videos`, via `client.videos.create(...)`.
- `create_ali_video_data_inspection.py` -> `POST /api/v1/videos`, showing the
  `provider.options.ali.dataInspection` body and
  `X-DashScope-DataInspection` header compatibility input.
- `create_seed_audio.py` -> `POST /doubao/api/v3/tts/create`, via `client.audio.seed_audio(...)`.

## Ali video data inspection

The body form uses the existing arbitrary mapping support:

```python
client.videos.create(
    {
        "model": "wan3.0-video",
        "prompt": "A quiet city rooftop at sunset",
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
)
```

The header compatibility form uses the existing one-shot request method so the
SDK does not add retries to the paid video POST:

```python
client.request_once(
    "POST",
    "/api/v1/videos",
    json_body={
        "model": "wan3.0-video",
        "prompt": "A quiet city rooftop at sunset",
    },
    headers={
        "X-DashScope-DataInspection": '{"input":"disable","output":"disable"}',
    },
)
```

`ALI_DATA_INSPECTION_MODE=header` runs the header example. Real calls remain
disabled unless `GLOBALROUTER_EXAMPLE_REAL=1` is set explicitly.

SeedAudio provider selection is server-side: the SDK sends only the
GlobalRouter Bearer key and official request fields, while GlobalRouter routes
the request through its dedicated `doubao_audio` provider.

The examples intentionally include only the public `/api/v1` request shapes shown in the GlobalRouter docs.
