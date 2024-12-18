from nonebot import on_command
from nonebot.adapters.onebot.v11.adapter import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from utils.utils import get_IO_path
from typing import List
import json

def create_plugin_ctrl(names: List[str], description: str, default_on: bool = True):
    plugin_ctrl = on_command(names[0], aliases = set(names[1:]))
    @plugin_ctrl.handle()
    async def _(bot: Bot, event: GroupMessageEvent, args = CommandArg()):
        group_id = event.group_id
        with open(get_IO_path("plugin_ctrl", "json"), "r") as f: data = json.load(f)
        name = names[0]
        if name not in data: data[name] = []
        group_list = data[name]
        cmd_params = args.extract_plain_text()
        permission = SUPERUSER
        if cmd_params:
            if cmd_params == "on":
                if not permission(bot, event): await plugin_ctrl.finish("你没有权限执行此操作")
                if (group_id not in group_list and not default_on) or (group_id in group_list and default_on):
                    group_list.append(group_id) if not default_on else group_list.remove(group_id)
                    await plugin_ctrl.send(f"已成功开启本群{description}")
                else: await plugin_ctrl.finish(f"本群{description}已经开启")
            elif cmd_params == "off":
                if not permission(bot, event): await plugin_ctrl.finish("你没有权限执行此操作")
                if (group_id in group_list and not default_on) or (group_id not in group_list and default_on):
                    group_list.remove(group_id) if not default_on else group_list.append(group_id)
                    await plugin_ctrl.send(f"已成功关闭本群{description}")
                else: await plugin_ctrl.finish(f"本群{description}已经关闭")
            else: return
        else: return
        data[name] = group_list
        with open(get_IO_path("plugin_ctrl", "json"), "w") as f: json.dump(data, f)
    return plugin_ctrl