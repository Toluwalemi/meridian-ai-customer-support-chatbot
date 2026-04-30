from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ToolCallTrace(BaseModel):
    name: str
    arguments: dict[str, Any]
    result_preview: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)


class ChatResponse(BaseModel):
    reply: str
    tool_calls: list[ToolCallTrace] = []
    stop_reason: str
    iterations: int
