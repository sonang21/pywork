# test_schedule.py

import schedule
import time

def test_job(tid):
    tm = time.ctime()
    print ("%d (%s) ... Start " % (tid, tm))
    time.sleep(10)  ## delay running time 
    print ('%d (%s) ... Done... %s'   % (tid, tm, time.ctime()))
    
schedule.every(10).seconde.do(test_job, (777))
