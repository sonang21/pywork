#-*- coding:utf-8 -*-
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import slackweb
import time
import datetime
import configparser

#import importlib
#importlib.reload(sys)
#sys.setdefaultencoding('utf-8')

intervalSec = 30


options = webdriver.ChromeOptions()
options.add_argument('headless')  ## no display brower
options.add_argument("lang=ko_KR")
##options.add_argument('disable-gpu')
options.add_argument("--disable-gpu")
driver_path = 'chromedriver_win32\\chromedriver.exe'

config = configparser.ConfigParser()
config_file='config.ini'
config.read(config_file, encoding='utf-8')

slack_url = config.get('slack', 't1')
slack_url = slack_url + '/' + config.get('slack', 't2')
slack_url = slack_url + '/' + config.get('slack', 't3')

plan_dates=[]
date_count = int(config.get('plan', 'date_count'))

print ("date_count=%d" % date_count)

for i in range(1,date_count+1):
    date = config.get('plan', 'plan_date'+ str(i))
    print ("plan_date%d = %s" % (i, date))
    plan_dates = plan_dates + [ date.split(':') ]
    
print ("plan_dates= %s" % plan_dates)

plan_type = config.get('plan', 'type')
if plan_type == '왕복':
    table_ixs = [0,1]
    table_ids = ['tblDep', 'tblRet']
elif plan_type == '가는편':
    table_ixs = [0]
    table_ids = ['tblDep']
elif plan_type == '오는편':
    table_ixs = [1]
    table_idx = ['tblDep', 'tblRet']


print ("plan_type = %s, ix= %s, id = %s" % (plan_type, table_ixs, table_ids))

