from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.params import CommandArg

from .config import Config
from .mahjongsoul import get_user_data

__plugin_meta__ = PluginMetadata(
    name="mahjong",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

qh = on_command("qh", aliases={"雀魂"})

@qh.handle()
async def qh_handle(args = CommandArg()):
    username = args.extract_plain_text()
    message = get_user_data(username)
    await qh.finish(message = message)

