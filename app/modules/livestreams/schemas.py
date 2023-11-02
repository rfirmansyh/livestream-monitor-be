from datetime import datetime
from pydantic import BaseModel
from pydantic.types import Optional, List
from .model import LivestreamBase
from app.modules.chats.model import Chat


class LivestreamRead(LivestreamBase):
  id: Optional[int]
  created_at: Optional[datetime]
  updated_at: Optional[datetime]