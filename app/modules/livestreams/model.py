import sqlalchemy as sa
import json
from datetime import datetime
from pydantic.types import Optional, List
from sqlmodel import Field, SQLModel, Relationship

class LivestreamBase(SQLModel):
  title: str
  description: str = Field(sa_column=sa.Column(sa.Text))
  thumbnails: str
  channel_id: str
  tags: Optional[str]
  livestream_url_id: Optional[str]
  livestream_livechat_id: Optional[str]
  livestream_start_time: Optional[datetime]
  livestream_end_time: Optional[datetime]
  

class Livestream(LivestreamBase, table=True):
  __tablename__ = 'livestreams'

  id: Optional[int] = Field(default=None, primary_key=True)
  created_at: Optional[datetime] = Field(sa_column=sa.Column(sa.DateTime, default=sa.func.now()))
  updated_at: Optional[datetime] = Field(sa_column=sa.Column(sa.DateTime, onupdate=sa.func.now(), default=sa.func.now()))
  

class LivestreamYtData:
  def __init__(self, yt_data, **kwargs):
    self.title = yt_data['snippet']['title']
    self.description = yt_data['snippet']['description']
    self.thumbnails = json.dumps(yt_data['snippet']['thumbnails'])
    self.channel_id = yt_data['snippet']['channelId']
    self.tags = json.dumps(yt_data['snippet']['tags']) if 'tags' in yt_data['snippet'] else None
    self.livestream_start_time = yt_data['liveStreamingDetails']['actualStartTime']
    self.livestream_end_time = yt_data['liveStreamingDetails']['actualEndTime'] if 'actualEndTime' in yt_data['liveStreamingDetails'] else None
    self.livestream_livechat_id = yt_data['liveStreamingDetails']['activeLiveChatId'] if 'activeLiveChatId' in yt_data['liveStreamingDetails'] else None
    self.livestream_url_id = kwargs['livestream_url_id'] if 'livestream_url_id' in kwargs else None