@echo off

tasklist | find "chrome.exe"

echo "chrome process를 모두 종료합니다."
pause
taskkill /IM "chrome.exe" /f