from app.modules.livestreams.model import Livestream
from typing import Optional
from .model import ChatBase

class ChatRead(ChatBase):
  id: Optional[int]

class ChatWithLivestreamRead(ChatRead):
  livestream: Livestream = None

class ChatCreate(ChatBase):
  pass