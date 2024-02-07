import sqlalchemy as sa
import json
from uuid import uuid4
from pydantic.types import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from app.modules.livestreams.model import Livestream


class DetectionTaskBase(SQLModel):
  livestream_id: Optional[int] = Field(default=None, foreign_key='livestreams.id')
  livestream_url_id: Optional[str]
  created_at: Optional[datetime]
  ended_at: Optional[datetime]
  
class DetectionTask(DetectionTaskBase, table=True):
  __tablename__ = 'detection_tasks'

  id: Optional[str] = Field(
    default_factory=uuid4,
    primary_key=True,
    index=True,
    nullable=False,
  )
  created_at: Optional[datetime] = Field(sa_column=sa.Column(sa.DateTime, default=sa.func.now()))
  livestream: Optional[Livestream] = Relationship(
    sa_relationship_kwargs={
      "primaryjoin": "DetectionTask.livestream_id==Livestream.id", 
      "lazy": "joined",
    }
  )
  
class DetectionTaskComparisonData:
  def __init__(self, raw_data):
    self.livestream = self._parse_livestream_data('livestream', raw_data)
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
      'thumbnails': json.loads(raw_data[f'{livestream_key}_thumbnails']) if raw_data[f'{livestream_key}_thumbnails'] else None,
      'livestream_max_viewers': raw_data[f'{livestream_key}_livestream_max_viewers'],
      'channel': {
        'title': raw_data[f'{livestream_key}_channel_title'],
        'thumbnails': json.loads(raw_data[f'{livestream_key}_channel_thumbnails']) if raw_data[f'{livestream_key}_channel_thumbnails'] else None,
      },
      'chats_total': raw_data[f'{livestream_key}_chats_total'],
      'chats_total_hs': raw_data[f'{livestream_key}_chats_total_hs'],
      'chats_total_nhs': raw_data[f'{livestream_key}_chats_total_nhs'],
    }