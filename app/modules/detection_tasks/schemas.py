from pydantic import BaseModel
from app.modules.livestreams.model import Livestream
from typing import Optional
from .model import DetectionTaskBase


class DetectionTaskRead(DetectionTaskBase):
  id: Optional[str]


class DetectionTaskCreate(DetectionTaskBase):
  pass


class DetectionTaskApiParams(BaseModel):
  livestream_url_id: str
  
class DetectionTaskEndApiParams(BaseModel):
  id: str
  