from nonebot import on_command
from nonebot.adapters.onebot.v11.adapter import Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from utils.utils import get_IO_path
from typing import List, Tuple
import json, textwrap

plugin_ctrl_json_path = get_IO_path("plugin_ctrl", "json")

class Plugin:
    def __init__(self, names: List[str], description: str, help_info: str, default_on: bool, priority: int):
        self.name = names[0]
        self.help_info = help_info
        self.default_on = default_on
        self.base_plugin = on_command(names[0], aliases = set(names[1:]), priority = priority)
        @self.base_plugin.handle()
        async def _(bot: Bot, event: GroupMessageEvent, args = CommandArg()):
            group_id = event.group_id
            with open(plugin_ctrl_json_path, "r") as f: data = json.load(f)
            name = names[0]
            if name not in data: data[name] = []
            group_list = data[name]
            cmd_params = args.extract_plain_text()
            permission = SUPERUSER
            if cmd_params:
                if cmd_params == "on":
                    if not await permission(bot, event): await self.base_plugin.finish("你没有权限执行此操作")
                    if (group_id not in group_list and not default_on) or (group_id in group_list and default_on):
                        group_list.append(group_id) if not default_on else group_list.remove(group_id)
                        await self.base_plugin.send(f"已成功开启本群{description}")
                    else: await self.base_plugin.finish(f"本群{description}已处于开启状态，无需重复开启")
                elif cmd_params == "off":
                    if not await permission(bot, event): await self.base_plugin.finish("你没有权限执行此操作")
                    if (group_id in group_list and not default_on) or (group_id not in group_list and default_on):
                        group_list.remove(group_id) if not default_on else group_list.append(group_id)
                        await self.base_plugin.send(f"已成功关闭本群{description}")
                    else: await self.base_plugin.finish(f"本群{description}已处于关闭状态，无需重复关闭")
                elif cmd_params == "help":
                    await self.base_plugin.finish(textwrap.dedent(self.help_info).strip())
                else: return
            else: return
            data[name] = group_list
            with open(plugin_ctrl_json_path, "w") as f: json.dump(data, f)
    
    def check_plugin_ctrl(self, group_id: int) -> bool:
        with open(get_IO_path("plugin_ctrl", "json"), "r") as f: data = json.load(f)
        if self.name not in data: data[self.name] = []
        group_list = data[self.name]
        return group_id not in group_list if self.default_on else group_id in group_list
    
class Plugin_Ctrl:
    def __init__(self):
        self.plugin_list: List[Plugin] = []

    def create_plugin(self, names: List[str], description: str, help_info: str = "本插件暂无帮助", default_on: bool = True, priority: int = 1) -> Plugin:
        plugin = Plugin(names, description, help_info, default_on, priority)
        self.plugin_list.append(plugin)
        return plugin
    
    def check_plugin_status(self, group_id: int) -> Tuple[List[str], List[str]]:
        with open(plugin_ctrl_json_path, "r") as f: data = json.load(f)
        on, off = [], []
        for plugin in self.plugin_list:
            if plugin.name not in data: data[plugin.name] = []
            on.append(plugin.name) if (group_id in data[plugin.name] and not plugin.default_on) \
                or (group_id not in data[plugin.name] and plugin.default_on) else off.append(plugin.name)
        return on, off
    
    def get_help_info(self) -> str:
        help_info = ""
        for plugin in sorted(self.plugin_list, key = lambda x: x.name):
            help_info += f"———————— {plugin.name} ————————\n{textwrap.dedent(plugin.help_info).strip()}\n"
        return help_info

plugin_ctrl = Plugin_Ctrl()