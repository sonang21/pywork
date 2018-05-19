# coding=cp949
# coding=euc-kr
# coding=utf-8 

import sched, time

print ("""
--------------------------------------------------------------------------------
sample 1
--------------------------------------------------------------------------------
""")

s = sched.scheduler(time.time, time.sleep)
id = 1

def do_something(sc, tid): 
    s.enter(3, 1, do_something, (sc, tid + 1,))   ## ���ణ���� �����ϰ� �����ϱ� ���� .. ���� ������ �ߺ����� ��? ^^
    tm = time.ctime()
    print ("%d (%s) ... Start " % (tid, tm))
    time.sleep(10)
    print ('%d (%s) ... Done... %s'   % (tid, tm, time.ctime()))
    
    # do your stuff

s.enter(3, 1, do_something, (s,id,))
s.run()


print ("""
--------------------------------------------------------------------------------
sample 2
--------------------------------------------------------------------------------
""")
while True:
  print (time.ctime())
  time.sleep(5)
  