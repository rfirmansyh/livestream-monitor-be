import pytchat
import time

chat = pytchat.create(video_id="zyvGw2a2D_U")
print('start')
print(chat.get())
# while chat.is_alive():
#   print('alive')
#   time.sleep(2)
print('end')