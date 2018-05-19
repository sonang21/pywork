#-*- coding:utf-8 -*-
from selenium import webdriver
from bs4 import BeautifulSoup
import slackweb
import time
import datetime
import sys

plan_dates = [["2018-09-22", "2018-09-25"], ["2018-09-22", "2018-09-26"]]
loopWaitSec = 20

options = webdriver.ChromeOptions()
## options.add_argument('headless')  ## no display brower
options.add_argument('disable-gpu')
options.add_argument("lang=ko_KR")
#options.add_argument("--disable-gpu")
driver_path = 'chromedriver_win32\\chromedriver.exe'
####################################################################################################
def file_save(file_name, file_content, file_option='w'):
    file = open(file_name, file_option, encoding='UTF-8')
    file.write(file_content)
    file.close()
    
def send_slack(msg):
    now = datetime.datetime.now()
    s = slackweb.Slack(url="https://hooks.slack.com/services/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")
    s.notify(text = msg)
def debug_sleep(msg, waitSec):
    print("## DEBUG WAITING [%s] FOR %d sec... " % (msg, waitSec));
    time.sleep(waitSec)
####################################################################################################
def scrap_eastar(aDates):
    sDepartDate = aDates[0]
    sReturnDate = aDates[1]
    slack_msg = []
    
    sURL = 'https://www.eastarjet.com/newstar/PGWHC00001'
    
    slack_msg.append("EASTAR JET: %s" % sURL)
    slack_msg.append("Depart: %s, Return: %s" % (sDepartDate, sReturnDate))
    
    try:
        driver = webdriver.Chrome(driver_path, chrome_options=options)
        driver.get(sURL)

        ## close popup windows
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
        for lst in driver.find_elements_by_tag_name('dd'):
            print(lst.text)
            if "김포" in lst.text:
                lst.click()
                print('-------------> click')
                
        for lst in driver.find_elements_by_tag_name('dd'):
            print(lst.text)
            if "제주" in lst.text:
                lst.click()
                print('-------------> click')
    
        
        debug_sleep("-1", 5)
        el = driver.find_element_by_id('PNWHC00001_departure_date')
        driver.execute_script("arguments[0].value = '%s';" % sDepartDate, el)

        debug_sleep("0", 5)
        el = driver.find_element_by_id('PNWHC00001_destination_date')
        driver.execute_script("arguments[0].value = '%s';" % sReturnDate, el)
        
        el = driver.find_element_by_xpath("//a[@class='addPlus']")
        for x in range(3):
            driver.execute_script("arguments[0].click();", el)
        
        # combo check
        #print('check box options ------------------------')
        #el = driver.find_element_by_id('PNWHC00001_icheck')
        #for option in el.find_elements_by_tag_name('li'):
        #    print(option.text)
        #    if "편도" in option.text:
        #        option.click()
        #        print('----------> clik')

           
        debug_sleep("A", 10)

        el=driver.find_element_by_xpath("//*[text() = '일정으로 조회']")
        driver.execute_script("arguments[0].click();", el)
        time.sleep(3)
        debug_sleep("B", 10)

        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    
        #file_save('eastar.txt', driver.page_source)
        
        tables = soup.find_all('table', class_ = 'air_goods_list')
        infos = soup.find_all('dl', class_ = 'wrap top')

        print('=' * 80)
    
        bSendMsg = False
        #for tab in tables: 
        for ix in range(len(tables)):
            if ix == 0 :    # 0:가는편, 1:오는편 
                continue
            slack_msg.append("-" * 40)
            slack_msg.append('info: %s' % infos[ix].get_text())
            tab = tables[ix]
            thead = tab.find('thead')
            slack_msg.append("H: %s" % (', '.join([row.get_text() for row in thead.find_all('th')[:4]])))

            tbody = tab.find('tbody')
            for row in tbody.find_all('tr'):  # 첫비행기 제외[1:]
                if len(row.get_text().strip()) > 1:
                    status = '매진'
    
                    for cell in row.find_all('td')[0:3]: 
                        if (not '매진' in cell.get_text()) and (row.find_all('td')[3].get_text() >= "07:00"):
                            status = '예약가능'
                            bSendMsg = True
                            slack_msg.append("R: %s ==> %s" % (', '.join([row.get_text() for row in row.find_all('td')[:4]]), status))
                            break
        
        #input("script end, type any key")
        print('\n'.join(slack_msg))
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

def scrap_jeju(aDates):
    sDepartDate = aDates[0]
    sReturnDate = aDates[1]
    
    sURL = 'https://www.jejuair.net/jejuair/kr/com/jeju/ibe/availInit.do'
    
    try:
        slack_msg= []
        slack_msg.append("JEJU AIR : %s" % sURL)
        slack_msg.append("Depart:%s, Return: %s" % (sDepartDate, sReturnDate))
        ###################################
        driver = webdriver.Chrome(driver_path, chrome_options=options)
        driver.get(sURL)
        
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
        
        #file_save('jjout.txt', driver.page_source)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        slack_msg.append("=" * 50)
        
        bBookable = False
        for idTab in ['tblDep(x)', 'tblRet']:
            tables = soup.find('table', id = idTab)

            if tables is None:
                continue

            #print(tables.get_text())
            thead = tables.find('thead')
            slack_msg.append(('[%s]'+ '-'* 40) % (idTab))
            slack_msg.append('%s' % ', '.join([cell.get_text() for cell in thead.find_all('th')]))

            tbody = tables.find('tbody')
            
            for row in tbody.find_all('tr'):
                for cell in row.find_all('td')[3:]:
                    if not ('마감' in cell.get_text()) and (row.find_all('td')[1].get_text() >= '07:00'):
                        bBookable = True
                        slack_msg.append('%s, %s' % ( ', '.join([cell.get_text() for cell in row.find_all('td')[:3]])    \
                                            ,', '.join([cell.get_text() for cell in row.find_all('label')])) \
                               )
                        break
            
            #slack_msg.append("-" * 50)
            
        print('\n'.join(slack_msg))
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


## function_list = [scrap_eastar, scrap_jeju]
function_list = [scrap_eastar]

while True:
    for scrap in function_list:
        for dt in plan_dates:
            scrap(dt)
            time.sleep(waitTime)
            
    
    
    #break
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    time.sleep(loopWaitSec)
    
print("[%s] script end" % sys.argv[0])
