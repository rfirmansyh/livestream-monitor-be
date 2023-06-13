import time
import pytchat
import json
from fastapi.encoders import jsonable_encoder
from celery import shared_task
from celery.app import control
from celery.contrib.abortable import AbortableTask
from app.database import async_session
from app.generators.celery_generator import sync_task
from app.socket import socket_manager
from app.helpers import fetcher
from app.modules.chats.repository import ChatRepsository
from app.modules.detection_tasks.repository import DetectionTaskRepository
from app.modules.livestreams.repository import LivestreamRepository
from app.modules.livestreams.model import LivestreamYtData
from .helper import predict_livechats, update_status, process_livechats

# THIS TASK USED TO DETECT LIVESTREAM STILL ACTIVE OR NOT AND UPDATE IT TO DATABASE
@shared_task(bind=True, name="task_livestream_check", base=AbortableTask)
@sync_task
async def task_livestream_check(
  self,
  livestream_url_id,
): 
  # SHOULD CHECK EVERY 1 HOUR
  # while True:
  #   try:
  #     fetch_livestream = fetcher.get_livestream(livestream_url_id)
  #     if fetch_livestream.status_code == 200 and fetch_livestream.json()['items']:
  #       yt_livestream_data = fetch_livestream.json()['items'][0]
  #       livestreamYtData = LivestreamYtData(yt_livestream_data, livestream_url_id = livestream_url_id)
  #       if livestreamYtData.livestream_end_time:
  #         raise Exception('livestream_ended')
  #     else:
  #       raise Exception('livestream_ended')
  #   except Exception as ex:
  #     revoke(f"task_predicts-{livestream_url_id}").abort()
  #     revoke(f"livestream_url_id-{livestream_url_id}").abort()
  #   time.sleep(10)
  
  # DEMO DUMMY AUTO DISABLE task_predicts ON 1 MINUTE
  time.sleep(60)
  print('ABORT TASK PREDICST')
  task_predicts.AsyncResult(f"task_predicts-LpJ_7ne_4vk").abort()
  # task_predicts.AsyncResult(f"task_predicts-{livestream_url_id}").abort()
  # control.revoke(f"task_predicts-{livestream_url_id}").abort()
  # control.revoke(f"task_livestream_check-{livestream_url_id}").abort()
    
@shared_task(bind=True, name="task_predicts", base=AbortableTask)
@sync_task
async def task_predicts(
  self, 
  active_live_chat_id, 
  livestream_id, 
  livestream_url_id, 
):
  try:
    started_time_detection = time.time()
    started_time_tolerance = time.time()
    stop_time_tolerance_seconds = 10
    stop_time_detection_seconds = 60
    task_livestream_check.apply_async(args=[livestream_url_id], task_id=f"task_livestream_check-{livestream_url_id}")
    chat = pytchat.create(video_id=livestream_url_id)
    async with async_session() as session:
      chat_repository = ChatRepsository(session=session)
      detection_task_repository = DetectionTaskRepository(session=session)
      livestream_repository = LivestreamRepository(session=session)
      
      while chat.is_alive():
        total_time_tolerance_seconds = time.time() - started_time_tolerance
        total_time_detection_seconds = time.time() - started_time_detection
        start_t = time.time()
        chats = json.loads(chat.get().json()) 
        
        # if total_time_detection_seconds > stop_time_detection_seconds:
        #   return f'aborted_maxium_detection_time'
        # if total_time_tolerance_seconds > stop_time_tolerance_seconds and len(chats) > 0:
        #   return f'aborted_no_response_from_livechat_after_{stop_time_tolerance_seconds}s'
        
        if self.is_aborted():
          await socket_manager.emit(
            f'livestream-ended', 
            'ended-expired',
            room=livestream_url_id
          )
          try:
            await detection_task_repository.set_end_by_related_livestream_url_id(livestream_url_id)
            await livestream_repository.update_livestream_end_time(livestream_url_id)
            return 'aborted-success-flow'
            break
          except Exception as ex:
            return 'aborted-failed-flow'
            break
        if len(chats) > 0:
          started_time_tolerance = time.time()
          process_chats_result = process_livechats(chats, livestream_id=livestream_id)
          if process_chats_result == 'error':
            break
          
          await socket_manager.emit(
            f'get_livechat_data_predicted-{livestream_url_id}', 
            jsonable_encoder(process_chats_result),
            room=livestream_url_id
          )
          
          await chat_repository.bulk(process_chats_result)
          end_t = time.time()
          print(f"USED TIME [s]: {(end_t-start_t):.5f}")
        
        time.sleep(3)
      await socket_manager.emit(
        f'status_livestream-{livestream_url_id}', 
        'offline',
        room=livestream_url_id
      )
      return 'finished'
    
  except Exception as ex:
    print('Exception', ex)
    update_status(self)
    await socket_manager.emit(
      f'status_livestream-{livestream_url_id}', 
      'offline',
      room=livestream_url_id
    )
    return 'ended_task_detection'
  