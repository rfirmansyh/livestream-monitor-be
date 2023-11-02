from typing import Optional
from .model import ChannelBase


class ChannelRead(ChannelBase):
  id: Optional[str]
