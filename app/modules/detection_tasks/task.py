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
from app.socket import socket_manager, format_emit_detection
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
    stop_time_tolerance_seconds = 10 # batas waktu tunggu livechat
    stop_time_detection_seconds = 3600 # batas waktu deteksi dalam detik
    
    chat = pytchat.create(video_id=livestream_url_id)
    async with async_session() as session:
      chat_repository = ChatRepsository(session=session)
      detection_task_repository = DetectionTaskRepository(session=session)
      livestream_repository = LivestreamRepository(session=session)
      time_constraints = 0.8 # batas waktu eksekusi
      current_detection_progress_seconds = time.time()
      result = ''
      
      async def handle_process(start_t, chats):
        nonlocal current_detection_progress_seconds, chat_repository
        
        print(f"WAKTU DIGUNAKAN MENGAMBIL DATA [s]: {(time.time()-start_t):.5f}")
        current_detection_progress_seconds = time.time()
        process_chats_result = process_livechats(chats, livestream_id=livestream_id)
        print(f"WAKTU DIGUNAKAN PROSES DATA [s]: {(time.time()-start_t):.5f}")
        
        if process_chats_result == 'error':
          print('process_chats_result', process_chats_result)
          return 'aborted'
        
        await socket_manager.emit(
          f'livechat_detection_processed', 
          jsonable_encoder(process_chats_result),
          room=livestream_url_id
        )
        
        try :
          await chat_repository.bulk(process_chats_result)
          print(f"WAKTU DIGUNAKAN MENYIMPAN DATA [s]: {(time.time()-start_t):.5f}")
        except:
          await socket_manager.emit(
            f'get_livechat_data_predicted_saved_error-{livestream_url_id}', 
            'error',
            room=livestream_url_id
          )
          
        print(f"WAKTU DIGUNAKAN KESELURUHAN [s]: {(time.time()-start_t):.5f}")
        print('='*30)
        return 'completed'
        
      async def handle_end(message='aborted'):
        await socket_manager.emit(
          'livechat_detection_status', 
          format_emit_detection('error', message),
          room=livestream_url_id
        )
        try:
          await detection_task_repository.set_end_by_related_livestream_url_id(livestream_url_id)
          await livestream_repository.update_livestream_end_time(livestream_url_id)
          return 'aborted'
        except Exception as ex:
          return 'aborted'
        
      while chat.is_alive():
        if result == 'aborted':
          break
        
        start_t = time.time()
        
        chats = json.loads(chat.get().json()) 
        elapsed_detection_time = time.time() - current_detection_progress_seconds
        
        if elapsed_detection_time > stop_time_detection_seconds:
          result = await handle_end('Deteksi dihentikan karena sudah mencapai batas waktu')
        elif elapsed_detection_time > stop_time_tolerance_seconds and len(chats) < 1:
          result = await handle_end(f'Deteksi dihentikan karena server tidak dapat mendapatkan data chat dalam rentan waktu {stop_time_tolerance_seconds}s')
        elif len(chats) > 0:
          result = await asyncio.wait_for(handle_process(start_t, chats), timeout=time_constraints)
          
      if result != 'aborted':
        await socket_manager.emit(
          'livechat_detection_status', 
          format_emit_detection('info', 'Proses deteksi sudah selesai'),
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
  
  
  