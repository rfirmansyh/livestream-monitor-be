import requests
from operator import itemgetter
from config import base_config

payload_yt_livestream = {
  'part': 'liveStreamingDetails,snippet',
  'key': base_config.BASE_YT_KEY
}
payload_yt_channel = {
  'part': 'snippet,statistics',
  'key': base_config.BASE_YT_KEY
}
payload_yt_livechat = {
  'part': 'snippet,authorDetails',
  'key': base_config.BASE_YT_KEY,
  # 1 - 74
  'maxResults': 74,
}

def get_livestream(livestream_id: str):
  global payload_yt_livestream
  req_payload = {**payload_yt_livestream, **{ 'id': livestream_id }}
  res = requests.get(f'{base_config.BASE_YT_API}/videos', params=req_payload)
  return res

def get_channel_detail(channel_id: str):
  global payload_yt_channel
  req_payload = {**payload_yt_channel, 'id': channel_id}
  res = requests.get(f'{base_config.BASE_YT_API}/channels', params=req_payload)
  return res

def get_livechat(active_live_chat_id: str):
  global payload_yt_livechat
  req_payload = {**payload_yt_livechat, **{ 'liveChatId': active_live_chat_id }}
  res = requests.get(f'{base_config.BASE_YT_API}/liveChat/messages', params=req_payload)
  return res