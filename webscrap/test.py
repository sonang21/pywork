#-*- coding:utf-8 -*-
from selenium import webdriver
import datetime
import slackweb
from bs4 import BeautifulSoup
# import dbcon
import pymysql
import re
import signal
import time
​
options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument("disable-gpu")
# 혹은 options.add_argument("--disable-gpu")
driver = webdriver.Chrome('chromedriver', chrome_options=options)
​
now = datetime.datetime.now()
#define time out
_TMOUT = 10
​
def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))
​
def timeout(signum,frame):
    raise TimeoutError()
​
# 이전 중복되는 기사를 체크하기 위해 마지막에 저장된 시간을 가져옴
# def check_wdt(urlnm, cursor):
#     selectSql= "SELECT TITLE, date_format(WDT,\'%Y-%m-%d %T') as WDT FROM tb_stock_dumy where URLNM='"+urlnm+"' order by wdt desc LIMIT 1"
#     cursor.execute(selectSql)
#     result=cursor.fetchall()
#     if(type(result) is tuple):
#         result=[{'TITLE': '','WDT': '1900-01-01' }]
#     return result
​# 
# def send_slack(num):
#         now = datetime.datetime.now()
#         s = slackweb.Slack(url="https://hooks.slack.com/services/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")
#         s.notify(text= now.strftime('%Y-%m-%d %H:%M:%S') + " - "+ str(num) +"건 입력 - Moneta",channel="#hp_server",user_name="sunghun")
​
def moneta_crawling():
​
    db = dbcon.conn()
    cursor = db.cursor(pymysql.cursors.DictCursor)
    driver.get('http://news.moneta.co.kr/Service/stock/ShellList.asp?ModuleID=2167&LinkID=371&NavDate='+now.strftime('%Y%m%d')+'&NavPage=1')
    soup = BeautifulSoup(driver.page_source, "lxml")
    url_name = 'moneta'
    contentarea = soup.findAll('table', {'class': 'tbl_type type2'})
​
    if len(contentarea) > 0:
​
        articleSubjectlist = contentarea[0].findAll('td' > '', {'class': 'tit'})
        articleSummaryList = contentarea[0].findAll('td' > '', {'class': 'cen sm'})
​
        checkWdt = check_wdt(url_name, cursor)  # 이전 중복되는 기사를 체크하기 위해 마지막에 저장된 시간을 가져옴
​
        seq = 0 # 등록일자, 등록시간, 기사 출처가 "cen sm"로 동일함 3개씩 구분주기 위해 별도 변수 선언
        parsResult = []
        for i in range(len(articleSubjectlist)):
            urlList = articleSubjectlist[i].find('a')['href']  # 원문 기사 URL
            titleList = articleSubjectlist[i].find('a').text  # 원문 기사 title
​
            wDate = str(articleSummaryList[seq].text.replace("/","-")) + " " + str(articleSummaryList[seq+1].text) # 등록 일시
            sourceName = articleSummaryList[seq+2].text  # 기사 출처
            seq=seq+3
​
            driver.get(urlList)
            inSoup = BeautifulSoup(driver.page_source, "lxml")
            inArticleCont = inSoup.findAll('span' > '', {'id': 'span_article_content'})
​
            if ((titleList != str(checkWdt[0]['TITLE']) and wDate > str(checkWdt[0]['WDT']))):
                for cont in inArticleCont:
                    ArticleCont = cont.get_text(" ", strip=True)
                    c1 = re.compile('.*' , re.M | re.DOTALL | re.IGNORECASE)
                    Conts = re.findall(c1, ArticleCont)
                    Cont ="'"+Conts[0]+''  # "[" 로 시작하면 리스트형식으로 인식하여 ' 를 추가하여 문자열로 만듦
                parsResult.append((url_name, urlList, titleList, Cont, sourceName, wDate))  # 파싱된 데이터를 리스트형태로 저장
                # moneta 수신 시간 체크
                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
​
        print(parsResult)
        sql = "insert into tb_stock_dumy(URLNM, NEWSURL, TITLE, CONTENTS, PRESS, WDT ) VALUES( %s, %s, %s, %s, %s, %s)"
        rows = cursor.executemany(sql, parsResult)
​
        db.commit()
​
        global _ROWS
        _ROWS = rows
        cursor.close()
    else:
        dbcon.close(db)
​
    dbcon.close(db)
    return
    driver.quit()
​
try:
     #moneta
     moneta_crawling()
     #message to slack
     send_slack(_ROWS)
except TimeoutError as ex:
     print("Time out  %d sec.. Exit" % _TMOUT)
finally:
     pass
     #signal.alarm(0)
getMoneta.py 4KB Python snippet 
Public file shared from 
