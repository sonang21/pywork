@echo off

tasklist | find "chromedriver.exe"

echo "chromedriver process�� ��� �����մϴ�."
pause
taskkill /IM "chromedriver.exe" /f