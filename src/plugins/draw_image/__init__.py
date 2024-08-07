from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command, on_fullmatch
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageEvent

from .config import Config
from .good_bad_news import draw_good_news, draw_bad_news
from .symmetric import symmetric_left, symmetric_right, symmetric_up, symmetric_down

import requests, os

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

symmetric = on_command("对称", aliases={"symmetric"})
@symmetric.handle()
async def symmetric_handle(event: MessageEvent, args = CommandArg()):
    cmd_params = args.extract_plain_text() 
    source_url = None
    for seg in event.reply.message:
        if seg.type == "image":
            source_url = seg.data.get("url")
            break
    if source_url:
        original_img_path = os.getcwd() + "/src/data/draw_image/original_img.png"
        with open(original_img_path, "wb") as f:
            f.write(requests.get(source_url).content)
        if cmd_params == "left" or cmd_params == "左":
            message = symmetric_left(original_img_path)
        elif cmd_params == "right" or cmd_params == "右":
            message = symmetric_right(original_img_path)
        elif cmd_params == "up" or cmd_params == "上":
            message = symmetric_up(original_img_path)
        elif cmd_params == "down" or cmd_params == "下":
            message = symmetric_down(original_img_path)
        else: return
        await symmetric.finish(message = message)

