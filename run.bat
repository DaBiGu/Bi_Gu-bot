if "%~1" neq "" (
    taskkill /f /pid %~1
)

conda activate bot
nb run