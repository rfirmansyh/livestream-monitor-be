import requests
from typing import List
from fastapi import APIRouter, Depends
from app.helpers import fetcher
from .depedencies import get_repository
from .repository import ChannelRepository


router = APIRouter()


@router.get('/get_with_summary')
async def get_with_summary(
  repository: ChannelRepository = Depends(get_repository)
):
  data = await repository.get_with_summary()
  return data
