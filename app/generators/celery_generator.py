import functools
import asyncio

def sync_task(f):
  @functools.wraps(f)
  def wrapper(*args, **kwargs):
    return asyncio.get_event_loop().run_until_complete(f(*args, **kwargs))
  return wrapper