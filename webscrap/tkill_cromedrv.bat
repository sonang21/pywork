@echo off

tasklist | find "chromedriver.exe"

echo "chromedriver process를 모두 종료합니다."
pause
taskkill /IM "chromedriver.exe" /f