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
from app.utils.app_util import format_row_to_dict
from app.utils.response_util import res_error
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


router = APIRouter(prefix='/detection_tasks', tags=['Detection Task'])
classifier = Classifier()


@router.get('/info')
async def info():
  return {
    "path": '/detection_tasks'
  }
  
@router.post('/start_detection')
async def start_detection(
  schema: sc.DetectionTaskApiParams,
  channel_repository: ChannelRepository = Depends(get_channel_repository),
  livestream_repository: LivestreamRepository = Depends(get_livestream_repository),
  detection_task_repository: DetectionTaskRepository = Depends(get_detection_task_repository),
): 
  # livestream_a_url_id = 'EjQajAujllI'
  # livestream_b_url_id = 'a4RxLxvgQ2c'
  livestream_a_url_id = schema.livestream_a_url_id
  livestream_b_url_id = schema.livestream_b_url_id
  
  livestream_a_should_start_new_task = False
  livestream_b_should_start_new_task = False
  
  task_predicts_list = []
  
  livestream_a = await livestream_repository.get_by_livestream_url_id(livestream_a_url_id)
  livestream_b = await livestream_repository.get_by_livestream_url_id(livestream_b_url_id)
  
  response_data = None
  response_status = None
  
  if not livestream_a:
    livestream_a = await create_livestream_from_api(livestream_repository, channel_repository, livestream_a_url_id)
    livestream_a_should_start_new_task = True
  if not livestream_b:
    livestream_b = await create_livestream_from_api(livestream_repository, channel_repository, livestream_b_url_id)
    livestream_b_should_start_new_task = True
    
  if livestream_a and livestream_b:
    if livestream_a.livestream_end_time and livestream_b.livestream_end_time:
      raise HTTPException(400, detail='All Livestream has Finished')
      return
      # return 'livestream-finished-all'
    if livestream_a.livestream_end_time or livestream_b.livestream_end_time:
      raise HTTPException(400, detail='Some Livestream has Finished')
      return
      # return 'livestream-finished-some'
    
    schema = sc.DetectionTaskCreate(
      livestream_a_id=livestream_a.id,
      livestream_a_url_id=livestream_a_url_id,
      livestream_b_id=livestream_b.id,
      livestream_b_url_id=livestream_b_url_id,
    )
    
    if livestream_a_should_start_new_task or livestream_b_should_start_new_task:
      response_data = await detection_task_repository.create(schema=schema)
      response_status = 'livestream-new'
    else:
      response_data = await detection_task_repository.get_by_livestream_urls(livestream_a_url_id, livestream_b_url_id)
      response_status = 'livestream-started'
      
    if livestream_a_should_start_new_task:
      task_predicts_list.append(
        task_predicts.s(livestream_a.livestream_livechat_id, livestream_a.id, livestream_a_url_id).set(task_id=f"task_predicts-{livestream_a_url_id}"),
      )
    if livestream_b_should_start_new_task:
      task_predicts_list.append(
        task_predicts.s(livestream_b.livestream_livechat_id, livestream_b.id, livestream_b_url_id).set(task_id=f"task_predicts-{livestream_b_url_id}"),
      )
      
    if len(task_predicts_list) > 0:
      group(*task_predicts_list).apply_async()
    
    response_final = response_data.__dict__
    response_final['status'] = response_status
    return response_final
  
  raise HTTPException(400, detail='Something went wrong, Detection task cannot be executed')

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
async def get_comparison_detail(
  id: str,
  detection_task_repository: DetectionTaskRepository = Depends(get_detection_task_repository),
  chat_repository: ChatRepsository = Depends(get_chat_repository),
):
  detection_task = await detection_task_repository.get(id)
  res = []
  
  if detection_task:
    detection_task = format_row_to_dict(detection_task)
    chats_detected_a = await chat_repository.get_chats_by_livestream_id(livestream_id=detection_task['livestream_a_id'], predicted_as='HS')
    chats_detected_b = await chat_repository.get_chats_by_livestream_id(livestream_id=detection_task['livestream_b_id'], predicted_as='HS')
    
    res = {
      'chats_detected_a': chats_detected_a,
      'chats_detected_b': chats_detected_b,
    }
    
  return res

