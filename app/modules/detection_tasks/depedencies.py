from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from .repository import DetectionTaskRepository


async def get_repository(session: AsyncSession = Depends(get_session)) -> DetectionTaskRepository:
  return DetectionTaskRepository(session=session)