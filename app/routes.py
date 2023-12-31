from fastapi import FastAPI
from app.modules.detection_tasks.main import router as detection_task_router
from app.modules.channels.main import router as channel_router
from app.modules.chats.main import router as chat_router

version_prefix = '/api/v1'

def add_routes(app: FastAPI):
  app.include_router(detection_task_router, prefix=version_prefix)
  app.include_router(channel_router, prefix=version_prefix)
  app.include_router(chat_router, prefix=version_prefix)
