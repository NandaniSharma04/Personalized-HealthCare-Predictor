@echo off

cd /d "%~dp0"

start cmd /k "python server.py"

timeout /t 5

start http://localhost:8000/login.html