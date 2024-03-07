from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.params import CommandArg

from .config import Config
from .good_bad_news import draw_good_news, draw_bad_news

__plugin_meta__ = PluginMetadata(
    name="draw_image",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

xb = on_command("喜报", aliases={"xb"})

@xb.handle()
async def xb_handle_func(args = CommandArg()):
    text = args.extract_plain_text()
    message = draw_good_news(text)
    await xb.finish(message = message)

bb = on_command("悲报", aliases={"bb"})

@bb.handle()
async def bb_handle_func(args = CommandArg()):
    text = args.extract_plain_text()
    message = draw_bad_news(text)
    await bb.finish(message = message)

