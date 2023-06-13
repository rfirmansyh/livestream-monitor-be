from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.modules.livestreams.repository import LivestreamRepository

async def get_repository(session: AsyncSession = Depends(get_session)) -> LivestreamRepository:
  return LivestreamRepository(session=session)
