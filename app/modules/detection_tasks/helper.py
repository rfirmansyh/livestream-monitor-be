from fastapi.encoders import jsonable_encoder
from celery import shared_task, states, uuid, group
from livestream_monitor_classifier import Classifier
from pandas import DataFrame
from app.database import get_session, get_session_raw, async_session
from app.helpers import fetcher
from app.socket import socket_manager
from app.modules.livestreams.repository import LivestreamRepository
from app.modules.chats.model import ChatYtData, ChatPytchatData
from app.modules.chats.repository import ChatRepsository

classifier = Classifier()

def update_status(self):
  self.update_state(
    state=states.FAILURE,
    meta={
      'exc_type': 'FAILURE',
      'exc_message': 'Livechat Session End',
    }
  )

async def create_livestream_from_api(livestream_repository, channel_repository, livestream_url_id, tes_null = False):
  fetch_livestream = fetcher.get_livestream(livestream_url_id)
  livestream = None
  if fetch_livestream.status_code == 200 and fetch_livestream.json()['items']:
    yt_livestream_data = fetch_livestream.json()['items'][0]
    yt_channel_data = None
    
    if yt_livestream_data['snippet']['channelId']:
      fetch_channel = fetcher.get_channel_detail(yt_livestream_data['snippet']['channelId'])
      if fetch_channel.status_code == 200 and fetch_channel.json()['items']:
        yt_data_channel = fetch_channel.json()['items'][0]
        # create channel detail data
        await channel_repository.create_from_api(yt_data_channel) 
    
    if tes_null:
      yt_livestream_data['liveStreamingDetails']['actualEndTime'] = None
    livestream = await livestream_repository.create_from_api(yt_livestream_data, livestream_url_id = livestream_url_id)  
      
  return livestream   

async def predict_livechats(
  active_live_chat_id, 
  livestream_id, 
  livestream_url_id,
  livestream_celery_task_id
):
  try:
    fetch = fetcher.get_livechat(active_live_chat_id)
    print('fetch.json', fetch.json())
    if fetch.status_code == 200:
      async with async_session() as session:
        chat_repository = ChatRepsository(session=session)
        livestream_repository = LivestreamRepository(session=session)
        
        livechats = fetch.json()['items']
        chats_formatted = map(lambda livechat: ChatYtData(livechat, livestream_id=1).__dict__, livechats)
        
        df = DataFrame(chats_formatted)
        df['predicted_as'] = classifier.predict_list(df['display_message'].tolist())
        df_dict = df.to_dict('records')
        
        await socket_manager.emit(
          f'get_livechat_data_predicted-{livestream_url_id}', 
          jsonable_encoder(df_dict),
          room=livestream_url_id
        )
        
        # created = await chat_repository.bulk(chats_dict)
        # data = await chat_repository.get_limit_and_count_by_livestream_id(
        #   limit=created.rowcount, 
        #   livestream_id=livestream_id
        # )
        
        await session.close()
        yield 'success'
    else:
      raise Exception('Get livechat error')
  except Exception as ex:
    print('Exception in predict_livechats', ex)
    yield None
  
def process_livechats(
  chats,
  livestream_id
):
  try:
    chats_formatted = map(lambda chat: ChatPytchatData(chat, livestream_id=livestream_id).__dict__, chats)
    df = DataFrame(chats_formatted)
    df['predicted_as'] = classifier.predict_list(df['display_message'].tolist())
    df_dict = df.to_dict('records')
    
    return df_dict
  except Exception as ex:
    print(json.loads(chats))
    print('Exception in process_livechats', ex)
    return 'error'