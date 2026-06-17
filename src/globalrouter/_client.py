from __future__ import annotations

import asyncio
import os
from threading import Thread
from time import sleep
from typing import Any, Optional, TypeVar, cast

import httpx
from pydantic import BaseModel

from globalrouter._errors import GlobalRouterError, error_from_response
from globalrouter._models import JSONDict
from globalrouter._resources import (
    AudioResource,
    ChatResource,
    CreditsResource,
    EmbeddingsResource,
    GenerationsResource,
    ImagesResource,
    KeysResource,
    MessagesResource,
    ModelsResource,
    ProvidersResource,
    ResponsesResource,
    TasksResource,
    ThreeDResource,
    VideosResource,
)
from globalrouter._webhooks import verify_webhook_signature

T = TypeVar("T", bound=BaseModel)


class GlobalRouter:
    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: str = "https://api.globalrouter.ai",
        timeout_seconds: float = 30,
        max_retries: int = 2,
        transport: Optional[httpx.BaseTransport] = None,
        async_transport: Optional[httpx.AsyncBaseTransport] = None,
    ) -> None:
        resolved_api_key = api_key or os.environ.get("GLOBALROUTER_API_KEY")
        if not resolved_api_key:
            raise ValueError("GlobalRouter api_key is required or GLOBALROUTER_API_KEY must be set")

        self.api_key = resolved_api_key
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout_seconds,
            transport=transport,
        )
        self._async_client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout_seconds,
            transport=async_transport,
        )

        self.chat = ChatResource(self)
        self.responses = ResponsesResource(self)
        self.messages = MessagesResource(self)
        self.embeddings = EmbeddingsResource(self)
        self.models = ModelsResource(self)
        self.credits = CreditsResource(self)
        self.generations = GenerationsResource(self)
        self.keys = KeysResource(self)
        self.providers = ProvidersResource(self)
        self.videos = VideosResource(self)
        self.tasks = TasksResource(self)
        self.images = ImagesResource(self)
        self.audio = AudioResource(self)
        self.three_d = ThreeDResource(self)

    def close(self) -> None:
        try:
            self._client.close()
        finally:
            self._close_async_client_from_sync()

    async def aclose(self) -> None:
        try:
            await self._async_client.aclose()
        finally:
            self._client.close()

    def __enter__(self) -> "GlobalRouter":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    async def __aenter__(self) -> "GlobalRouter":
        return self

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
        await self.aclose()

    def _close_async_client_from_sync(self) -> None:
        if self._async_client.is_closed:
            return

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(self._async_client.aclose())
            return

        error: BaseException | None = None

        def close_in_thread() -> None:
            nonlocal error
            try:
                asyncio.run(self._async_client.aclose())
            except BaseException as exc:
                error = exc

        thread = Thread(target=close_in_thread)
        thread.start()
        thread.join()
        if error is not None:
            raise error

    @staticmethod
    def verify_webhook_signature(secret: str, payload: bytes, signature: str) -> bool:
        return verify_webhook_signature(secret, payload, signature)

    def request_model(
        self,
        method: str,
        path: str,
        model: type[T],
        *,
        json_body: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> T:
        response = self.request(method, path, json_body=json_body, params=params, headers=headers)
        return model.model_validate(response.json())

    async def request_model_async(
        self,
        method: str,
        path: str,
        model: type[T],
        *,
        json_body: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> T:
        response = await self.request_async(
            method,
            path,
            json_body=json_body,
            params=params,
            headers=headers,
        )
        return model.model_validate(response.json())

    def request(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> httpx.Response:
        last_error: Optional[httpx.TransportError] = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self._client.request(
                    method,
                    path,
                    headers=self._headers(headers),
                    json=json_body,
                    params=_clean(params),
                )
            except httpx.TransportError as exc:
                last_error = exc
                self._sleep_before_retry(attempt)
                continue
            if response.status_code >= 500 and attempt < self.max_retries:
                self._sleep_before_retry(attempt)
                continue
            if response.status_code >= 400:
                raise error_from_response(response)
            return response
        if last_error is not None:
            raise last_error
        raise RuntimeError("GlobalRouter SDK request exhausted retries")

    async def request_async(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[dict[str, Any]] = None,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> httpx.Response:
        last_error: Optional[httpx.TransportError] = None
        for attempt in range(self.max_retries + 1):
            try:
                response = await self._async_client.request(
                    method,
                    path,
                    headers=self._headers(headers),
                    json=json_body,
                    params=_clean(params),
                )
            except httpx.TransportError as exc:
                last_error = exc
                await self._async_sleep_before_retry(attempt)
                continue
            if response.status_code >= 500 and attempt < self.max_retries:
                await self._async_sleep_before_retry(attempt)
                continue
            if response.status_code >= 400:
                raise error_from_response(response)
            return response
        if last_error is not None:
            raise last_error
        raise RuntimeError("GlobalRouter SDK request exhausted retries")

    def stream(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> httpx.Response:
        response = self._client.build_request(
            method,
            path,
            headers=self._headers(headers),
            json=json_body,
        )
        result = self._client.send(response, stream=True)
        if result.status_code >= 400:
            try:
                raise error_from_response(result)
            finally:
                result.close()
        return result

    async def stream_async(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> httpx.Response:
        request = self._async_client.build_request(
            method,
            path,
            headers=self._headers(headers),
            json=json_body,
        )
        result = await self._async_client.send(request, stream=True)
        if result.status_code >= 400:
            try:
                raise error_from_response(result)
            finally:
                await result.aclose()
        return result

    def _headers(self, extra: Optional[dict[str, str]] = None) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "globalrouter-python/0.1.0",
        }
        if extra:
            headers.update(extra)
        return headers

    def _sleep_before_retry(self, attempt: int) -> None:
        if attempt < self.max_retries:
            sleep(min(0.25 * (2**attempt), 1.0))

    async def _async_sleep_before_retry(self, attempt: int) -> None:
        if attempt < self.max_retries:
            import asyncio

            await asyncio.sleep(min(0.25 * (2**attempt), 1.0))


def payload_from_mapping(request: Optional[dict[str, Any]], params: dict[str, Any]) -> JSONDict:
    payload: JSONDict = {}
    if request is not None:
        payload.update(request)
    payload.update({key: value for key, value in params.items() if value is not None})
    return payload


def _clean(params: Optional[dict[str, Any]]) -> Optional[dict[str, str]]:
    if params is None:
        return None
    return {key: str(value) for key, value in params.items() if value is not None}


def _ensure_error_type(_: GlobalRouterError) -> None:
    return None


def _cast_json_dict(value: Any) -> JSONDict:
    return cast(JSONDict, value)
