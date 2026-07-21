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
python examples/seedance_compatibility.py
```

## Files

- `create_chat_completion.py` -> `POST /api/v1/chat/completions`, via `client.chat.send(...)`.
- `create_images.py` -> `POST /api/v1/images`, via `client.images.generate(...)`.
- `create_image_task.py` -> `POST /api/v1/image-tasks`, via `client.images.create_task(...)`.
- `create_video.py` -> `POST /api/v1/videos`, via `client.videos.create(...)`.
- `seedance_compatibility.py` -> compatibility video creation and asset registration via
  `client.seedance.create_video_generation(...)` and `client.seedance.create_asset(...)`. It uses
  `doubao-seedance-2-0-260128` and preserves the case-sensitive `Name`, `URL`, and `AssetType`
  asset fields.

The standard examples intentionally include only the public `/api/v1` request shapes shown in the
GlobalRouter docs. The compatibility example demonstrates its separate public compatibility methods.
