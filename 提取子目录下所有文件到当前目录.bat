@echo off
for /r %%i in (*) do (move "%%~i" "%~dp0")
