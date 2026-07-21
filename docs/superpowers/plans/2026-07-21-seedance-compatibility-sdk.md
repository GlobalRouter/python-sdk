# Seedance Compatibility Python SDK Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expose all five Seedance video and asset compatibility routes through a documented, synchronous and asynchronous `client.seedance` Python SDK resource.

**Architecture:** Add one focused `SeedanceResource` next to the existing handwritten resource namespaces. It delegates to the established authenticated HTTP transport and returns `APIResponse`, preserving the compatibility envelope and unknown fields. The resource is initialized by `GlobalRouter` and does not change the existing `videos` or `tasks` APIs.

**Tech Stack:** Python 3.9+, httpx, Pydantic v2, pytest, pytest-asyncio, Ruff, mypy.

---

### Task 1: Specify synchronous compatibility calls with a failing transport test

**Files:**
- Modify: `tests/test_client.py`
- Modify: `src/globalrouter/_resources.py`
- Modify: `src/globalrouter/_client.py`

- [ ] **Step 1: Write the failing synchronous test**

Add a focused `test_seedance_compatibility_resource_uses_documented_paths_and_casing` using `httpx.MockTransport`. The handler must assert bearer authentication and dispatch exactly these calls:

```python
assert request.method == "POST"
assert request.url.path == "/v1/video/generations"
assert request.headers["idempotency-key"] == "seedance-idem-1"
assert "idempotency_key" not in json.loads(request.content)

assert request.url.path == "/api/v3/assets/groups"
assert json.loads(request.content)["Name"] == "product references"
assert json.loads(request.content)["Description"] == "launch campaign"

assert request.url.path == "/api/v3/assets"
payload = json.loads(request.content)
assert payload["URL"] == "https://cdn.example.test/reference.png"
assert payload["AssetType"] == "Image"
assert payload["GroupId"] == "group_gr_123"
assert "asset_type" not in payload

assert request.url.path == "/api/v3/assets/get"
assert json.loads(request.content)["Id"] == "asset_gr_123"
```

Invoke `client.seedance.create_video_generation`, `get_video_generation`, `create_asset_group`, `create_asset`, and `get_asset`. Return `{"code": "success", "data": ...}` responses and assert that each `APIResponse.data` value preserves the expected task, group, asset, and signed URL fields.

- [ ] **Step 2: Run the new test and verify RED**

Run: `pytest tests/test_client.py::test_seedance_compatibility_resource_uses_documented_paths_and_casing -q`

Expected: FAIL with `AttributeError` because `GlobalRouter` does not yet expose `seedance`.

- [ ] **Step 3: Add the minimal resource implementation**

In `src/globalrouter/_resources.py`, add `SeedanceResource(BaseResource)` with these methods:

```python
def create_video_generation(self, request=None, **params):
    return self._client.request_model(
        "POST", "/v1/video/generations", APIResponse,
        json_body=self._payload_without_params(request, params, {"idempotency_key"}),
        headers=_idempotency_header(params.get("idempotency_key")),
    )

def get_video_generation(self, task_id):
    return self._client.request_model(
        "GET", f"/v1/video/generations/{task_id}", APIResponse,
    )

def create_asset_group(self, request=None, **params):
    return self._client.request_model(
        "POST", "/api/v3/assets/groups", APIResponse,
        json_body=self._payload(request, params),
    )
```

Implement `create_asset` and `get_asset` with the analogous `POST /api/v3/assets` and `POST /api/v3/assets/get` calls. Import `SeedanceResource` in `src/globalrouter/_client.py` and initialize `self.seedance = SeedanceResource(self)` beside the existing resource fields.

- [ ] **Step 4: Run the focused test and verify GREEN**

Run: `pytest tests/test_client.py::test_seedance_compatibility_resource_uses_documented_paths_and_casing -q`

Expected: PASS.

- [ ] **Step 5: Commit the tested resource**

```bash
git add src/globalrouter/_client.py src/globalrouter/_resources.py tests/test_client.py
git commit -m "feat: add Seedance compatibility resource"
```

### Task 2: Add and test asynchronous compatibility calls

**Files:**
- Modify: `src/globalrouter/_resources.py`
- Modify: `tests/test_client.py`

- [ ] **Step 1: Write the failing async test**

Add `@pytest.mark.asyncio` test `test_seedance_compatibility_resource_async_methods`. Its async mock handler must return responses for all five paths. Call:

```python
await client.seedance.create_video_generation_async(
    model="doubao-seedance-2-0-260128",
    content=[{"type": "text", "text": "a quiet product demo"}],
    idempotency_key="seedance-async-1",
)
await client.seedance.get_video_generation_async("task_gr_async")
await client.seedance.create_asset_group_async(
    model="doubao-seedance-2-0-260128", Name="product references"
)
await client.seedance.create_asset_async(
    model="doubao-seedance-2-0-260128",
    URL="https://cdn.example.test/reference.png",
    AssetType="Image",
)
await client.seedance.get_asset_async(
    model="doubao-seedance-2-0-260128", Id="asset_gr_async"
)
```

Assert the async video-create request sends `Idempotency-Key` and excludes `idempotency_key` from JSON, while the two asset payloads retain their Pascal-case keys.

- [ ] **Step 2: Run the new test and verify RED**

Run: `pytest tests/test_client.py::test_seedance_compatibility_resource_async_methods -q`

Expected: FAIL because the `_async` resource methods do not exist.

- [ ] **Step 3: Add minimal async methods**

Add `_async` counterparts to every `SeedanceResource` operation, all using `request_model_async`. For video creation, preserve the same excluded `idempotency_key` payload and header behavior:

```python
return await self._client.request_model_async(
    "POST", "/v1/video/generations", APIResponse,
    json_body=self._payload_without_params(request, params, {"idempotency_key"}),
    headers=_idempotency_header(params.get("idempotency_key")),
)
```

- [ ] **Step 4: Run focused sync and async tests and verify GREEN**

Run: `pytest tests/test_client.py -q`

Expected: PASS with all client tests green.

- [ ] **Step 5: Commit the async interface**

```bash
git add src/globalrouter/_resources.py tests/test_client.py
git commit -m "feat: add async Seedance compatibility methods"
```

### Task 3: Document the additional SDK entry and validate packaging

**Files:**
- Modify: `README.md`
- Create: `examples/seedance_compatibility.py`
- Modify: `examples/README.md`
- Test: `tests/test_client.py`

- [ ] **Step 1: Write the failing documentation assertions**

Add a small test that reads `README.md` and `examples/seedance_compatibility.py` and asserts both contain `client.seedance`, `create_video_generation`, `create_asset`, and `AssetType`. Assert neither file contains the upstream provider name nor real-person verification terminology.

- [ ] **Step 2: Run the documentation test and verify RED**

Run: `pytest tests/test_client.py -q`

Expected: FAIL because the new example and README section do not exist.

- [ ] **Step 3: Add README and mock-safe example**

Document `client.seedance` under the native/additional API section. Create `examples/seedance_compatibility.py` using `httpx.MockTransport` by default and an explicit `GLOBALROUTER_EXAMPLE_REAL=1` opt-in for real calls. Show video creation plus asset creation with exact `URL` and `AssetType` keys. Add the example to `examples/README.md`.

- [ ] **Step 4: Run full SDK validation**

Run:

```bash
pytest -q
ruff check .
mypy src
python -m build
git diff --check
```

Expected: every command exits 0.

- [ ] **Step 5: Commit documentation and checks**

```bash
git add README.md examples/seedance_compatibility.py examples/README.md tests/test_client.py
git commit -m "docs: add Seedance compatibility example"
```

### Task 4: Publish the SDK PR and connect the dependency

**Files:**
- Modify: none (GitHub metadata only)

- [ ] **Step 1: Re-sync branch and verify clean state**

Run:

```bash
git fetch origin
git rebase origin/main
pytest -q
ruff check .
mypy src
python -m build
git status --short --branch
```

Expected: branch is based on current `origin/main`, all checks pass, and no uncommitted changes remain.

- [ ] **Step 2: Push and create a draft PR**

Run:

```bash
git push -u origin codex/seedance-python-sdk
gh pr create --base main --head codex/seedance-python-sdk --draft \
  --title "feat: add Seedance compatibility Python SDK" \
  --body "Adds client.seedance for the documented video and asset compatibility routes."
```

- [ ] **Step 3: Update the root feature PR description**

Add the Python SDK PR URL to GlobalRouter PR #666 under its SDK dependency section.
