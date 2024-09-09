from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.permission import SUPERUSER
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot

from .config import Config
from .draw_update_message import draw_update_message

import subprocess, os

__plugin_meta__ = PluginMetadata(
    name="update",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

update = on_command("update", permission = SUPERUSER, priority = 2)

@update.handle()
async def update_handle(bot: Bot):
    update_status = os.popen("git pull").read()
    if "Already up to date" in update_status:
        await update.finish(message = "Already up to date")
    else:
        await update.send(message = draw_update_message(update_status))
        subprocess.Popen([os.getcwd() + "/run.bat", str(os.getpid())])
    