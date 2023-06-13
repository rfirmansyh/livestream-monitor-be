from pydantic.types import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from app.modules.livestreams.model import Livestream


class DetectionTaskBase(SQLModel):
  livestream_a_id: Optional[int] = Field(default=None, foreign_key='livestreams.id')
  livestream_a_url_id: Optional[str]
  livestream_b_id: Optional[int] = Field(default=None, foreign_key='livestreams.id')
  livestream_b_url_id: Optional[str]
  created_at: Optional[datetime]
  ended_at: Optional[datetime]
  
  
class DetectionTask(DetectionTaskBase, table=True):
  __tablename__ = 'detection_tasks'

  id: Optional[int] = Field(default=None, primary_key=True)
  livestream_a: Optional[Livestream] = Relationship(
    sa_relationship_kwargs={
      "primaryjoin": "DetectionTask.livestream_a_id==Livestream.id", 
      "lazy": "joined",
    }
  )
  livestream_b: Optional[Livestream] = Relationship(
    sa_relationship_kwargs={
      "primaryjoin": "DetectionTask.livestream_b_id==Livestream.id", 
      "lazy": "joined"
    }
  )
  
# query = text(f"""
#   SELECT 
#     la.title AS livestream_a_title,
#     lb.title AS livestream_b_title,
#     lb.description AS livestream_b_description,
#     la.description AS livestream_a_description,
#     la.livestream_url_id AS livestream_a_livestream_url_id,
#     lb.livestream_url_id AS livestream_b_livestream_url_id,
#     la.livestream_max_viewers AS livestream_a_livestream_max_viewers,
#     lb.livestream_max_viewers AS livestream_b_livestream_max_viewers,
#     ca.title AS channel_a_title,
#     cb.title AS channel_b_title,
#     (SELECT COUNT(c.livechat_id) FROM `chats` AS c WHERE c.livestream_id = dt.livestream_a_id) as livestream_a_chats_total,
#     (SELECT COUNT(c.livechat_id) FROM `chats` AS c WHERE c.livestream_id = dt.livestream_b_id) as livestream_b_chats_total,
#     (SELECT COUNT(c.livechat_id) FROM `chats` AS c WHERE c.predicted_as = 'HS' AND c.livestream_id = dt.livestream_a_id) as livestream_a_chats_total_hs,
#     (SELECT COUNT(c.livechat_id) FROM `chats` AS c WHERE c.predicted_as = 'HS' AND c.livestream_id = dt.livestream_b_id) as livestream_b_chats_total_hs,
#     (SELECT COUNT(c.livechat_id) FROM `chats` AS c WHERE c.predicted_as = 'NHS' AND c.livestream_id = dt.livestream_a_id) as livestream_a_chats_total_nhs,
#     (SELECT COUNT(c.livechat_id) FROM `chats` AS c WHERE c.predicted_as = 'NHS' AND c.livestream_id = dt.livestream_b_id) as livestream_b_chats_total_nhs,
#     (SELECT COUNT(c.livechat_id) FROM `chats` AS c WHERE c.predicted_as = 'HS' AND (c.livestream_id = dt.livestream_a_id OR c.livestream_id = dt.livestream_b_id)) as current_detection_chats_total_hs,
#     (SELECT COUNT(c.livechat_id) FROM `chats` AS c WHERE c.predicted_as = 'NHS' AND (c.livestream_id = dt.livestream_a_id OR c.livestream_id = dt.livestream_b_id)) as current_detection_chats_total_nhs
#   FROM `detection_tasks` AS dt
#   JOIN `livestreams` AS la ON la.id = dt.livestream_a_id
#   JOIN `livestreams` AS lb ON lb.id = dt.livestream_b_id
#   JOIN `channels` AS ca ON ca.channel_id = la.channel_id
#   JOIN `channels` AS cb ON cb.channel_id = lb.channel_id
#   WHERE `livestream_a_url_id` = '{livestream_a_url_id}' AND `livestream_b_url_id` = '{livestream_b_url_id}'
# """)
class DetectionTaskComparisonData:
  def __init__(self, raw_data):
    self.livestream_a = self._parse_livestream_data('livestream_a', raw_data)
    self.livestream_b = self._parse_livestream_data('livestream_b', raw_data)
    self.current_detection_chats_total_hs = raw_data['current_detection_chats_total_hs']
    self.current_detection_chats_total_nhs = raw_data['current_detection_chats_total_nhs']
  
  @classmethod
  def get_formatted_data(cls, raw_data):
    if raw_data:
      return cls(raw_data)
    return None
  
  def _parse_livestream_data(self, livestream_key, raw_data):
    return {
      'title': raw_data[f'{livestream_key}_title'],
      'description': raw_data[f'{livestream_key}_description'],
      'livestream_url_id': raw_data[f'{livestream_key}_livestream_url_id'],
      'livestream_max_viewers': raw_data[f'{livestream_key}_livestream_max_viewers'],
      'channel': {
        'title': raw_data[f'{livestream_key}_channel_title'],
      },
      'chats_total': raw_data[f'{livestream_key}_chats_total'],
      'chats_total_hs': raw_data[f'{livestream_key}_chats_total_hs'],
      'chats_total_nhs': raw_data[f'{livestream_key}_chats_total_nhs'],
    }