import requests
import time
import app.modules.detection_tasks.schemas as sc
from fastapi import Body, APIRouter, Depends
from fastapi_pagination import Page, Params
from celery.result import AsyncResult
from celery import group
from typing import List, Optional
from pandas import DataFrame
from livestream_monitor_classifier import Classifier
from app.helpers import fetcher
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
  livestream_a_url_id = schema.livestream_a_url_id
  livestream_b_url_id = schema.livestream_b_url_id
  
  livestream_a_should_start_new_task = False
  livestream_b_should_start_new_task = False
  
  task_predicts_list = []
  
  livestream_a = await livestream_repository.get_by_livestream_url_id(livestream_a_url_id)
  livestream_b = await livestream_repository.get_by_livestream_url_id(livestream_b_url_id)
  
  if (livestream_a and livestream_a.livestream_end_time) and (livestream_b and livestream_b.livestream_end_time):
    return 'livestream-finished-all'
  if (livestream_a and livestream_a.livestream_end_time) or (livestream_b and livestream_b.livestream_end_time):
    return 'livestream-finished-some'
  
  if not livestream_a:
    livestream_a = await create_livestream_from_api(livestream_repository, channel_repository, livestream_a_url_id)
    livestream_a_should_start_new_task = True
  if not livestream_b:
    livestream_b = await create_livestream_from_api(livestream_repository, channel_repository, livestream_b_url_id)
    livestream_b_should_start_new_task = True
    
  if livestream_a and livestream_b:
    detection_task = await detection_task_repository.get_by_livestream_urls(livestream_a_url_id, livestream_b_url_id)
    
    if not detection_task:
      schema = sc.DetectionTaskCreate(
        livestream_a_id=livestream_a.id,
        livestream_a_url_id=livestream_a_url_id,
        livestream_b_id=livestream_b.id,
        livestream_b_url_id=livestream_b_url_id,
      )
      await detection_task_repository.create(schema=schema)
    
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
    return 'livestream-ok-detection'
  
  return 'livestream-can-not-be-detected'

@router.post('/end_detection', response_model=DetectionTask)
async def end_detection(
  schema: sc.DetectionTaskApiParams,
  repository: DetectionTaskRepository = Depends(get_detection_task_repository),
):
  livestream_a_url_id = schema.livestream_a_url_id
  livestream_b_url_id = schema.livestream_b_url_id
  data = await repository.set_end_detection(livestream_a_url_id, livestream_b_url_id)
  return data

@router.get('/get_comparison_data')
async def get_comparison_data(
  livestream_a_url_id: str,
  livestream_b_url_id: str,
  detection_task_repository: DetectionTaskRepository = Depends(get_detection_task_repository),
):
  data = await detection_task_repository.get_comparison_data(
    livestream_a_url_id, 
    livestream_b_url_id
  )
  return data

@router.get('/test-detection')
async def test_detection(
  chat_repository: ChatRepsository = Depends(get_chat_repository),
  detection_task_repository: DetectionTaskRepository = Depends(get_detection_task_repository),
  livestream_repository: LivestreamRepository = Depends(get_livestream_repository),
):
  # test here put active_live_chat_id
  mnb_classifier_start_ts = time.time()
  
  fetch = fetcher.get_livechat("Cg0KC3pJRnJ4MGlPclcwKicKGFVDQ2U2NE1WQWJ2czdVeTFTS0h0WG5aURILeklGcngwaU9yVzA")
  if fetch.status_code == 200 and fetch.json()['items']:
    livechats = fetch.json()['items']
    chats_formatted = map(lambda livechat: ChatYtData(livechat, livestream_id=1).__dict__, livechats)
    
    df = DataFrame(chats_formatted)
    df['predicted_as'] = classifier.predict_list(df['display_message'].tolist())
    chats_dict = df.to_dict('records')
    
    created = await chat_repository.bulk(chats_dict)
    data = await chat_repository.get_limit_and_count_by_livestream_id(
      limit=created.rowcount, 
      livestream_id=1
    )
  else:
    return None
    
  mnb_classifier_end_ts = time.time()
  print(f"Prediction of mnb_classifier Time [s]: {(mnb_classifier_end_ts-mnb_classifier_start_ts):.5f}")
  
  print('fetch result', fetch.json())
  
  return {
    "info": 'test-detection'
  }

@router.post('/test_set_end', response_model=List[DetectionTask])
async def test_set_end(
  repository: DetectionTaskRepository = Depends(get_detection_task_repository),
):
  data = await repository.set_end_by_related_livestream_url_id('jfKfPfyJRdk')
  return data