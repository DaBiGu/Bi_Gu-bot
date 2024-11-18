from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from utils.utils import get_asset_path
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="meme",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

yuyu = on_command("玉玉", aliases= {"yuyu"})
@yuyu.handle()
async def yuyu_handle_func():
    await yuyu.finish(Message([MessageSegment.image("file:///" + get_asset_path("images/yuyu.gif"))]))

fufu = on_command("芙芙", aliases= {"fufu"})
@fufu.handle()
async def fufu_handle_func():
    await fufu.finish(Message([MessageSegment.image("file:///" + get_asset_path("images/fufu.gif"))]))

die = on_command("kill")
@die.handle()
async def die_handle_func():
    await die.finish(Message([MessageSegment.image("file:///" + get_asset_path("images/die.png"))]))

pupu = on_command("噗噗", aliases= {"pupu"})
@pupu.handle()
async def pupu_handle_func():
    await pupu.finish(Message([MessageSegment.image("file:///" + get_asset_path("images/pupu.png"))]))

biebie = on_command("憋憋", aliases= {"biebie"})
@biebie.handle()
async def biebie_handle_func():
    await biebie.finish(Message([MessageSegment.image("file:///" + get_asset_path("images/biebie.png"))]))