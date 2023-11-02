from pydantic import BaseModel
from app.modules.livestreams.model import Livestream
from typing import Optional
from .model import DetectionTaskBase


class DetectionTaskRead(DetectionTaskBase):
  id: Optional[str]


class DetectionTaskWithLivestreamRead(DetectionTaskRead):
  livestream_a: Livestream = None
  livestream_b: Livestream = None


class DetectionTaskCreate(DetectionTaskBase):
  pass


class DetectionTaskApiParams(BaseModel):
  livestream_a_url_id: str
  livestream_b_url_id: str
  
class DetectionTaskEndApiParams(BaseModel):
  id: str
  