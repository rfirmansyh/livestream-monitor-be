from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, insert, asc
from sqlmodel import select
from fastapi.encoders import jsonable_encoder
from .model import Chat, ChatYtData

class ChatRepsository:
  def __init__(self, session: AsyncSession):
    self.session = session

  async def get_predicted_result_count(self, livestream_id):
    query = text(f"""
      SELECT 
        COUNT(livechat_id) AS total_current_chats,
        (SELECT COUNT(livechat_id) FROM `chats` WHERE `predicted_as` = 'HS' AND `livestream_id` = {livestream_id}) AS total_current_chats_positive_detected,
        (SELECT COUNT(livechat_id) FROM `chats` WHERE `predicted_as` = 'NHS' AND `livestream_id` = {livestream_id}) AS total_current_chats_negative_detected,
        (SELECT COUNT(livechat_id) FROM `chats` WHERE `predicted_as` = 'HS') AS total_all_chats_positive_detected,
        (SELECT COUNT(livechat_id) FROM `chats` WHERE `predicted_as` = 'NHS') AS total_all_chats_negative_detected
      FROM `chats`
      WHERE `livestream_id` = {livestream_id}
    """)
    
    res = await self.session.execute(query)
    res = res.all()
    
    return res[0] if res else None
    
  async def get_limit_and_count_by_livestream_id(self, limit, livestream_id):
    chats_stmt = (
      select(
        select(Chat.id, Chat.display_message, Chat.livechat_id, Chat.predicted_as)
        .where(Chat.livestream_id == livestream_id)
        .order_by(Chat.id.desc())
        .limit(int(limit)).subquery()
      ).order_by(asc('id'))
    )

    res_chats = await self.session.execute(chats_stmt)
    res_total = await self.get_predicted_result_count(livestream_id)
    results = {
      'total': res_total,
      'chats': res_chats.all()
    }
    return jsonable_encoder(results)

  async def get_chats_by_livestream_id(self, livestream_id, predicted_as):
    query = text(f"""
      SELECT ca.*
      FROM `chats` AS ca
      JOIN `livestreams` AS ls ON ls.id = ca.livestream_id
      WHERE ls.id = '{livestream_id}' AND ca.predicted_as = '{predicted_as}'
    """)
    
    res = await self.session.execute(query)
    res = res.all()
    
    return res

  async def get_users_chat_detected(self):
    query = text(f"""
      SELECT
        author_channel_id,
        author_display_name,
        author_image_url,
        COUNT(*) AS total_chats
      FROM
        chats
      WHERE
        predicted_as = 'HS'
      GROUP BY
        author_channel_id, author_display_name, author_image_url;
    """)
    
    res = await self.session.execute(query)
    res = res.all()
    
    return res

  async def get_chats_detected_by_channel_id(self, channel_id):
    query = text(f"""
      SELECT * FROM chats
      WHERE
        author_channel_id = '{channel_id}' AND predicted_as = 'HS'
    """)
    
    res = await self.session.execute(query)
    res = res.all()
    
    return res

  async def bulk(self, schemas: List[dict]):
    chats: List[dict] = schemas

    stmt = insert(Chat).prefix_with("IGNORE").values(chats)
    res = await self.session.execute(stmt)
    await self.session.commit()
    return res


