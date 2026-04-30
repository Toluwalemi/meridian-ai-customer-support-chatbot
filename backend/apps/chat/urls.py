from fastapi import APIRouter

from apps.chat.views import ChatViews, limiter

router = APIRouter()
router.include_router(ChatViews().router)

__all__ = ["router", "limiter"]
