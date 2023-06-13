import sqlalchemy as sa
import json
from datetime import datetime
from pydantic.types import Optional
from sqlmodel import Field, SQLModel

class ChannelBase(SQLModel):
  channel_id: str
  thumbnails: str
  title: str
  description: str = Field(sa_column=sa.Column(sa.Text))
  
class Channel(ChannelBase, table=True):
  __tablename__ = 'channels'

  channel_id: str = Field(sa_column=sa.Column(sa.String(255), primary_key=True, unique=True))
  created_at: Optional[datetime] = Field(sa_column=sa.Column(sa.DateTime, default=sa.func.now()))
  updated_at: Optional[datetime] = Field(sa_column=sa.Column(sa.DateTime, onupdate=sa.func.now(), default=sa.func.now()))
  
class ChannelYtData:
  def __init__(self, yt_data, **kwargs):
    self.channel_id = yt_data['id']
    self.title = yt_data['snippet']['title']
    self.description = yt_data['snippet']['description']
    self.thumbnails = json.dumps(yt_data['snippet']['thumbnails'])