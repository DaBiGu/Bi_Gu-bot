param(
    [string]$pid = ""
)

if ($pid -ne "") {
    Stop-Process -Id $pid -Force
}

conda run -n bot python bot.py