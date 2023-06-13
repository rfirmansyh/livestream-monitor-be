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
    
  async def all(self):
    query = select(DetectionTask)
    res = await self.session.execute(query)
    return res.scalars().all()
  
  async def get(self, id: int) -> Optional[DetectionTask]:
    q = select(DetectionTask).where(DetectionTask.id == id)
    res = await self.session.execute(q)
    return res.scalar_one_or_none()
  
  async def create(self, schema: sc.DetectionTaskCreate):
    detection_task = DetectionTask(**schema.dict())
    self.session.add(detection_task)
    await self.session.commit()
    await self.session.refresh(detection_task)

    return detection_task
  
  async def get_by_livestream_urls(self, livestream_a_url_id, livestream_b_url_id):
    q = (
      select(DetectionTask)
      .where(literal_column('livestream_a_url_id') == livestream_a_url_id)
      .where(literal_column('livestream_b_url_id') == livestream_b_url_id)
    )
    res = await self.session.execute(q)
    print(res)
    return res.scalar_one_or_none()
  
  async def get_comparison_data(self, livestream_a_url_id, livestream_b_url_id):
    query = text(f"""
      SELECT 
        la.title AS livestream_a_title,
        lb.title AS livestream_b_title,
        lb.description AS livestream_b_description,
        la.description AS livestream_a_description,
        la.livestream_url_id AS livestream_a_livestream_url_id,
        lb.livestream_url_id AS livestream_b_livestream_url_id,
        la.livestream_max_viewers AS livestream_a_livestream_max_viewers,
        lb.livestream_max_viewers AS livestream_b_livestream_max_viewers,
        ca.title AS livestream_a_channel_title,
        cb.title AS livestream_b_channel_title,
        (SELECT COUNT(c.livechat_id) FROM `chats` AS c WHERE c.livestream_id = dt.livestream_a_id AND (c.created_at >= dt.created_at AND c.created_at <= dt.ended_at)) as livestream_a_chats_total,
        (SELECT COUNT(c.livechat_id) FROM `chats` AS c WHERE c.livestream_id = dt.livestream_b_id AND (c.created_at >= dt.created_at AND c.created_at <= dt.ended_at)) as livestream_b_chats_total,
        (SELECT COUNT(c.livechat_id) FROM `chats` AS c WHERE c.predicted_as = 'HS' AND c.livestream_id = dt.livestream_a_id AND (c.created_at >= dt.created_at AND c.created_at <= dt.ended_at)) as livestream_a_chats_total_hs,
        (SELECT COUNT(c.livechat_id) FROM `chats` AS c WHERE c.predicted_as = 'HS' AND c.livestream_id = dt.livestream_b_id AND (c.created_at >= dt.created_at AND c.created_at <= dt.ended_at)) as livestream_b_chats_total_hs,
        (SELECT COUNT(c.livechat_id) FROM `chats` AS c WHERE c.predicted_as = 'NHS' AND c.livestream_id = dt.livestream_a_id AND (c.created_at >= dt.created_at AND c.created_at <= dt.ended_at)) as livestream_a_chats_total_nhs,
        (SELECT COUNT(c.livechat_id) FROM `chats` AS c WHERE c.predicted_as = 'NHS' AND c.livestream_id = dt.livestream_b_id AND (c.created_at >= dt.created_at AND c.created_at <= dt.ended_at)) as livestream_b_chats_total_nhs,
        (SELECT COUNT(c.livechat_id) FROM `chats` AS c WHERE c.predicted_as = 'HS' AND (c.livestream_id = dt.livestream_a_id OR c.livestream_id = dt.livestream_b_id) AND (c.created_at >= dt.created_at AND c.created_at <= dt.ended_at)) as current_detection_chats_total_hs,
        (SELECT COUNT(c.livechat_id) FROM `chats` AS c WHERE c.predicted_as = 'NHS' AND (c.livestream_id = dt.livestream_a_id OR c.livestream_id = dt.livestream_b_id) AND (c.created_at >= dt.created_at AND c.created_at <= dt.ended_at)) as current_detection_chats_total_nhs
      FROM `detection_tasks` AS dt
      JOIN `livestreams` AS la ON la.id = dt.livestream_a_id
      JOIN `livestreams` AS lb ON lb.id = dt.livestream_b_id
      JOIN `channels` AS ca ON ca.channel_id = la.channel_id
      JOIN `channels` AS cb ON cb.channel_id = lb.channel_id
      WHERE `livestream_a_url_id` = '{livestream_a_url_id}' AND `livestream_b_url_id` = '{livestream_b_url_id}'
    """)
    
    res = await self.session.execute(query)
    return DetectionTaskComparisonData.get_formatted_data(res.first())
  
  async def set_end_by_related_livestream_url_id(self, livestream_url_id):
    select_operator = or_(
      DetectionTask.livestream_a_url_id == livestream_url_id,
      DetectionTask.livestream_b_url_id == livestream_url_id
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
  
  async def set_end_detection(self, livestream_a_url_id, livestream_b_url_id):
    select_operator = and_(
      DetectionTask.livestream_a_url_id == livestream_a_url_id,
      DetectionTask.livestream_b_url_id == livestream_b_url_id
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
    return res.scalar_one_or_none()