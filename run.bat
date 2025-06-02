@echo off
if "%~1" neq "" (
    taskkill /f /pid %~1
)

conda run -n bot python bot.py