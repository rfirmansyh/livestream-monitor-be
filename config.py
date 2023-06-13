import pathlib
from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
  APP_NAME = 'Livestream Monitor API'
  BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent
  BASE_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
  ]
  CELERY_RESULT_ENGINE_OPTIONS = {"echo": True}
  BASE_YT_API: str
  BASE_YT_KEY: str
  DATABASE_URL: str
  CELERY_BROKER_URL: str
  CELERY_RESULT_BACKEND: str
  WS_MESSAGE_QUEUE: str
  
  class Config:
    env_file = '.env'
    env_file_encoding = 'utf-8'
    
@lru_cache()
def get_config():
  return Settings()

get_config.cache_clear()

base_config = get_config()
# print(base_config)