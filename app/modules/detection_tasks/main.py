import requests
import time
import app.modules.detection_tasks.schemas as sc
from fastapi import Body, APIRouter, Depends
from fastapi_pagination import Page, Params
from fastapi.exceptions import HTTPException
from celery.result import AsyncResult
from celery import group
from typing import List, Optional
from pandas import DataFrame
from livestream_monitor_classifier import Classifier
from app.helpers import fetcher
from app.utils.app_util import format_row_to_dict, CustomException
from app.utils.celery_util import get_task_info
from app.socket import socket_manager
from app.modules.channels.repository import ChannelRepository
from app.modules.channels.depedencies import get_repository as get_channel_repository
from app.modules.chats.repository import ChatRepsository
from app.modules.chats.depedencies import get_repository as get_chat_repository
from app.modules.chats.model import Chat, ChatYtData
from app.modules.livestreams.repository import LivestreamRepository
from app.modules.livestreams.depedencies import get_repository as get_livestream_repository
from .depedencies import get_repository as get_detection_task_repository
from .repository import DetectionTaskRepository
from .helper import create_livestream_from_api
from .task import task_predicts
from .model import DetectionTask


router = APIRouter()
classifier = Classifier()


@router.post('/start_detection')
async def start_detection(
  schema: sc.DetectionTaskApiParams,
  channel_repository: ChannelRepository = Depends(get_channel_repository),
  livestream_repository: LivestreamRepository = Depends(get_livestream_repository),
  detection_task_repository: DetectionTaskRepository = Depends(get_detection_task_repository),
): 
  try:
    livestream_url_id = schema.livestream_url_id
    livestream_should_start_new_task = False
    task_runner = None
    response_data = None
    response_type = 'info'
    response_message = None
    
    livestream = await livestream_repository.get_by_livestream_url_id(livestream_url_id)
    
    if not livestream:
      livestream = await create_livestream_from_api(livestream_repository, channel_repository, livestream_url_id)
      livestream_should_start_new_task = True
      
    if livestream:
      schema = sc.DetectionTaskCreate(
        livestream_id=livestream.id,
        livestream_url_id=livestream_url_id,
      )
      
      if livestream_should_start_new_task and not livestream.livestream_end_time:
        response_data = await detection_task_repository.create(schema=schema)
        response_type = 'success'
        response_message = 'Berhasil memulai deteksi baru'
      elif livestream.livestream_end_time:
        response_data = await detection_task_repository.create(schema=schema)
        response_type = 'warning'
        response_message = 'Berhasil, tetapi sesi livestream ini sudah expired'
      else:
        response_data = await detection_task_repository.get_by_livestream_url(livestream_url_id)
        response_type = 'success'
        response_message = 'Berhasil mengikuti sesi deteksi yang sudah ada'
        
      if livestream_should_start_new_task:
        task_runner = task_predicts.s(livestream.livestream_livechat_id, livestream.id, livestream_url_id).set(task_id=f"task_predicts-{livestream_url_id}")
        
      if task_runner:
        task_runner.apply_async()
      
    response_final = response_data.__dict__ 
    response_final['type'] = response_type
    response_final['message'] = response_message
    return response_final
  except CustomException as ce:
    message = ce.details.get('detail', 'Upps server lagi ada kendala, deteksi tidak dapat dijalankan')
    raise HTTPException(400, detail=message)
  

@router.post('/end_detection', response_model=DetectionTask)
async def end_detection(
  schema: sc.DetectionTaskEndApiParams,
  repository: DetectionTaskRepository = Depends(get_detection_task_repository),
):
  data = await repository.set_end_detection(id=schema.id)
  return data

@router.get('/get_all_comparison')
async def get_all_comparison(
  detection_task_repository: DetectionTaskRepository = Depends(get_detection_task_repository),
):
  data = await detection_task_repository.get_all_comparison()
  return data

@router.get('/get_comparison_detail')
async def get_comparison_detail(
  id: str,
  detection_task_repository: DetectionTaskRepository = Depends(get_detection_task_repository),
):
  data = await detection_task_repository.get_comparison_detail(id)
  return data

@router.get('/get_chats_detected')
async def get_chats_detected(
  id: str,
  detection_task_repository: DetectionTaskRepository = Depends(get_detection_task_repository),
  chat_repository: ChatRepsository = Depends(get_chat_repository),
):
  detection_task = await detection_task_repository.get(id)
  res = []
  
  if detection_task:
    detection_task = format_row_to_dict(detection_task)
    chats_detected = await chat_repository.get_chats_by_livestream_id(livestream_id=detection_task['livestream_id'], predicted_as='HS')
    
    res = chats_detected
    
  return res

