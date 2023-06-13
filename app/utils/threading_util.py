import threading
import time

def set_interval(func, sec, stop_condition = False):
  def func_wrapper():
      set_interval(func, sec) 
      func()  
  t = threading.Timer(sec, func_wrapper)
  t.start()
  if stop_condition:
    t.cancel()
  return t


def set_block_interval(func, sec):
  signal = func()
  time.sleep(sec)
  
  if (signal):
    return set_block_interval(func, sec)
  return False