import json
from typing import Annotated, Any

from fastapi import Depends
from openai import AsyncOpenAI

from apps.chat.prompts import SYSTEM_PROMPT
from apps.chat.schemas import ChatMessage, ChatResponse, ToolCallTrace
from apps.mcp.services import McpClientService, mcp_service
from core.exceptions import UpstreamError
from core.logging import logger
from core.settings import settings

_MAX_RESULT_PREVIEW = 240


def _preview(content: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for block in content:
        text = block.get("text") if isinstance(block, dict) else None
        if text:
            parts.append(str(text))
    joined = "\n".join(parts) or str(content)
    return joined[:_MAX_RESULT_PREVIEW]


def _preview_tool_result(result: Any) -> str:
    if isinstance(result, list):
        return _preview(result)
    return str(result)[:_MAX_RESULT_PREVIEW]


def _mcp_tools_to_openai(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t.get("description") or "",
                "parameters": t["input_schema"],
            },
        }
        for t in tools
    ]


def _to_openai_messages(messages: list[ChatMessage]) -> list[dict[str, Any]]:
    return [{"role": m.role, "content": m.content} for m in messages]


class ChatService:
    def __init__(self, mcp: McpClientService) -> None:
        self.mcp = mcp
        default_headers: dict[str, str] = {}
        if settings.openrouter_site_url is not None:
            default_headers["HTTP-Referer"] = str(settings.openrouter_site_url)
        if settings.openrouter_site_name is not None:
            default_headers["X-Title"] = settings.openrouter_site_name

        self.client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url=str(settings.openrouter_base_url),
            default_headers=default_headers or None,
        )
        self.model = settings.openrouter_model
        self.max_iterations = settings.max_tool_iterations

    async def reply(self, messages: list[ChatMessage]) -> ChatResponse:
        if not self.mcp.tools:
            await self.mcp.refresh_tools()
        openai_tools = _mcp_tools_to_openai(self.mcp.tools)
        convo: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *_to_openai_messages(messages),
        ]
        traces: list[ToolCallTrace] = []

        for iteration in range(1, self.max_iterations + 1):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    max_tokens=1024,
                    temperature=0,
                    tools=openai_tools,
                    messages=convo,
                )
            except Exception as exc:
                logger.error("chat.openrouter_error", error=str(exc))
                raise UpstreamError(f"LLM call failed: {exc}") from exc

            choice = response.choices[0]
            message = choice.message

            if not message.tool_calls:
                text = (message.content or "").strip()
                logger.info(
                    "chat.completed",
                    iterations=iteration,
                    stop_reason=choice.finish_reason,
                    tool_calls=len(traces),
                )
                return ChatResponse(
                    reply=text or "(no response)",
                    tool_calls=traces,
                    stop_reason=choice.finish_reason or "stop",
                    iterations=iteration,
                )

            convo.append(message.model_dump(exclude_none=True))

            for tool_call in message.tool_calls:
                if tool_call.function is None:
                    continue

                logger.info(
                    "chat.tool_call",
                    name=tool_call.function.name,
                    iteration=iteration,
                )
                arguments: dict[str, Any] = {}

                try:
                    arguments = json.loads(tool_call.function.arguments or "{}")
                    if not isinstance(arguments, dict):
                        raise ValueError("Tool arguments must decode to an object")
                    result = await self.mcp.call_tool(tool_call.function.name, arguments)
                    result_text = json.dumps(result)
                    traces.append(
                        ToolCallTrace(
                            name=tool_call.function.name,
                            arguments=arguments,
                            result_preview=_preview_tool_result(result),
                        )
                    )
                    convo.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result_text,
                        }
                    )
                except Exception as exc:
                    logger.warning(
                        "chat.tool_error",
                        name=tool_call.function.name,
                        error=str(exc),
                    )
                    error_text = f"Tool error: {exc}"
                    traces.append(
                        ToolCallTrace(
                            name=tool_call.function.name,
                            arguments=arguments,
                            result_preview=error_text[:_MAX_RESULT_PREVIEW],
                        )
                    )
                    convo.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": error_text,
                        }
                    )

        logger.warning("chat.iteration_cap_reached", cap=self.max_iterations)
        return ChatResponse(
            reply=(
                "I hit the maximum number of tool calls for this turn. "
                "Could you rephrase or break the request into smaller steps?"
            ),
            tool_calls=traces,
            stop_reason="iteration_cap",
            iterations=self.max_iterations,
        )


def get_chat_service() -> ChatService:
    return ChatService(mcp_service)


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
