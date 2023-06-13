import socketio
from typing import List
from config import base_config


class SocketManager:
  def __init__(self, origins: List[str]):
    mgr = socketio.AsyncRedisManager(
      base_config.CELERY_BROKER_URL
    )
    self.server = socketio.AsyncServer(
      cors_allowed_origins=origins,
      client_manager=mgr,
      async_mode="asgi",
      logger=False,
      engineio_logger=False,
    )
    self.asgi = socketio.ASGIApp(socketio_server=self.server)

  @property
  def on(self):
    return self.server.on

  @property
  def emit(self):
    return self.server.emit

  @property
  def send(self):
    return self.server.send

  def mount_to(self, path: str, app: socketio.ASGIApp):
    app.mount(path, self.asgi)
