@echo off

tasklist | find "chrome.exe"

echo "chrome process�� ��� �����մϴ�."
pause
taskkill /IM "chrome.exe" /f