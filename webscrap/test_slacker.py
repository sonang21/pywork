#-*- coding:utf-8 -*-
import slackweb
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
        s.notify(text= msg)

send_slack("테스트로 보냅니다.^^")
