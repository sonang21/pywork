#-*- coding:utf-8 -*-
from selenium import webdriver
from bs4 import BeautifulSoup
import slackweb
import pandas as Pd
import time
import datetime

#from tkinter import messagebox
#import tkinter

# hide main window
#root = tkinter.Tk()
#root.withdraw()

########################################
def send_slack(msg):
    now = datetime.datetime.now()
    s = slackweb.Slack(url="https://hooks.slack.com/services/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")
    s.notify(text = msg)

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('disable-gpu')
options.add_argument("lang=ko_KR")
#options.add_argument("--disable-gpu")

#driver = webdriver.Chrome('C:\\8.SW\\21.python\\chromedriver_win32\\chromedriver.exe', chrome_options=options)
driver = webdriver.Chrome('C:\\8.SW\\21.python\\chromedriver_win32\\chromedriver.exe')

#driver.implicity_wait(3)
driver.get('https://www.eastarjet.com/newstar/PGWHC00001')

# messagebox.showinfo("확인","창하나 닫기전")

slack_msg = []

try:
    # close all pop-up windows
    #driver.minimize_window()
    hasCloseButton = True
    while hasCloseButton:
        hasCloseButton = False
        print("*" * 80)
        els = driver.find_elements_by_xpath('//*[@id]')
        
        for el in els:
            if "close" in el.get_attribute('id') :
                print("id: %s, display: %s, text:%s" % (el.get_attribute('id'), el.is_displayed(), el.text)) 
                if el.is_displayed():
                    hasCloseButton = True
                    el.click()
                    print("----------> click")                
                    break
                #for a in el.get_property('attributes'):
                #    print(a.keys, a.values)
                #pass
            pass
        pass
    
    el = driver.find_element_by_xpath("//a[@class='addPlus']")
    for x in range(3):
        driver.execute_script("arguments[0].click();", el)
    
    driver.execute_script("document.getElementsByClassName('id_person1')[0].value='4';")
        
    time.sleep(5)
    
except Exception as err:
    print("[Error]================================")
    print(str(err))
    #send_slack(str(err))
    #print('---------------- debug -------------------')
    #print('\n'.join(slack_msg))
    
finally:
    print("[finally]==============================")
    #time.sleep(10)
    driver.close()
    driver.quit()
    
    #file.close()
