from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.params import CommandArg

from .config import Config
from .mahjongsoul import get_user_data
from .mahjongclub import get_mahjongclub_info

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

qh = on_command("qh", aliases={"雀魂"})

@qh.handle()
async def qh_handle(args = CommandArg()):
    username = args.extract_plain_text()
    message = get_user_data(username)
    await qh.finish(message = message)

### Deprecated
#
#qz = on_command("qz", aliases={"雀庄"})
#
#@qz.handle()
#async def qz_handle(args = CommandArg()):
#    username = args.extract_plain_text()
#    message = get_mahjongclub_info(username)
#    await qz.finish(message = message)