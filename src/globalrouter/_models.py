from __future__ import annotations

from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

JSONDict = dict[str, Any]


class GlobalRouterModel(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)


class APIResponse(GlobalRouterModel):
    id: Optional[str] = None
    object: Optional[str] = None
    data: Any = None
    status: Optional[str] = None
    text: Optional[str] = None


class GeminiImageInlineData(GlobalRouterModel):
    mime_type: str = Field(alias="mimeType")
    data: str


class GeminiImagePart(GlobalRouterModel):
    text: Optional[str] = None
    inline_data: Optional[GeminiImageInlineData] = Field(default=None, alias="inlineData")


class GeminiImageContent(GlobalRouterModel):
    role: Optional[str] = None
    parts: list[GeminiImagePart] = Field(default_factory=list)


class GeminiImageSafetyRating(GlobalRouterModel):
    category: Optional[str] = None
    probability: Optional[str] = None
    blocked: Optional[bool] = None


class GeminiImageCandidate(GlobalRouterModel):
    content: GeminiImageContent
    finish_reason: Optional[str] = Field(default=None, alias="finishReason")
    safety_ratings: Optional[list[GeminiImageSafetyRating]] = Field(
        default=None,
        alias="safetyRatings",
    )


class GeminiImageUsageMetadata(GlobalRouterModel):
    prompt_token_count: Optional[int] = Field(default=None, alias="promptTokenCount")
    candidates_token_count: Optional[int] = Field(default=None, alias="candidatesTokenCount")
    total_token_count: Optional[int] = Field(default=None, alias="totalTokenCount")
    cached_content_token_count: Optional[int] = Field(
        default=None,
        alias="cachedContentTokenCount",
    )
    thoughts_token_count: Optional[int] = Field(default=None, alias="thoughtsTokenCount")
    prompt_tokens_details: Optional[list[JSONDict]] = Field(
        default=None,
        alias="promptTokensDetails",
    )
    candidates_tokens_details: Optional[list[JSONDict]] = Field(
        default=None,
        alias="candidatesTokensDetails",
    )


class GeminiImagePromptFeedback(GlobalRouterModel):
    block_reason: Optional[str] = Field(default=None, alias="blockReason")
    safety_ratings: Optional[list[GeminiImageSafetyRating]] = Field(
        default=None,
        alias="safetyRatings",
    )


class GeminiGenerateContentResponse(GlobalRouterModel):
    candidates: list[GeminiImageCandidate] = Field(default_factory=list)
    model_version: str = Field(alias="modelVersion")
    response_id: Optional[str] = Field(default=None, alias="responseId")
    usage_metadata: Optional[GeminiImageUsageMetadata] = Field(
        default=None,
        alias="usageMetadata",
    )
    prompt_feedback: Optional[GeminiImagePromptFeedback] = Field(
        default=None,
        alias="promptFeedback",
    )


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


class SeedAudioSubtitleWord(GlobalRouterModel):
    text: str = ""
    start_time: Optional[int] = None
    end_time: Optional[int] = None


class SeedAudioSubtitleSentence(GlobalRouterModel):
    text: str = ""
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    words: list[SeedAudioSubtitleWord] = Field(default_factory=list)


class SeedAudioSubtitle(GlobalRouterModel):
    text: str = ""
    sentences: list[SeedAudioSubtitleSentence] = Field(default_factory=list)


class SeedAudioResponse(GlobalRouterModel):
    code: Optional[Union[int, str]] = None  # noqa: UP007 - Python 3.9 compatibility
    message: Optional[str] = None
    audio: Optional[str] = None
    duration: Optional[float] = None
    original_duration: Optional[float] = None
    url: Optional[str] = None
    subtitle: Optional[SeedAudioSubtitle] = None


class DeletedObject(GlobalRouterModel):
    id: Optional[str] = None
    deleted: bool = False
    status: Optional[str] = None
