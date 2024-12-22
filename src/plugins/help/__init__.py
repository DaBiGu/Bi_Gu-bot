from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from .config import Config

from .help import draw_help
from .helper_message import Helper_Messages

from utils import global_plugin_ctrl

__plugin_meta__ = PluginMetadata(
    name="help",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

helper_messages = Helper_Messages().get_helper_messages()
update_logs = Helper_Messages().get_update_logs()

_help = on_command("help", aliases = {"帮助"})

@_help.handle()
async def help_handle():
    for i in range(len(helper_messages)):
        await _help.send(draw_help(helper_messages[i], i+1, len(helper_messages)))

_update_log = on_command("update log", priority = 1)

@_update_log.handle()
async def update_log_handle():
    for i in range(len(update_logs)):
        await _update_log.send(draw_help(update_logs[i], i+1, len(update_logs)))

_plugin_status = on_command("plugin status")
@_plugin_status.handle()
async def plugin_status_handle(event: GroupMessageEvent):
    on, off = global_plugin_ctrl.check_plugin_status(event.group_id)
    await _plugin_status.finish("本群插件状态\n\n开启的插件: " + " | ".join(sorted(on)) + "\n关闭的插件: " + " | ".join(sorted(off)))

_plugin_help = on_command("plugin help")
@_plugin_help.handle()
async def plugin_help_handle():
    await _plugin_help.finish(global_plugin_ctrl.get_help_info())