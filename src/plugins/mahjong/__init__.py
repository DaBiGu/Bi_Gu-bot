from nonebot import get_plugin_config, get_bot
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot_plugin_apscheduler import scheduler

from .config import Config
from .mahjongsoul import get_user_data, get_latest_match, create_match_result_image

from utils import global_plugin_ctrl
from utils.utils import get_IO_path
import json

__plugin_meta__ = PluginMetadata(
    name="mahjong",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

_qh = global_plugin_ctrl.create_plugin(names = ["qh", "雀魂"], description = "雀魂战绩查询",
                                       help_info = "/qh [username] 查看[username]的近30局雀魂战绩",
                                       default_on = True, priority = 1)

qh = _qh.base_plugin

@qh.handle()
async def qh_handle(event: GroupMessageEvent, args = CommandArg()):
    if not _qh.check_plugin_ctrl(event.group_id): await qh.finish("该插件在本群中已关闭")
    username = args.extract_plain_text()
    if _qh.check_base_plugin_functions(username): return
    message = get_user_data(username)
    await qh.finish(message = message)

qh.append_handler(qh_handle)

qh_json_path = get_IO_path("mahjongsoul", "json")

@scheduler.scheduled_job("interval", minutes = 5)
async def qh_check_new_match():
    with open(qh_json_path, "r", encoding = "utf-8") as f:
        data = json.load(f)
    for group_id in data:
        for user_id in data[group_id]:
            latest_match = get_latest_match(int(user_id))
            if latest_match:
                if not data[group_id][user_id] or data[group_id][user_id]["gameId"] != latest_match["gameId"]:
                    data[group_id][user_id] = latest_match
                    with open(qh_json_path, "w", encoding = "utf-8") as f:
                        json.dump(data, f)
                    latest_match_message = create_match_result_image(latest_match, int(user_id))
                    await get_bot().send_group_msg(group_id = int(group_id), message = latest_match_message)