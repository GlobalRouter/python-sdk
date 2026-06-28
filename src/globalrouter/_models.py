from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

JSONDict = dict[str, Any]


class GlobalRouterModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class APIResponse(GlobalRouterModel):
    id: Optional[str] = None
    object: Optional[str] = None
    data: Any = None
    status: Optional[str] = None
    text: Optional[str] = None


class ChatCompletion(GlobalRouterModel):
    id: str
    object: str = "chat.completion"
    created: Optional[int] = None
    model: str
    choices: list[JSONDict] = Field(default_factory=list)
    usage: Optional[JSONDict] = None
    openrouter_metadata: Optional[JSONDict] = None


class ChatCompletionChunk(GlobalRouterModel):
    id: Optional[str] = None
    object: Optional[str] = None
    created: Optional[int] = None
    model: Optional[str] = None
    choices: list[JSONDict] = Field(default_factory=list)
    usage: Optional[JSONDict] = None
    openrouter_metadata: Optional[JSONDict] = None


class ModelList(GlobalRouterModel):
    object: str = "list"
    data: list[JSONDict] = Field(default_factory=list)


class Task(GlobalRouterModel):
    id: str
    status: Optional[str] = None
    model: Optional[str] = None
    type: Optional[str] = None
    output: Any = None
    usage: Any = None
    error: Any = None


class VideoJob(GlobalRouterModel):
    id: str
    object: str = "video.generation"
    status: str
    model: Optional[str] = None
    provider: Optional[str] = None
    polling_url: Optional[str] = None
    content_url: Optional[str] = None
    usage: Any = None
    error: Any = None


class DeletedObject(GlobalRouterModel):
    id: Optional[str] = None
    deleted: bool = False
    status: Optional[str] = None
