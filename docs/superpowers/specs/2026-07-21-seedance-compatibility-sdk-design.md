# Seedance Compatibility Resource Design

**Date:** 2026-07-21
**Status:** Approved design
**Scope:** Add the documented Seedance video-generation and asset compatibility API to the GlobalRouter Python SDK. This is an additional entry point; it does not replace the existing `videos` or `tasks` resources.

## Goal

Give Python users a first-class, synchronous and asynchronous interface for the compatibility surface added for the masked `cloub` provider, without requiring callers to construct raw HTTP requests or rely on provider-specific names.

## Public API

The client will expose `client.seedance` as a new `SeedanceResource` namespace. It will provide the following methods and their `_async` counterparts:

- `create_video_generation(request=None, **params)` → `APIResponse`
- `get_video_generation(task_id)` → `APIResponse`
- `create_asset_group(request=None, **params)` → `APIResponse`
- `create_asset(request=None, **params)` → `APIResponse`
- `get_asset(request=None, **params)` → `APIResponse`

The methods map exactly to the documented compatibility paths:

- `POST /v1/video/generations`
- `GET /v1/video/generations/{task_id}`
- `POST /api/v3/assets/groups`
- `POST /api/v3/assets`
- `POST /api/v3/assets/get`

`create_video_generation` accepts `idempotency_key` as an SDK-only parameter and sends it as `Idempotency-Key`; it must not serialize that key into the JSON body. Other request fields pass through unchanged so the SDK preserves the compatibility request shape.

## Request and Response Handling

The SDK continues its established flexible-mapping convention rather than adding a parallel, incomplete hierarchy of Pydantic request DTOs. This gives callers access to all server-validated video fields while keeping a stable handwritten SDK API.

Asset request keys are intentionally passed through exactly as received. Documentation and examples use the server's case-sensitive fields: `Name`, `Description`, `URL`, `AssetType`, `GroupId`, and `Id`. Responses remain `APIResponse`, which already preserves the `code`, `message`, and `data` envelope.

## Boundaries

- Keep `client.videos` unchanged; it serves the existing GlobalRouter video resource.
- Keep `client.tasks` unchanged; it remains the general native async-task resource.
- Do not expose the upstream vendor name or endpoint.
- Do not add real-person verification methods.
- Do not make network calls in tests.

## Validation

HTTP transport tests will assert all five methods, request method/path, bearer authentication, the idempotency header, and Pascal-case asset payload fields. Both sync and async methods will be tested. A README example will demonstrate the additional `client.seedance` entry point.
