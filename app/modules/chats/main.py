import app.modules.chats.schemas as sc

from fastapi import APIRouter, Depends
from typing import List
from fastapi_pagination import Page, Params
from app.helpers import fetcher
from .depedencies import get_repository
from .repository import ChatRepsository
from .model import Chat, ChatYtData


router = APIRouter(prefix='/chats', tags=['Chats'])


@router.get('/info')
async def info():
  return {
    "path": '/chats'
  }

