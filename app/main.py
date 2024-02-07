# FILE PADA app.main atau app/main.py
import time
from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi.middleware.cors import CORSMiddleware
from config import base_config

from app.socket import add_socket
from app.routes import add_routes
from app.utils.celery_util import create_celery

def init_app() -> FastAPI:
  
  app = FastAPI(
    title='Aplikasi Deteksi Ujaran Kebencian API',
    description='API Service untuk Aplikasi Deteksi Ujaran Kebencian API',
    version='1',
  )

  app.add_middleware(
    CORSMiddleware,
    allow_origins=base_config.BASE_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
  )
  
  app.celery_app = create_celery()
  
  add_routes(app)
  add_pagination(app)
  add_socket(app)

  @app.middleware("http")
  async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    return response

  return app

