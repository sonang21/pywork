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

#driver = webdriver.Chrome('chromedriver', chrome_options=options)
driver = webdriver.Chrome('C:\\8.SW\\21.python\\chromedriver_win32\\chromedriver.exe', chrome_options=options)
#driver = webdriver.Chrome('C:\\8.SW\\21.python\\chromedriver_win32\\chromedriver.exe')
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

    driver.find_element_by_id('PNWHC00001_departure_anchor').click()
    #driver.find_element_by_xpath("//*[text() = '서울/김포 (GMP)']").click()
    for lst in driver.find_elements_by_tag_name('dd'):
        print(lst.text)
        if "김포" in lst.text:
            lst.click()
            print('-------------> click')
            
    #el = driver.find_element_by_id('PNWHC00001_arrival_anchor')
    for lst in driver.find_elements_by_tag_name('dd'):
        print(lst.text)
        if "제주" in lst.text:
            lst.click()
            print('-------------> click')

    
    el = driver.find_element_by_id('PNWHC00001_departure_date')
    driver.execute_script("arguments[0].value = '2018-02-14';", el)
    #el.clear()
    #el.send_keys("2018-02-14")

    el = driver.find_element_by_id('PNWHC00001_destination_date')
    driver.execute_script("arguments[0].value = '2018-02-18';", el)
    
    # combo check
    #print('check box options ------------------------')
    #el = driver.find_element_by_id('PNWHC00001_icheck')
    #for option in el.find_elements_by_tag_name('li'):
    #    print(option.text)
    #    if "편도" in option.text:
    #        option.click()
    #        print('----------> clik')
        

    print(driver.find_element_by_xpath("//*[text() = '항공권 조회']").is_displayed())
    el=driver.find_element_by_xpath("//*[text() = '항공권 조회']")
    driver.execute_script("arguments[0].click();", el)
    time.sleep(3)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    #file = open('out.txt', 'w', encoding='UTF-8')
    #file.write(driver.page_source)

    tables = soup.find_all('table', class_ = 'air_goods_list')
    
    print('count: %s' % len(tables))

    print('=' * 80)
    for info in soup.find_all('dl', class_ = 'wrap top'):
        slack_msg.append('info: %s' % info.get_text())

    bSendMsg = False
    for tab in tables:
        slack_msg.append("-" * 40)
        #print(tab.get_text())
        thead = tab.find('thead')
        #slack_msg.append("head: %s" % (thead.get_text()))
        # print(', '.join([row.get_text() for row in thead.find_all('th')[:4]]))
        # print('*' * 80)
        slack_msg.append("head: %s" % (', '.join([row.get_text() for row in thead.find_all('th')[:4]])))

        tbody = tab.find('tbody')
        for row in tbody.find_all('tr'):  # 첫비행기 제외[1:]
            if len(row.get_text().strip()) > 1:
                status = '매진'

                for cell in row.find_all('td')[0:3]: 
                    if (not '매진' in cell.get_text()) and (row.find_all('td')[3].get_text() >= "08:30"):
                        status = '예약가능'
                        bSendMsg = True
                        slack_msg.append(" row: %s ==> %s" % (', '.join([row.get_text() for row in row.find_all('td')[:4]]), status))
    
    
    
    #input("script end, type any key")
    print('Send Message; %s' %bSendMsg)
    if bSendMsg:
        send_slack('\n'.join(slack_msg))
    
except Exception as err:
    print("[Error]================================")
    print(str(err))
    send_slack(str(err))
    #print('---------------- debug -------------------')
    #print('\n'.join(slack_msg))
    
finally:
    print("[finally]==============================")
    #time.sleep(10)
    driver.close()
    driver.quit()
    
    #file.close()
