import pytchat
import json
import pprint
from pandas import DataFrame
from livestream_monitor_classifier import Classifier

class ChatPytchatData:
  def __init__(self, pytchat_data, **kwargs):
    self.livechat_id = pytchat_data['id']
    self.has_display_content = '1'
    self.display_message = pytchat_data['message'] if pytchat_data['message'] else "No Message"
    self.author_channel_id = pytchat_data['author']['channelId']
    self.author_channel_url = pytchat_data['author']['channelUrl']
    self.author_display_name = pytchat_data['author']['name']
    self.author_image_url = pytchat_data['author']['imageUrl']
    self.predicted_as = kwargs['predicted_as'] if 'predicted_as' in kwargs else None
    self.livestream_id = kwargs['livestream_id'] if 'livestream_id' in kwargs else None
 
pp = pprint.PrettyPrinter(indent=4)    
classifier = Classifier()    

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
    print('Exception in process_livechats', ex)
    return 'error'
  
livestream_id = "iyZsFr9XZH0"
livestream_chat = pytchat.create(video_id=livestream_id)
while livestream_chat.is_alive():
  chats = json.loads(livestream_chat.get().json())
  if len(chats) > 0:
    chats_len_3 = [chats[0], chats[1], chats[2]]
    process_chats_result = process_livechats(chats_len_3, livestream_id=livestream_id)
    pprint.pprint(process_chats_result)
    livestream_chat.terminate()
    break  
  break