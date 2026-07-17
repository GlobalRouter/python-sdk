# GlobalRouter Python SDK examples

These examples adapt request payloads from `../../llm_gateway/docs` into calls through the Python SDK.
They use `httpx.MockTransport` by default, so running them prints the SDK request and a mock response without calling GlobalRouter.

Run from `gr_sdk_demo/py_sdk`:

```bash
python examples/images_generations.py
EXAMPLE_NAME=text2image python examples/seedream_image.py
GLOBALROUTER_BASE_URL=http://127.0.0.1:8000 python examples/std_video_tasks.py
```

## Files

- `images_generations.py` -> `images_generations.yaml`, via `client.images.generate(...)`.
- `seedance_tasks.py` -> `jimeng.yaml` `/v1/tasks`, via `client.tasks.create(...)`.
- `jimeng_legacy.py` -> `jimeng.yaml` `/v1/jimeng/create` and `/v1/jimeng/query`, via `client.request(...)`.
- `seedream_image.py` -> `seedream.yaml`, via `client.request(...)`.
- `wan_image.py` -> `wan.yaml`, via `client.request(...)`.
- `happyhorse_video.py` -> `happyhorse.yaml`, via `client.request(...)`.
- `admin_price_rules.py` -> `price-rules-admin.yaml`, mock-only admin example.

Not converted here: docs without concrete JSON request examples, the multipart upload doc, invalid `models-admin.yaml`, `ali_avatar.yaml` because GlobalRouter itself does not expose avatar as an SDK capability, `claude.yaml`, `gemini.yaml`, `std_tasks.yaml`, and `sync_password.yaml` because it contains password-sync token-like sample data rather than an SDK-facing API example.
