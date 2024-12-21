from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.params import CommandArg

from .config import Config
from .get_setu import get_setu
from .search_setu import search_setu

from utils import global_plugin_ctrl

__plugin_meta__ = PluginMetadata(
    name="setu",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

_setu = global_plugin_ctrl.create_plugin(names = ["setu", "涩图"], description = "来点涩图",
                                         help_info = "/setu 返回随机色图\n \
                                                      /setu search 对消息记录中的图片回复该指令进行以图搜图\n \
                                                      /setu [tags] 返回指定tags的色图; 可以传入多个tag, 以空格分隔",
                                         default_on = True, priority = 1)
                                         

setu = _setu.base_plugin

@setu.handle()
async def setu_handle(event: GroupMessageEvent, args = CommandArg()):
    if not _setu.check_plugin_ctrl(event.group_id): await setu.finish("该插件在本群中已关闭")
    if args.extract_plain_text() == "search":
        source_url = None
        for seg in event.reply.message:
            if seg.type == "image":
                source_url = seg.data.get("url")
                break
        if source_url: result = await search_setu(source_url)
        result_str = "Search result(s):\n"
        for item in result:
            result_str += f"{item}\n"
        await setu.finish(result_str)
    else:
        setu_tags = args.extract_plain_text().split(" ")
        message = await get_setu(setu_tags)
        await setu.finish(message = message)