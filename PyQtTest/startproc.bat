@echo off
if "%1"=="hide" goto CmdBegin

start mshta vbscript:createobject("wscript.shell").run("""%~0"" hide",0)(window.close)&&exit

:CmdBegin

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