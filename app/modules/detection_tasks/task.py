import time
import pytchat
import json
import asyncio
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
from .helper import update_status, process_livechats

    
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
    stop_time_detection_seconds = 3600 # force stop detection 
    
    chat = pytchat.create(video_id=livestream_url_id)
    async with async_session() as session:
      chat_repository = ChatRepsository(session=session)
      detection_task_repository = DetectionTaskRepository(session=session)
      livestream_repository = LivestreamRepository(session=session)
      time_constraints = 0.8
      
      async def handle_end(message='aborted'):
        await socket_manager.emit(
          f'livestream-ended', 
          'ended-expired',
          room=livestream_url_id
        )
        try:
          await detection_task_repository.set_end_by_related_livestream_url_id(livestream_url_id)
          await livestream_repository.update_livestream_end_time(livestream_url_id)
          return message
        except Exception as ex:
          return 'aborted-with-failed-flow' # not saved end time
      
      while chat.is_alive():
        started_time_tolerance = time.time() # task dimulai
        total_time_tolerance_seconds = time.time() - started_time_tolerance
        total_time_detection_seconds = time.time() - started_time_detection
        
        start_t = time.time()
        chats = json.loads(chat.get().json()) 
        
        if total_time_detection_seconds > stop_time_detection_seconds:
          return await handle_end(f'aborted_maxium_detection_time')
          break
        if total_time_tolerance_seconds > stop_time_tolerance_seconds and len(chats) < 1:
          return await handle_end(f'aborted_no_response_from_livechat_after_{stop_time_tolerance_seconds}s')
          break
        
        if len(chats) > 0:
          process_chats_result = process_livechats(chats, livestream_id=livestream_id)
          if process_chats_result == 'error':
            break
          
          await socket_manager.emit(
            f'get_livechat_data_predicted-{livestream_url_id}', 
            jsonable_encoder(process_chats_result),
            room=livestream_url_id
          )
          
          try :
            await asyncio.wait_for(chat_repository.bulk(process_chats_result), timeout=time_constraints)
          except:
            await socket_manager.emit(
              f'get_livechat_data_predicted_saved_error-{livestream_url_id}', 
              'error',
              room=livestream_url_id
            )
            
        end_t = time.time() # task selesai
        print(f"USED TIME [s]: {(end_t-start_t):.5f}")
        
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
  