from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from utils.utils import get_asset_path
from .config import Config

import requests

from utils.utils import get_output_path

__plugin_meta__ = PluginMetadata(
    name="meme",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

yuyu = on_command("玉玉", aliases= {"yuyu", "jade jade"})
@yuyu.handle()
async def yuyu_handle():
    await yuyu.finish(Message([MessageSegment.image("file:///" + get_asset_path("images/yuyu.gif"))]))

fufu = on_command("芙芙", aliases= {"fufu", "furina"})
@fufu.handle()
async def fufu_handle():
    await fufu.finish(Message([MessageSegment.image("file:///" + get_asset_path("images/fufu.gif"))]))

die = on_command("kill")
@die.handle()
async def die_handle():
    await die.finish(Message([MessageSegment.image("file:///" + get_asset_path("images/die.png"))]))

pupu = on_command("噗噗", aliases= {"pupu"})
@pupu.handle()
async def pupu_handle():
    await pupu.finish(Message([MessageSegment.image("file:///" + get_asset_path("images/pupu.png"))]))

biebie = on_command("憋憋", aliases= {"biebie"})
@biebie.handle()
async def biebie_handle():
    await biebie.finish(Message([MessageSegment.image("file:///" + get_asset_path("images/biebie.png"))]))

httpcat = on_command("httpcat")
@httpcat.handle()
async def httpcat_handle(args = CommandArg()):
    code = args.extract_plain_text()
    output_path = get_output_path("httpcat", temp = True)
    response = requests.get(f"https://httpcats.com/{code}.jpg")
    if response.status_code == 200:
        with open(output_path, "wb") as f: f.write(response.content)
        await httpcat.finish(Message([MessageSegment.image("file:///" + output_path)]))
    else: await httpcat.finish("未找到对应状态码的图片")

yuyu.append_handler(yuyu_handle); fufu.append_handler(fufu_handle); die.append_handler(die_handle)
pupu.append_handler(pupu_handle); biebie.append_handler(biebie_handle); httpcat.append_handler(httpcat_handle)