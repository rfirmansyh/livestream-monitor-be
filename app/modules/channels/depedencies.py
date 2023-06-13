from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from .repository import ChannelRepository


async def get_repository(session: AsyncSession = Depends(get_session)) -> ChannelRepository:
  return ChannelRepository(session=session)