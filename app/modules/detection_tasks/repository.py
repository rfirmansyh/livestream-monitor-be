import app.modules.detection_tasks.schemas as sc
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, text, update, or_, and_
from sqlalchemy import literal_column
from .model import DetectionTask, DetectionTaskComparisonData


class DetectionTaskRepository:
  def __init__(self, session: AsyncSession):
    self.session = session
    
  async def get(self, id: str) -> Optional[DetectionTask]:
    q = select(DetectionTask).where(DetectionTask.id == id)
    res = await self.session.execute(q)
    return res.scalar()
  
  async def create(self, schema: sc.DetectionTaskCreate):
    detection_task = DetectionTask(**schema.dict())
    self.session.add(detection_task)
    await self.session.commit()
    await self.session.refresh(detection_task)

    return detection_task
  
  async def get_by_livestream_url(self, livestream_url_id):
    q = (
      select(DetectionTask)
      .where(literal_column('livestream_url_id') == livestream_url_id)
    )
    res = await self.session.execute(q)
    return res.scalar()
  
  async def get_all_comparison(self):
    def where_case(column):
      return f"""
        CASE WHEN {column} IS NOT NULL
          THEN c.created_at <= {column}
          ELSE c.created_at
        END
      """
      
    query = text(f"""
      SELECT 
        dt.id AS id,
        ls.title AS livestream_title,
        ls.description AS livestream_description,
        ls.thumbnails AS livestream_thumbnails,
        ls.livestream_url_id AS livestream_livestream_url_id,
        ls.livestream_max_viewers AS livestream_livestream_max_viewers,
        ca.title AS livestream_channel_title,
        ca.thumbnails AS livestream_channel_thumbnails,
        (SELECT COUNT(c.livechat_id) FROM `chats` AS c WHERE c.livestream_id = dt.livestream_id AND {where_case('dt.ended_at')}) as livestream_chats_total,
        (SELECT COUNT(c.livechat_id) FROM `chats` AS c WHERE c.predicted_as = 'HS' AND c.livestream_id = dt.livestream_id AND {where_case('dt.ended_at')}) as livestream_chats_total_hs,
        (SELECT COUNT(c.livechat_id) FROM `chats` AS c WHERE c.predicted_as = 'NHS' AND c.livestream_id = dt.livestream_id AND {where_case('dt.ended_at')}) as livestream_chats_total_nhs
      FROM `detection_tasks` AS dt
      JOIN `livestreams` AS ls ON ls.id = dt.livestream_id
      JOIN `channels` AS ca ON ca.id = ls.channel_id
      GROUP BY dt.id
    """)
     
    res = await self.session.execute(query)
    return res.all()
  
  async def get_comparison_detail(self, id: str):
    def where_case(column):
      return f"""
        CASE WHEN {column} IS NOT NULL
          THEN c.created_at <= {column}
          ELSE c.created_at
        END
      """
      
    query = text(f"""
      SELECT 
        dt.id AS id,
        ls.title AS livestream_title,
        ls.description AS livestream_description,
        ls.thumbnails AS livestream_thumbnails,
        ls.livestream_url_id AS livestream_livestream_url_id,
        ls.livestream_max_viewers AS livestream_livestream_max_viewers,
        ca.title AS livestream_channel_title,
        ca.thumbnails AS livestream_channel_thumbnails,
        (SELECT COUNT(c.livechat_id) FROM `chats` AS c WHERE c.livestream_id = dt.livestream_id AND {where_case('dt.ended_at')}) as livestream_chats_total,
        (SELECT COUNT(c.livechat_id) FROM `chats` AS c WHERE c.predicted_as = 'HS' AND c.livestream_id = dt.livestream_id AND {where_case('dt.ended_at')}) as livestream_chats_total_hs,
        (SELECT COUNT(c.livechat_id) FROM `chats` AS c WHERE c.predicted_as = 'NHS' AND c.livestream_id = dt.livestream_id AND {where_case('dt.ended_at')}) as livestream_chats_total_nhs
      FROM `detection_tasks` AS dt
      JOIN `livestreams` AS ls ON ls.id = dt.livestream_id
      JOIN `channels` AS ca ON ca.id = ls.channel_id
      WHERE dt.id = '{id}'
      GROUP BY dt.id
    """)
     
    res = await self.session.execute(query)
    return res.first()
  
  async def set_end_by_related_livestream_url_id(self, livestream_url_id):
    select_operator = or_(
      DetectionTask.livestream_url_id == livestream_url_id,
    ) 
    q = (
      update(DetectionTask)
        .where(select_operator)
        .values({ 'ended_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S') })
    )
    q_select = select(DetectionTask).where(select_operator)
    
    await self.session.execute(q)
    await self.session.commit()
    res = await self.session.execute(q_select)
    return res.scalars().all()
  
  async def set_end_detection(self, id: str):
    select_operator = DetectionTask.id == id; 
    q = (
      update(DetectionTask)
        .where(select_operator)
        .values({ 'ended_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S') })
    )
    q_select = select(DetectionTask).where(select_operator)
    
    await self.session.execute(q)
    await self.session.commit()
    res = await self.session.execute(q_select)
    return res.scalar_one_or_none()