from fastapi import FastAPI
from app.modules.livestreams.main import router as livestream_router
from app.modules.detection_tasks.main import router as detection_task_router
from app.modules.channels.main import router as channel_router

version_prefix = '/api/v1'

def add_routes(app: FastAPI):
  app.include_router(livestream_router, prefix=version_prefix)
  app.include_router(detection_task_router, prefix=version_prefix)
  app.include_router(channel_router, prefix=version_prefix)
