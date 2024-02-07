import socketio
import asyncio

from celery import current_app as current_celery_app
from celery.result import AsyncResult
from celery.signals import worker_shutdown
from config import base_config
from app.socket import socket_manager, format_emit_detection

def create_celery():
  celery_app = current_celery_app
  celery_app.config_from_object(base_config, namespace="CELERY")
  
  return celery_app


def update_celery_task_status_socketio(task_id):
  """
  This function would be called in Celery worker
  https://python-socketio.readthedocs.io/en/latest/server.html#emitting-from-external-processes
  """
  # connect to the redis queue as an external process
  external_sio = socketio.RedisManager(base_config.WS_MESSAGE_QUEUE, write_only=True)
  # emit an event
  external_sio.emit("livechat_detection_status", get_task_info(task_id), room=task_id, namespace="/task_status")

@worker_shutdown.connect
def handle_worker_shutdown(**kwargs):
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  loop.run_until_complete(
    socket_manager.emit(
      'livechat_detection_status', 
      format_emit_detection('error', 'Upps server lagi ada kendala, deteksi dihentikan tiba-tiba') , room=kwargs.get('task_id')
    )
  )

def get_task_info(taks_id):
  task = AsyncResult(taks_id)
  state = task.state
  
  if state == "FAILURE":
    error = str(task.result)
    response = {
      "state": task.state,
      "error": error,
    }
  else:
    response = {
      "state": task.state,
    }
  return response


