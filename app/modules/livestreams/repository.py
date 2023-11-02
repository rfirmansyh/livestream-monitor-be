import app.modules.livestreams.schemas as sc

from datetime import datetime
from typing import Optional
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from .model import Livestream, LivestreamYtData


class LivestreamRepository:
  def __init__(self, session: AsyncSession):
    self.session = session

  async def get_by_livestream_url_id(self, livestream_url_id: str) -> Optional[sc.LivestreamRead]:
    q = select(Livestream).where(Livestream.livestream_url_id == livestream_url_id).limit(1)
    res = await self.session.execute(q)
    return res.scalar_one_or_none()
  
  async def create_from_api(self, yt_data, **kwargs):
    livestreamYtData = LivestreamYtData(yt_data, **kwargs)
    livestream = Livestream(**livestreamYtData.__dict__)
    
    self.session.add(livestream)
    await self.session.commit()
    await self.session.refresh(livestream)

    return livestream
  
  async def update_livestream_end_time(self, livestream_url_id, end_time = None):
    livestream_current = await self.get_by_livestream_url_id(livestream_url_id)
    if livestream_current:
      setattr(livestream_current, 'livestream_end_time', datetime.now())
      
      self.session.add(livestream_current)
      await self.session.commit()
      await self.session.refresh(livestream_current)
      
      return livestream_current
    
    return None
  
  async def destroy(self, id: int):
    res = await self.session.execute(
      select(Livestream).where(Livestream.id == id)
    )
    livestream = res.scalar_one()
    await self.session.delete(livestream)
    await self.session.commit()

    return livestream

