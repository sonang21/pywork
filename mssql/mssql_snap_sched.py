# coding=utf-8 
# coding=euc-kr
# coding=cp949

import sched, time
import subprocess

print ("""
--------------------------------------------------------------------------------
sample 1
--------------------------------------------------------------------------------
""")

s = sched.scheduler(time.time, time.sleep)
## 60초 * 20 : 20분
vIntervalSec = 60 * 20
id = 1

def do_something(sc, tid): 
    s.enter(vIntervalSec, 1, do_something, (sc, tid + 1,))   ## 실행간격을 일정하게 유지하기 위함 .. 실행 지연시 중복실행 안? ^^
    tm = time.ctime()
    print ("%d (%s) ... Start " % (tid, tm))
    
    subprocess.call(".\mssql_snap.py", shell=True)
    # time.sleep(10)
    print ('%d (%s) ... Done... %s'   % (tid, tm, time.ctime()))
    
    # do your stuff

s.enter(0, 1, do_something, (s,id,))
s.run()