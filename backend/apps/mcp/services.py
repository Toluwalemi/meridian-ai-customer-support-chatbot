import asyncio
from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from core.exceptions import UpstreamError
from core.logging import logger
from core.settings import settings


class McpUnavailable(UpstreamError):
    status_code = 503


class McpClientService:
    """Process-level singleton wrapping a streamable-HTTP MCP session."""

    def __init__(self, server_url: str, timeout: int) -> None:
        self.server_url = server_url
        self.timeout = timeout
        self.session: ClientSession | None = None
        self._stack = AsyncExitStack()
        self._tools_cache: list[dict[str, Any]] = []
        self._lock = asyncio.Lock()

    async def connect(self) -> None:
        async with self._lock:
            if self.session is not None:
                return
            try:
                read, write, _ = await self._stack.enter_async_context(
                    streamablehttp_client(self.server_url)
                )
                self.session = await self._stack.enter_async_context(
                    ClientSession(read, write)
                )
                await self.session.initialize()
                await self._refresh_tools_locked()
                logger.info(
                    "mcp.connected",
                    server_url=self.server_url,
                    tools=[t["name"] for t in self._tools_cache],
                )
            except Exception as exc:
                await self._stack.aclose()
                self.session = None
                raise McpUnavailable(f"Cannot connect to MCP server: {exc}") from exc

    async def _refresh_tools_locked(self) -> list[dict[str, Any]]:
        if self.session is None:
            raise McpUnavailable("MCP session not initialized")
        result = await self.session.list_tools()
        self._tools_cache = [
            {
                "name": t.name,
                "description": (t.description or "").strip(),
                "input_schema": t.inputSchema,
            }
            for t in result.tools
        ]
        return self._tools_cache

    async def refresh_tools(self) -> list[dict[str, Any]]:
        async with self._lock:
            return await self._refresh_tools_locked()

    @property
    def tools(self) -> list[dict[str, Any]]:
        return self._tools_cache

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> list[dict[str, Any]]:
        if self.session is None:
            raise McpUnavailable("MCP session not initialized")
        try:
            result = await asyncio.wait_for(
                self.session.call_tool(name, arguments), timeout=self.timeout
            )
        except asyncio.TimeoutError as exc:
            raise UpstreamError(f"MCP tool '{name}' timed out") from exc
        return [block.model_dump() for block in result.content]

    async def close(self) -> None:
        await self._stack.aclose()
        self.session = None


mcp_service = McpClientService(
    server_url=str(settings.mcp_server_url),
    timeout=settings.mcp_timeout_seconds,
)
