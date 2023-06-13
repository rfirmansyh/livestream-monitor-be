from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, text
from sqlmodel import select
from .model import Channel, ChannelYtData

class ChannelRepository:
  def __init__(self, session: AsyncSession):
    self.session = session

  async def all(self):
    query = select(Channel)
    res = await self.session.execute(query)
    return res.scalars().all()
  
  async def get(self):
    query = text(f"""
      SELECT 
        ch.title,
        ch.thumbnails,
        ch.channel_id,
        COALESCE((SELECT COUNT(ls_2.id) from `livestreams` AS ls_2 WHERE ls_2.channel_id = ch.channel_id), 0) AS total_livestream_detected,
        COALESCE((
            SELECT COUNT(ct_2.id) 
            from `chats` AS ct_2 
            WHERE ct_2.livestream_id IN (
                SELECT id
                FROM `livestreams` ls_ct_2
                WHERE ls_ct_2.channel_id = ch.channel_id
            )
        ), 0) AS total_chats_processed,
        COALESCE((
            SELECT COUNT(ct_2.id) 
            from `chats` AS ct_2 
            WHERE 
                ct_2.predicted_as = 'HS' AND
                ct_2.livestream_id IN (
                    SELECT id
                    FROM `livestreams` ls_ct_2
                    WHERE ls_ct_2.channel_id = ch.channel_id
                )
        ), 0) AS total_chats_hs_detected,
        COALESCE((
            SELECT COUNT(ct_2.id) 
            from `chats` AS ct_2 
            WHERE 
                ct_2.predicted_as = 'NHS' AND
                ct_2.livestream_id IN (
                    SELECT id
                    FROM `livestreams` ls_ct_2
                    WHERE ls_ct_2.channel_id = ch.channel_id
                )
        ), 0) AS total_chats_nhs_detected
      FROM `channels` AS ch
      JOIN `livestreams` AS ls ON ls.channel_id = ch.channel_id
      GROUP BY ch.channel_id
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