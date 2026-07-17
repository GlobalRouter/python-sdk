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
```

## Files

- `create_chat_completion.py` -> `POST /api/v1/chat/completions`, via `client.chat.send(...)`.
- `create_images.py` -> `POST /api/v1/images`, via `client.images.generate(...)`.
- `create_image_task.py` -> `POST /api/v1/image-tasks`, via `client.images.create_task(...)`.
- `create_video.py` -> `POST /api/v1/videos`, via `client.videos.create(...)`.

The examples intentionally include only the public `/api/v1` request shapes shown in the GlobalRouter docs.
