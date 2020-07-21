net stop jssvcl
taskkill /f /im csmgr.exe
taskkill /f /im jsmgr.exe
taskkill /f /im jsmgr.exe
taskkill /f /im jsmgr.exe
taskkill /f /im jsenv.exe
taskkill /f /im jstray.exe
taskkill /f /im jssvc.exe
taskkill /f /im jswatcher.exe

taskkill /f /im w3wp.exe
taskkill /f /im w3wp.exe
taskkill /f /im w3wp.exe

iisreset /STOP 

"C:\Windows\Microsoft.NET\Framework\v4.0.30319\InstallUtil.exe" /u %1
pause

"C:\Windows\Microsoft.NET\Framework\v4.0.30319\InstallUtil.exe" %2
iisreset /START 
pause


