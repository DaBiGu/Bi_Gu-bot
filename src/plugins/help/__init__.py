from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message

from .config import Config

from .help import draw_help
from .helper_message import Helper_Messages

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