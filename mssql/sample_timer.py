# coding=euc-kr

import threading 
import time

class RepeatedTimer(object):
  def __init__(self, interval, function, *args, **kwargs):
    self._timer = None
    self.interval = interval
    self.function = function
    self.args = args
    self.kwargs = kwargs
    self.is_running = False
    self.next_call = time.time()
    self.start()

  def _run(self):
    self.is_running = False
    self.start()
    self.function(*self.args, **self.kwargs)

  def start(self):
    if not self.is_running:
      self.next_call += self.interval
      self._timer = threading.Timer(self.next_call - time.time(), self._run)
      self._timer.start()
      self.is_running = True

  def stop(self):
    self._timer.cancel()
    self.is_running = False


def do_something(id):
    tid = time.ctime()
    print ("%s Started " % tid )
    time.sleep(10)       # test, if run time delayed ... 중복실행됨
    print ("%s... Done at %s " % (tid, time.ctime())) 

id = 0
rtimer = RepeatedTimer(3, do_something, (id + 1))
rtimer.start()

    