from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from apps.chat.schemas import ChatRequest, ChatResponse
from apps.chat.services import ChatServiceDep
from core.deps import CurrentUser
from core.settings import settings

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
@limiter.limit(settings.rate_limit_chat)
async def send_chat(
    request: Request,
    payload: ChatRequest,
    user: CurrentUser,
    service: ChatServiceDep,
) -> ChatResponse:
    del request, user
    return await service.reply(payload.messages)
