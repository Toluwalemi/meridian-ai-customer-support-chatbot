from typing import Annotated

from fastapi import APIRouter, Depends

from apps.mcp.schemas import ToolDescriptor
from apps.mcp.services import McpClientService, mcp_service
from core.deps import CurrentUser


def get_mcp() -> McpClientService:
    return mcp_service


class McpViews:
    def __init__(self) -> None:
        self.router = APIRouter(prefix="/mcp", tags=["mcp"])
        self.router.add_api_route(
            "/tools",
            self.list_tools,
            methods=["GET"],
            response_model=list[ToolDescriptor],
        )
        self.router.add_api_route(
            "/tools/refresh",
            self.refresh_tools,
            methods=["POST"],
            response_model=list[ToolDescriptor],
        )

    async def list_tools(
        self,
        _user: CurrentUser,
        client: Annotated[McpClientService, Depends(get_mcp)],
    ) -> list[ToolDescriptor]:
        return [ToolDescriptor(**t) for t in client.tools]

    async def refresh_tools(
        self,
        _user: CurrentUser,
        client: Annotated[McpClientService, Depends(get_mcp)],
    ) -> list[ToolDescriptor]:
        tools = await client.refresh_tools()
        return [ToolDescriptor(**t) for t in tools]
