import sqlalchemy as sa
from datetime import datetime
from pydantic.types import Optional
from sqlmodel import Field, SQLModel, Relationship
from app.modules.livestreams.model import Livestream

class ChatBase(SQLModel):
  livechat_id: Optional[str]
  has_display_content: Optional[int]
  display_message: Optional[str]
  author_channel_id: Optional[str]
  author_channel_url: Optional[str]
  author_display_name: Optional[str]
  author_image_url: Optional[str]
  predicted_as: Optional[str]
  livestream_id: Optional[int] = Field(default=None, foreign_key='livestreams.id')


class Chat(ChatBase, table=True):
  __tablename__ = 'chats'

  id: Optional[int] = Field(default=None, primary_key=True)
  created_at: Optional[datetime] = Field(sa_column=sa.Column(sa.DateTime, default=sa.func.now()))
  livestream: Optional[Livestream] = Relationship(back_populates="chats", sa_relationship_kwargs={"lazy": "selectin"})


class ChatYtData:
  def __init__(self, yt_data, **kwargs):
    self.livechat_id = yt_data['id']
    self.has_display_content = yt_data['snippet']['hasDisplayContent']
    self.display_message = yt_data['snippet']['displayMessage']
    self.author_channel_id = yt_data['authorDetails']['channelId']
    self.author_channel_url = yt_data['authorDetails']['channelUrl']
    self.author_display_name = yt_data['authorDetails']['displayName']
    self.author_image_url = yt_data['authorDetails']['profileImageUrl']
    self.predicted_as = kwargs['predicted_as'] if 'predicted_as' in kwargs else None
    self.livestream_id = kwargs['livestream_id'] if 'livestream_id' in kwargs else None
    
class ChatPytchatData:
  def __init__(self, pytchat_data, **kwargs):
    self.livechat_id = pytchat_data['id']
    self.has_display_content = '1'
    self.display_message = pytchat_data['message'] if pytchat_data['message'] else "No Message"
    self.author_channel_id = pytchat_data['author']['channelId']
    self.author_channel_url = pytchat_data['author']['channelUrl']
    self.author_display_name = pytchat_data['author']['name']
    self.author_image_url = pytchat_data['author']['imageUrl']
    self.predicted_as = kwargs['predicted_as'] if 'predicted_as' in kwargs else None
    self.livestream_id = kwargs['livestream_id'] if 'livestream_id' in kwargs else None