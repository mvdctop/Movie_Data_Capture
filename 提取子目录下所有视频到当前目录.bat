@echo off 
for /r %%i in (*.mp4 *.avi *.wmv *.rmvb *.flv *.rm *.mov) do (move "%%~i" "%~dp0")
