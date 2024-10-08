from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot_plugin_apscheduler import scheduler

from .config import Config

import os, shutil

__plugin_meta__ = PluginMetadata(
    name="delete",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

def get_dir_path(path: str) -> str:
    return os.getcwd() + path

@scheduler.scheduled_job("cron", hour = 0, minute = 5)
async def delete_unnecessary_files():
    dir_list = ["/src/data/output", "/src/data/temp"]
    for _dir in dir_list:
        folderpath = get_dir_path(_dir)
        for filename in os.listdir(folderpath):
            filepath = os.path.join(folderpath, filename)
            os.remove(filepath) if os.path.isfile(filepath) else shutil.rmtree(filepath)
