from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from .repository import ChatRepsository

async def get_repository(session: AsyncSession = Depends(get_session)) -> ChatRepsository:
  return ChatRepsository(session=session)