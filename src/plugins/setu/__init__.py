from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.params import CommandArg

from .config import Config
from .get_setu import get_setu

__plugin_meta__ = PluginMetadata(
    name="setu",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

setu = on_command("setu")

@setu.handle()
async def setu_handle(args = CommandArg()):
    setu_tags = args.extract_plain_text().split(" ")
    message = get_setu(setu_tags)
    await setu.finish(message = message)