import socketio
from .helpers.socket_manager import SocketManager
from config import base_config

socket_manager = SocketManager(origins=base_config.BASE_ORIGINS)

def handle_connect(sid, environ):
  print(f'Socket connected with sid {sid} kontol')
def handle_join(sid, room_id):
  print(f'joined room {room_id}')
  socket_manager.server.enter_room(sid, room_id)

def add_socket(app):
  socket_manager.on('connect', handler=handle_connect)
  socket_manager.on('join_detection_room', handler=handle_join)
  socket_manager.mount_to('/ws', app)
