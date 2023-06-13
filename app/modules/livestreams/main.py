
import app.modules.livestreams.schemas as sc

from fastapi import Body, APIRouter, Depends
from app.helpers import fetcher
from .depedencies import get_repository
from .repository import LivestreamRepository

router = APIRouter(prefix='/livestreams', tags=['Livestreams'])


@router.get('/info')
async def info():
  return {
    "path": '/livestreams'
  }
  
@router.get('/')
async def index(
  repository: LivestreamRepository = Depends(get_repository)
):
  return await repository.all()
  
@router.post('/update_livestream_end_time')
async def update_livestream_end_time(
  repository: LivestreamRepository = Depends(get_repository)
):
  livestream = await repository.update_livestream_end_time("4mXXVFoEW8w")
  return livestream
  
@router.post('/store_dummy', response_model=sc.LivestreamRead)
async def store_dummy(
  livestream_url_id: str,
  repository: LivestreamRepository = Depends(get_repository)
):
  fetch1 = fetcher.get_livestream(livestream_url_id)
  if fetch1.status_code == 200 and fetch1.json()['items']:
    yt_1 = fetch1.json()['items'][0]
    
    data = await repository.create_from_api(
      yt_1,
      livestream_url_id = livestream_url_id
    )
    return data.__dict__
  
  return 'error'