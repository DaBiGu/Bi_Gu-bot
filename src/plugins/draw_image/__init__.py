from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command, on_fullmatch
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageEvent

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

test = on_fullmatch("/test", priority = 1)
@test.handle()
async def test_handle(event: MessageEvent):
    for seg in event.reply.message:
        await test.send(seg.type)
    '''
    source_url = None
    for seg in event.reply.message:
        if seg.type == "image":
            source_url = seg.data.get("url")
            break
    if source_url: result = search_setu(source_url)
    result_str = "Search result(s):\n"
    for item in result:
        result_str += f"{item}\n"
    await search.finish(result_str)
    '''
