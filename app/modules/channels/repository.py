from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, text
from sqlmodel import select
from .model import Channel, ChannelYtData

class ChannelRepository:
  def __init__(self, session: AsyncSession):
    self.session = session

  async def get_with_summary(self):
    query = text(f"""
      SELECT 
        ch.*,
          COUNT(ls.id) as total_livestreams,
          (
              SELECT COUNT(*) 
              FROM `chats` 
              AS ca 
              WHERE 
                ca.livestream_id IN (
                    SELECT id FROM `livestreams` WHERE `livestreams`.`channel_id` = ch.id
                  ) 
          ) AS total_chats_processed,
          (
              SELECT COUNT(*) 
              FROM `chats` 
              AS ca 
              WHERE 
                ca.livestream_id IN (
                    SELECT id FROM `livestreams` WHERE `livestreams`.`channel_id` = ch.id
                  ) AND 
                ca.predicted_as = 'HS'
          ) AS total_chats_detected
      FROM `channels` AS ch
      LEFT JOIN `livestreams` AS ls ON ls.channel_id = ch.id
      GROUP BY ch.id
    """)
    
    res = await self.session.execute(query)
    return res.all()

  async def create_from_api(self, yt_data, **kwargs):
    channelYtData = ChannelYtData(yt_data, **kwargs)
    channel = Channel(**channelYtData.__dict__)
    
    stmt = insert(Channel).prefix_with("IGNORE").values(channel.dict())
    await self.session.execute(stmt)
    await self.session.commit()
    
    return channel