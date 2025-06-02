if "%~1" neq "" (
    taskkill /f /pid %~1
)

call conda activate bot
python bot.py