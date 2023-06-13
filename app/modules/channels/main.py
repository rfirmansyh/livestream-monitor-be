import requests
import app.modules.channels.schemas as sc
from typing import List
from fastapi import APIRouter, Depends
from app.helpers import fetcher
from .depedencies import get_repository
from .repository import ChannelRepository


router = APIRouter(prefix='/channels', tags=['Channels'])


@router.get('/')
async def index(
  repository: ChannelRepository = Depends(get_repository)
):
  data = await repository.get()
  return data

@router.post('/store_dummy')
async def store_dummy(
  channel_id: str,
  repository: ChannelRepository = Depends(get_repository)
):
  fetch_channel = fetcher.get_channel_detail(channel_id)
  if fetch_channel.status_code == 200 and fetch_channel.json()['items']:
    yt_data_channel = fetch_channel.json()['items'][0]
    
    data = await repository.create_from_api(yt_data_channel)
    
    return data
  
  return 'error'