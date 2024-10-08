from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.permission import SUPERUSER
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot
from nonebot_plugin_apscheduler import scheduler

from .config import Config
from .draw_update_message import draw_update_message
from utils.utils import get_data_path

import subprocess, os, requests, zipfile, shutil

__plugin_meta__ = PluginMetadata(
    name="update",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

update = on_command("update", permission = SUPERUSER, priority = 2)

@update.handle()
async def update_handle():
    update_status = os.popen("git pull").read()
    if "Already up to date" in update_status:
        await update.finish(message = "Already up to date")
    else:
        await update.send(message = draw_update_message(update_status))
        subprocess.Popen([os.getcwd() + "/run.bat", str(os.getpid())])

reboot = on_command("reboot", permission = SUPERUSER)

@reboot.handle()
async def reboot_handle():
    await reboot.send(message = "Furina Rebooting...")
    subprocess.Popen([os.getcwd() + "/run.bat", str(os.getpid())])  

@scheduler.scheduled_job("cron", hour = 0, minute = 0)
async def update_chromedriver():
    request_url, download_url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json", None
    for data in requests.get(request_url).json()["channels"]["Stable"]["downloads"]["chromedriver"]:
        if data["platform"] == "win64": download_url = data["url"]
    with open(get_data_path("chromedriver.zip", temp = True), "wb") as file: file.write(requests.get(download_url).content)
    with zipfile.ZipFile(get_data_path("chromedriver.zip", temp = True), "r") as file: file.extractall(get_data_path(temp = True))
    os.remove(os.getcwd() + "/chromedriver.exe")
    shutil.move(get_data_path("chromedriver-win64/chromedriver.exe"), os.getcwd())