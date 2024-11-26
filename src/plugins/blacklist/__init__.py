from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata

from .config import Config

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor
from nonebot.adapters.onebot.v11 import MessageEvent, Bot, GroupMessageEvent
from utils.utils import get_IO_path

import json

__plugin_meta__ = PluginMetadata(
    name="blacklist",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

blacklist_json_path = get_IO_path("blacklist", "json")

@event_preprocessor
async def check_blacklist(event: MessageEvent):
    with open(blacklist_json_path, "r") as f: blacklist = json.load(f)
    if event.get_user_id() in blacklist:
        print(f"Blacklisted user {event.get_user_id()} tried to send message")
        raise IgnoredException("Blacklisted user")
    
blacklist_ctrl = on_command("blacklist")

@blacklist_ctrl.handle()
async def blacklist_ctrl_handle(bot: Bot, event: GroupMessageEvent, args = CommandArg()):
    permission = SUPERUSER
    if not await permission(bot, event):
        await blacklist_ctrl.finish("你没有权限执行此操作")
    with open(blacklist_json_path, "r") as f: blacklist = json.load(f)
    if cmd_params := args.extract_plain_text():
        if " " in cmd_params:
            param_list = cmd_params.split(" ")
            if param_list[0] == "add":
                if param_list[1] not in blacklist:
                    blacklist.append(param_list[1])
                    message = f"Added {param_list[1]} to blacklist"
                else: message = f"{param_list[1]} already exists"
            else: return
        else: return
    else:
        message = f"Blacklisted users:\n{str(blacklist)}"
    with open(blacklist_json_path, "w") as f: json.dump(blacklist, f)
    await blacklist_ctrl.finish(message = message)