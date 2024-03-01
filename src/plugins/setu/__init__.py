from typing import Annotated
from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command, on_fullmatch
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.params import CommandArg, Fullmatch

from .config import Config
from .get_setu import get_setu
from .search_setu import search_setu

__plugin_meta__ = PluginMetadata(
    name="setu",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

setu = on_command("setu", priority = 2)

@setu.handle()
async def setu_handle(args = CommandArg()):
    setu_tags = args.extract_plain_text().split(" ")
    message = get_setu(setu_tags)
    await setu.finish(message = message)

search = on_fullmatch("/setu search", priority = 1)
@search.handle()
async def search_handle(event: MessageEvent):
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