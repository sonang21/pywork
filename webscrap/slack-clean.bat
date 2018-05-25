@echo off
@rem get token https://api.slack.com/custom-integrations/legacy-tokens
set t1=xoxp-294011574325
set t2=293792089107-369646495942
set t3=c2d2b8259ca5ca39d5d52592ff465a8d
slack-cleaner --token=%t1%-%t2%-%t3% --rate 3 --message --channel airplane --bot --perform