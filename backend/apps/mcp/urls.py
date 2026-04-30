from fastapi import APIRouter

from apps.mcp.views import McpViews

router = APIRouter()
router.include_router(McpViews().router)
