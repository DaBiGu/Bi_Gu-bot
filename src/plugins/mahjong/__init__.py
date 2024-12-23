from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from .config import Config
from .mahjongsoul import get_user_data

from utils import global_plugin_ctrl

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