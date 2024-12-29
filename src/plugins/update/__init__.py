from nonebot import get_plugin_config, get_bot
from nonebot.plugin import PluginMetadata
from nonebot.permission import SUPERUSER
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot_plugin_apscheduler import scheduler

from .config import Config
from .draw_update_message import draw_update_message
from ..help.about import on_disconnect
from utils.utils import get_data_path, get_asset_path

import subprocess, os, requests, zipfile, shutil

__plugin_meta__ = PluginMetadata(
    name="update",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)
permission = SUPERUSER

update = on_command("update", priority = 2)

@update.handle()
async def update_handle(bot: Bot, event: GroupMessageEvent):
    if not await permission(bot, event):
        await update.finish(message = "你没有权限执行此操作")
    update_status = os.popen("git pull").read()
    if "Already up to date" in update_status:
        await update.finish(message = "Already up to date")
    else:
        await update.send(message = draw_update_message(update_status))
        subprocess.Popen([os.getcwd() + "/run.bat", str(os.getpid())])

_reboot = on_command("reboot")

@scheduler.scheduled_job("cron", hour = 4, minute = 0)
async def reboot():
    await on_disconnect(get_bot())
    subprocess.Popen([os.getcwd() + "/run.bat", str(os.getpid())])

@_reboot.handle()
async def reboot_handle(bot: Bot, event: GroupMessageEvent):
    if not await permission(bot, event):
        await update.finish(message = "你没有权限执行此操作")
    await _reboot.send(message = "芙芙重启中...")
    await reboot()

_update_chromedriver = on_command("update chromedriver", priority = 1, permission = permission)
@scheduler.scheduled_job("cron", hour = 0, minute = 0)
@_update_chromedriver.handle()
async def update_chromedriver():
    request_url, download_url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json", None
    for data in requests.get(request_url).json()["channels"]["Stable"]["downloads"]["chromedriver"]:
        if data["platform"] == "win64": download_url = data["url"]
    with open(get_data_path("chromedriver.zip", temp = True), "wb") as file: file.write(requests.get(download_url).content)
    with zipfile.ZipFile(get_data_path("chromedriver.zip", temp = True), "r") as file: file.extractall(get_data_path(temp = True))
    output_path = get_asset_path("chrome")
    if os.path.exists(f"{output_path}/chromedriver.exe"): os.remove(f"{output_path}/chromedriver.exe")
    shutil.move(get_data_path("chromedriver-win64/chromedriver.exe", temp = True), output_path)