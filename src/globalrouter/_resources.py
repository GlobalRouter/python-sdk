from __future__ import annotations

from collections.abc import AsyncIterator, Iterator, Mapping
from contextlib import closing
from typing import TYPE_CHECKING, Any, Optional

from globalrouter._models import (
    APIResponse,
    ChatCompletion,
    ChatCompletionChunk,
    DeletedObject,
    JSONDict,
    ModelList,
    Task,
    VideoJob,
)
from globalrouter._streaming import aiter_sse_models, iter_sse_models

if TYPE_CHECKING:
    from globalrouter._client import GlobalRouter


class BaseResource:
    def __init__(self, client: "GlobalRouter") -> None:
        self._client = client

    def _payload(self, request: Optional[Mapping[str, Any]], params: dict[str, Any]) -> JSONDict:
        payload: JSONDict = {}
        if request is not None:
            payload.update(dict(request))
        payload.update({key: value for key, value in params.items() if value is not None})
        return payload

    def _payload_without_params(
        self,
        request: Optional[Mapping[str, Any]],
        params: dict[str, Any],
        excluded: set[str],
    ) -> JSONDict:
        return self._payload(
            request,
            {key: value for key, value in params.items() if key not in excluded},
        )


class ChatResource(BaseResource):
    def send(self, request: Optional[Mapping[str, Any]] = None, **params: Any) -> ChatCompletion:
        return self._client.request_model(
            "POST",
            "/api/v1/chat/completions",
            ChatCompletion,
            json_body=self._payload(request, params),
        )

    async def send_async(
        self,
        request: Optional[Mapping[str, Any]] = None,
        **params: Any,
    ) -> ChatCompletion:
        return await self._client.request_model_async(
            "POST",
            "/api/v1/chat/completions",
            ChatCompletion,
            json_body=self._payload(request, params),
        )

    def stream(
        self,
        request: Optional[Mapping[str, Any]] = None,
        **params: Any,
    ) -> Iterator[ChatCompletionChunk]:
        payload = {**self._payload(request, params), "stream": True}
        with closing(
            self._client.stream("POST", "/api/v1/chat/completions", json_body=payload)
        ) as response:
            yield from iter_sse_models(response, ChatCompletionChunk)

    async def stream_async(
        self,
        request: Optional[Mapping[str, Any]] = None,
        **params: Any,
    ) -> AsyncIterator[ChatCompletionChunk]:
        payload = {**self._payload(request, params), "stream": True}
        response = await self._client.stream_async(
            "POST",
            "/api/v1/chat/completions",
            json_body=payload,
        )
        try:
            async for item in aiter_sse_models(response, ChatCompletionChunk):
                yield item
        finally:
            await response.aclose()


class ResponsesResource(BaseResource):
    def create(self, request: Optional[Mapping[str, Any]] = None, **params: Any) -> APIResponse:
        return self._client.request_model(
            "POST",
            "/api/v1/responses",
            APIResponse,
            json_body=self._payload(request, params),
        )

    async def create_async(
        self,
        request: Optional[Mapping[str, Any]] = None,
        **params: Any,
    ) -> APIResponse:
        return await self._client.request_model_async(
            "POST",
            "/api/v1/responses",
            APIResponse,
            json_body=self._payload(request, params),
        )


class MessagesResource(BaseResource):
    def create(self, request: Optional[Mapping[str, Any]] = None, **params: Any) -> APIResponse:
        return self._client.request_model(
            "POST",
            "/api/v1/messages",
            APIResponse,
            json_body=self._payload(request, params),
        )

    async def create_async(
        self,
        request: Optional[Mapping[str, Any]] = None,
        **params: Any,
    ) -> APIResponse:
        return await self._client.request_model_async(
            "POST",
            "/api/v1/messages",
            APIResponse,
            json_body=self._payload(request, params),
        )


class EmbeddingsResource(BaseResource):
    def create(self, request: Optional[Mapping[str, Any]] = None, **params: Any) -> APIResponse:
        return self._client.request_model(
            "POST",
            "/api/v1/embeddings",
            APIResponse,
            json_body=self._payload(request, params),
        )

    async def create_async(
        self,
        request: Optional[Mapping[str, Any]] = None,
        **params: Any,
    ) -> APIResponse:
        return await self._client.request_model_async(
            "POST",
            "/api/v1/embeddings",
            APIResponse,
            json_body=self._payload(request, params),
        )


class ModelsResource(BaseResource):
    def list(self, **params: Any) -> ModelList:
        return self._client.request_model("GET", "/api/v1/models", ModelList, params=params)

    async def list_async(self, **params: Any) -> ModelList:
        return await self._client.request_model_async(
            "GET",
            "/api/v1/models",
            ModelList,
            params=params,
        )

    def count(self, **params: Any) -> APIResponse:
        return self._client.request_model("GET", "/api/v1/models/count", APIResponse, params=params)

    async def count_async(self, **params: Any) -> APIResponse:
        return await self._client.request_model_async(
            "GET",
            "/api/v1/models/count",
            APIResponse,
            params=params,
        )

    def endpoints(self, author: str, slug: str) -> APIResponse:
        return self._client.request_model(
            "GET",
            f"/api/v1/models/{author}/{slug}/endpoints",
            APIResponse,
        )

    async def endpoints_async(self, author: str, slug: str) -> APIResponse:
        return await self._client.request_model_async(
            "GET",
            f"/api/v1/models/{author}/{slug}/endpoints",
            APIResponse,
        )


class CreditsResource(BaseResource):
    def get(self) -> APIResponse:
        return self._client.request_model("GET", "/api/v1/credits", APIResponse)

    async def get_async(self) -> APIResponse:
        return await self._client.request_model_async("GET", "/api/v1/credits", APIResponse)


class GenerationsResource(BaseResource):
    def get(self, generation_id: str) -> APIResponse:
        return self._client.request_model(
            "GET",
            "/api/v1/generation",
            APIResponse,
            params={"id": generation_id},
        )

    async def get_async(self, generation_id: str) -> APIResponse:
        return await self._client.request_model_async(
            "GET",
            "/api/v1/generation",
            APIResponse,
            params={"id": generation_id},
        )

    def content(self, generation_id: str) -> APIResponse:
        return self._client.request_model(
            "GET",
            "/api/v1/generation/content",
            APIResponse,
            params={"id": generation_id},
        )

    async def content_async(self, generation_id: str) -> APIResponse:
        return await self._client.request_model_async(
            "GET",
            "/api/v1/generation/content",
            APIResponse,
            params={"id": generation_id},
        )


class KeysResource(BaseResource):
    def current(self) -> APIResponse:
        return self._client.request_model("GET", "/api/v1/key", APIResponse)

    async def current_async(self) -> APIResponse:
        return await self._client.request_model_async("GET", "/api/v1/key", APIResponse)

    def list(self, *, include_disabled: bool = False) -> APIResponse:
        return self._client.request_model(
            "GET",
            "/api/v1/keys",
            APIResponse,
            params={"include_disabled": include_disabled},
        )

    async def list_async(self, *, include_disabled: bool = False) -> APIResponse:
        return await self._client.request_model_async(
            "GET",
            "/api/v1/keys",
            APIResponse,
            params={"include_disabled": include_disabled},
        )

    def get(self, key_ref: str) -> APIResponse:
        return self._client.request_model("GET", f"/api/v1/keys/{key_ref}", APIResponse)

    async def get_async(self, key_ref: str) -> APIResponse:
        return await self._client.request_model_async(
            "GET",
            f"/api/v1/keys/{key_ref}",
            APIResponse,
        )

    def create(self, request: Optional[Mapping[str, Any]] = None, **params: Any) -> APIResponse:
        return self._client.request_model(
            "POST",
            "/api/v1/keys",
            APIResponse,
            json_body=self._payload(request, params),
        )

    async def create_async(
        self,
        request: Optional[Mapping[str, Any]] = None,
        **params: Any,
    ) -> APIResponse:
        return await self._client.request_model_async(
            "POST",
            "/api/v1/keys",
            APIResponse,
            json_body=self._payload(request, params),
        )

    def update(
        self,
        key_ref: str,
        request: Optional[Mapping[str, Any]] = None,
        **params: Any,
    ) -> APIResponse:
        return self._client.request_model(
            "PATCH",
            f"/api/v1/keys/{key_ref}",
            APIResponse,
            json_body=self._payload(request, params),
        )

    async def update_async(
        self,
        key_ref: str,
        request: Optional[Mapping[str, Any]] = None,
        **params: Any,
    ) -> APIResponse:
        return await self._client.request_model_async(
            "PATCH",
            f"/api/v1/keys/{key_ref}",
            APIResponse,
            json_body=self._payload(request, params),
        )

    def delete(self, key_ref: str) -> DeletedObject:
        return self._client.request_model("DELETE", f"/api/v1/keys/{key_ref}", DeletedObject)

    async def delete_async(self, key_ref: str) -> DeletedObject:
        return await self._client.request_model_async(
            "DELETE",
            f"/api/v1/keys/{key_ref}",
            DeletedObject,
        )


class ProvidersResource(BaseResource):
    def list(self) -> APIResponse:
        return self._client.request_model("GET", "/api/v1/providers", APIResponse)

    async def list_async(self) -> APIResponse:
        return await self._client.request_model_async("GET", "/api/v1/providers", APIResponse)


class VideosResource(BaseResource):
    def create(self, request: Optional[Mapping[str, Any]] = None, **params: Any) -> VideoJob:
        return self._client.request_model(
            "POST",
            "/api/v1/videos",
            VideoJob,
            json_body=self._payload_without_params(request, params, {"idempotency_key"}),
            headers=_idempotency_header(params.get("idempotency_key")),
        )

    async def create_async(
        self,
        request: Optional[Mapping[str, Any]] = None,
        **params: Any,
    ) -> VideoJob:
        return await self._client.request_model_async(
            "POST",
            "/api/v1/videos",
            VideoJob,
            json_body=self._payload_without_params(request, params, {"idempotency_key"}),
            headers=_idempotency_header(params.get("idempotency_key")),
        )

    def get(self, job_id: str) -> VideoJob:
        return self._client.request_model("GET", f"/api/v1/videos/{job_id}", VideoJob)

    async def get_async(self, job_id: str) -> VideoJob:
        return await self._client.request_model_async(
            "GET",
            f"/api/v1/videos/{job_id}",
            VideoJob,
        )

    def content(self, job_id: str) -> APIResponse:
        return self._client.request_model("GET", f"/api/v1/videos/{job_id}/content", APIResponse)

    async def content_async(self, job_id: str) -> APIResponse:
        return await self._client.request_model_async(
            "GET",
            f"/api/v1/videos/{job_id}/content",
            APIResponse,
        )

    def models(self) -> APIResponse:
        return self._client.request_model("GET", "/api/v1/videos/models", APIResponse)

    async def models_async(self) -> APIResponse:
        return await self._client.request_model_async("GET", "/api/v1/videos/models", APIResponse)


class TasksResource(BaseResource):
    def create(self, request: Optional[Mapping[str, Any]] = None, **params: Any) -> Task:
        return self._client.request_model(
            "POST",
            "/v1/tasks",
            Task,
            json_body=self._payload_without_params(request, params, {"idempotency_key"}),
            headers=_idempotency_header(params.get("idempotency_key")),
        )

    async def create_async(
        self,
        request: Optional[Mapping[str, Any]] = None,
        **params: Any,
    ) -> Task:
        return await self._client.request_model_async(
            "POST",
            "/v1/tasks",
            Task,
            json_body=self._payload_without_params(request, params, {"idempotency_key"}),
            headers=_idempotency_header(params.get("idempotency_key")),
        )

    def create_batch(self, tasks: list[Mapping[str, Any]]) -> APIResponse:
        return self._client.request_model(
            "POST",
            "/v1/tasks/batch",
            APIResponse,
            json_body={"tasks": [dict(task) for task in tasks]},
        )

    async def create_batch_async(self, tasks: list[Mapping[str, Any]]) -> APIResponse:
        return await self._client.request_model_async(
            "POST",
            "/v1/tasks/batch",
            APIResponse,
            json_body={"tasks": [dict(task) for task in tasks]},
        )

    def get_batch(self, batch_id: str) -> APIResponse:
        return self._client.request_model("GET", f"/v1/tasks/batch/{batch_id}", APIResponse)

    async def get_batch_async(self, batch_id: str) -> APIResponse:
        return await self._client.request_model_async(
            "GET",
            f"/v1/tasks/batch/{batch_id}",
            APIResponse,
        )

    def list(self, **params: Any) -> APIResponse:
        return self._client.request_model(
            "GET",
            "/v1/tasks",
            APIResponse,
            params=_task_params(params),
        )

    async def list_async(self, **params: Any) -> APIResponse:
        return await self._client.request_model_async(
            "GET",
            "/v1/tasks",
            APIResponse,
            params=_task_params(params),
        )

    def get(self, task_id: str, *, wait: bool = False) -> Task:
        return self._client.request_model(
            "GET",
            f"/v1/tasks/{task_id}",
            Task,
            params={"wait": "1" if wait else None},
        )

    async def get_async(self, task_id: str, *, wait: bool = False) -> Task:
        return await self._client.request_model_async(
            "GET",
            f"/v1/tasks/{task_id}",
            Task,
            params={"wait": "1" if wait else None},
        )

    def events(self, task_id: str) -> Iterator[APIResponse]:
        with closing(self._client.stream("GET", f"/v1/tasks/{task_id}/events")) as response:
            yield from iter_sse_models(response, APIResponse)

    async def events_async(self, task_id: str) -> AsyncIterator[APIResponse]:
        response = await self._client.stream_async("GET", f"/v1/tasks/{task_id}/events")
        try:
            async for item in aiter_sse_models(response, APIResponse):
                yield item
        finally:
            await response.aclose()

    def cancel(self, task_id: str) -> Task:
        return self._client.request_model("POST", f"/v1/tasks/{task_id}/cancel", Task)

    async def cancel_async(self, task_id: str) -> Task:
        return await self._client.request_model_async(
            "POST",
            f"/v1/tasks/{task_id}/cancel",
            Task,
        )

    def retry(self, task_id: str) -> Task:
        return self._client.request_model("POST", f"/v1/tasks/{task_id}/retry", Task)

    async def retry_async(self, task_id: str) -> Task:
        return await self._client.request_model_async(
            "POST",
            f"/v1/tasks/{task_id}/retry",
            Task,
        )


class ImagesResource(BaseResource):
    def generate(self, request: Optional[Mapping[str, Any]] = None, **params: Any) -> APIResponse:
        return self._client.request_model(
            "POST",
            "/api/v1/images",
            APIResponse,
            json_body=self._create_images_payload(request, params),
        )

    async def generate_async(
        self,
        request: Optional[Mapping[str, Any]] = None,
        **params: Any,
    ) -> APIResponse:
        return await self._client.request_model_async(
            "POST",
            "/api/v1/images",
            APIResponse,
            json_body=self._create_images_payload(request, params),
        )

    def _create_images_payload(
        self,
        request: Optional[Mapping[str, Any]],
        params: dict[str, Any],
    ) -> JSONDict:
        payload = self._payload(request, params)
        provider = payload.get("provider")
        if provider is None:
            payload.pop("provider", None)
            return payload
        if not isinstance(provider, Mapping):
            payload.pop("provider", None)
            return payload

        normalized_provider: JSONDict = {}
        provider_id = provider.get("provider_id")
        if isinstance(provider_id, str) and provider_id.strip():
            normalized_provider["provider_id"] = provider_id
        options = provider.get("options")
        if isinstance(options, Mapping) and options:
            normalized_provider["options"] = dict(options)
        if normalized_provider:
            payload["provider"] = normalized_provider
        else:
            payload.pop("provider", None)
        return payload

    def create_task(
        self,
        request: Optional[Mapping[str, Any]] = None,
        **params: Any,
    ) -> APIResponse:
        return self._client.request_model(
            "POST",
            "/api/v1/image-tasks",
            APIResponse,
            json_body=self._payload_without_params(request, params, {"idempotency_key"}),
            headers=_idempotency_header(params.get("idempotency_key")),
        )

    async def create_task_async(
        self,
        request: Optional[Mapping[str, Any]] = None,
        **params: Any,
    ) -> APIResponse:
        return await self._client.request_model_async(
            "POST",
            "/api/v1/image-tasks",
            APIResponse,
            json_body=self._payload_without_params(request, params, {"idempotency_key"}),
            headers=_idempotency_header(params.get("idempotency_key")),
        )

    def get_task(self, image_task_id: str) -> APIResponse:
        return self._client.request_model(
            "GET",
            f"/api/v1/image-tasks/{image_task_id}",
            APIResponse,
        )

    async def get_task_async(self, image_task_id: str) -> APIResponse:
        return await self._client.request_model_async(
            "GET",
            f"/api/v1/image-tasks/{image_task_id}",
            APIResponse,
        )


class AudioResource(BaseResource):
    def speech(self, request: Optional[Mapping[str, Any]] = None, **params: Any) -> APIResponse:
        return self._client.request_model(
            "POST",
            "/v1/audio/speech",
            APIResponse,
            json_body=self._payload(request, params),
        )

    async def speech_async(
        self,
        request: Optional[Mapping[str, Any]] = None,
        **params: Any,
    ) -> APIResponse:
        return await self._client.request_model_async(
            "POST",
            "/v1/audio/speech",
            APIResponse,
            json_body=self._payload(request, params),
        )

    def transcription(
        self,
        request: Optional[Mapping[str, Any]] = None,
        **params: Any,
    ) -> APIResponse:
        return self._client.request_model(
            "POST",
            "/v1/audio/transcriptions",
            APIResponse,
            json_body=self._payload(request, params),
        )

    async def transcription_async(
        self,
        request: Optional[Mapping[str, Any]] = None,
        **params: Any,
    ) -> APIResponse:
        return await self._client.request_model_async(
            "POST",
            "/v1/audio/transcriptions",
            APIResponse,
            json_body=self._payload(request, params),
        )


class ThreeDResource(BaseResource):
    def generate(self, request: Optional[Mapping[str, Any]] = None, **params: Any) -> APIResponse:
        return self._client.request_model(
            "POST",
            "/v1/3d/generations",
            APIResponse,
            json_body=self._payload(request, params),
        )

    async def generate_async(
        self,
        request: Optional[Mapping[str, Any]] = None,
        **params: Any,
    ) -> APIResponse:
        return await self._client.request_model_async(
            "POST",
            "/v1/3d/generations",
            APIResponse,
            json_body=self._payload(request, params),
        )


def _task_params(params: dict[str, Any]) -> dict[str, Any]:
    result = dict(params)
    if "metadata_project_id" in result:
        result["metadata.project_id"] = result.pop("metadata_project_id")
    if "task_type" in result:
        result["type"] = result.pop("task_type")
    return result


def _idempotency_header(value: Any) -> Optional[dict[str, str]]:
    if value is None:
        return None
    return {"Idempotency-Key": str(value)}
