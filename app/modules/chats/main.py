import json
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


@router.post('/bulk_dummy')
async def bulk_dummy(
  chat_repository: ChatRepsository = Depends(get_repository)
):
  dummy_data = [
    {
      'author_channel_id': 'UCLryzggpxJfLswnBJ0tEC_Q',
      'author_channel_url': 'http://www.youtube.com/channel/UCLryzggpxJfLswnBJ0tEC_Q',
      'author_display_name': 'LAMBE PEDES',
      'author_image_url': 'https://yt4.ggpht.com/XV-41RCITmWcNV4aGwgvuSmy_9qk8UPByIai7BQJ8_c-Hsg9mpC7y2TH8FukzjWBs3UnNP8pVA=s64-c-k-c0x00ffffff-no-rj',
      'display_message': 'JANGAN KASIH KENDOR RRQ. MISI PEMBALASAN LEG 1',
      'has_display_content': '1',
      'livechat_id': 'ChwKGkNNZmgyWS1sdnZvQ0ZaakV3Z1FkeVhFRDFR',
      'livestream_id': '1',
      'predicted_as': 'NHS'
    },
    {
      'author_channel_id': 'UCaq9dq5_lFDccg9rIF4QZlw',
      'author_channel_url': 'http://www.youtube.com/channel/UCaq9dq5_lFDccg9rIF4QZlw',
      'author_display_name': 'nissa abdullah',
      'author_image_url': 'https://yt4.ggpht.com/ytc/AIf8zZQZ4RFOZLZPnY8w0_ab3Jx5h0iPmVGWSNwCMwtlRlQ=s64-c-k-c0x00ffffff-no-rj',
      'display_message': 'Bismillah RRQ bisa, para kingdom pasti gk profok, dan sllu full respeck',
      'has_display_content': '1',
      'livechat_id': 'ChwKGkNQalZsWi1sdnZvQ0ZSSUdmUW9kbmIwSDVR',
      'livestream_id': '1',
      'predicted_as': 'NHS'
    },
    {
      'author_channel_id': 'UC9yxvitvfzx39DH04VewYqQ',
      'author_channel_url': 'http://www.youtube.com/channel/UC9yxvitvfzx39DH04VewYqQ',
      'author_display_name': 'kayen',
      'author_image_url': 'https://yt4.ggpht.com/7XbsnPLRuYtz31IQpfzrOHgHQxVb8AkgPlYuiwIDh9FocpPCbH0Hf7efskpJ1EIZVrgOcKtUAA=s64-c-k-c0x00ffffff-no-rj',
      'display_message': 'MANA INI KAGA ADA EGGVOS FAM',
      'has_display_content': '1',
      'livechat_id': 'ChwKGkNQYjNxcUNsdnZvQ0ZYRWNmUW9kZHlnRlVB',
      'livestream_id': '1',
      'predicted_as': 'NHS'
    }
  ]

  await chat_repository.bulk(dummy_data)
  return 'success'