#-*- coding:utf-8 -*-
from selenium import webdriver
from bs4 import BeautifulSoup
import slackweb
import pandas as Pd
import time
import datetime
import sys

#from tkinter import messagebox
#import tkinter

# hide main window
#root = tkinter.Tk()
#root.withdraw()

sDepartDate = '2018-02-13'
sReturnDate = '2018-02-17'

slack_msg = []
########################################
def msg_add(msg, bSlackMsg = True):
    print(msg)
    if bSlackMsg:
        slack_msg.append(msg)

def send_slack(msg):
    now = datetime.datetime.now()
    s = slackweb.Slack(url="https://hooks.slack.com/services/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")
    s.notify(text = msg)

def file_save(file_name, file_content, file_option='w'):
    file = open(file_name, file_option, encoding='UTF-8')
    file.write(file_content)
    file.close()

def scrap_jeju():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('disable-gpu')
    options.add_argument("lang=ko_KR")
    #options.add_argument("--disable-gpu")
    driver_path = 'chromedriver_win32\\chromedriver.exe'
    
    driver = webdriver.Chrome(driver_path, chrome_options=options)
    #driver = webdriver.Chrome(driver_path)
    
    #driver.implicity_wait(3)
    
    sURL = 'https://www.jejuair.net/jejuair/kr/com/jeju/ibe/availInit.do'
    
    del slack_msg[:]
    msg_add(sURL)
    msg_add("Depart:%s, Return: %s" % (sDepartDate, sReturnDate))
    ###################################
    driver.get(sURL)
    
    # messagebox.showinfo("확인","창하나 닫기전")    
    
    try:
        
        el = driver.find_element_by_id('btnDepStn1')
        driver.execute_script("arguments[0].click();", el)
        time.sleep(1)
        driver.find_element_by_xpath('//button[@airname="서울(김포)"]').click()

        el = driver.find_element_by_id('btnArrStn1')
        driver.execute_script("arguments[0].click();", el)
        time.sleep(1)
        driver.find_element_by_xpath('//button[@airname="제주"]').click()

        el = driver.find_element_by_id('txtDate1')
        driver.execute_script("arguments[0].value = '%s';" % sDepartDate, el)
        el = driver.find_element_by_id('txtDate2')
        driver.execute_script("arguments[0].value = '%s';" % sReturnDate, el)

        el = driver.find_element_by_id('btnSelADT')
        driver.execute_script("arguments[0].click();", el)

        el = driver.find_element_by_xpath('//button[@title="성인 4명"]')
        driver.execute_script("arguments[0].click();", el)

        driver.find_element_by_id('btnSearchAirline').click();
        
        time.sleep(3)
        file_save('dump.html', driver.page_source)
        
        file_save('jjout.txt', driver.page_source)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        msg_add("=" * 50)
        
        bBookable = False
        for idTab in ['tblDep', 'tblRet']:
            tables = soup.find('table', id = idTab)

            #print(tables.get_text())
            thead = tables.find('thead')

            msg_add('%s' % ', '.join([cell.get_text() for cell in thead.find_all('th')]))

            tbody = tables.find('tbody')
            for row in tbody.find_all('tr'):
                for cell in row.find_all('td')[3:]:
                    if not ('마감' in cell.get_text()):
                        bBookable = True
                        msg_add('%s, %s' % ( ', '.join([cell.get_text() for cell in row.find_all('td')[:3]])    \
                                            ,', '.join([cell.get_text() for cell in row.find_all('label')])) \
                               )
                        break
            
            msg_add("-" * 50)

        print('Send Message; %s' % bBookable)
        if bBookable:
            send_slack('\n'.join(slack_msg))
            
    except Exception as err:
        print("[Error at line %s ]********************" % sys.exc_info()[-1].tb_lineno)
        print(str(err))
        #send_slack(str(err))
        #print('---------------- debug -------------------')
        #print('\n'.join(slack_msg))
        
    finally:
        print("[Finally]********************")
        #time.sleep(10)
        driver.close()
        driver.quit()


scrap_jeju()

print("[%s] script end" % sys.argv[0])
