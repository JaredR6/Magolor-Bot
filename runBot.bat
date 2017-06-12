@echo off
:start
python magolor.py
echo Bot restarting in 10 seconds...
timeout /t 10 /nobreak > NUL
goto start