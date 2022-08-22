@echo off

tasklist | find /i "trayicondemo.exe" 
if "%errorlevel%"=="1" (goto f) else (goto e)

:f
echo [ %time:~,-3% ] Process "trayicondemo.exe" is not found !
start "" "D:\dist\trayicondemo.exe"
exit

:e
echo [ %time:~,-3% ] Process "trayicondemo.exe" has existed .
REM taskkill /f /im cmd.exe
REM pause