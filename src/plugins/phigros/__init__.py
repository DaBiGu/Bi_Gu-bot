from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent

from .config import Config
from .search_song import phigros_search_song

from utils import global_plugin_ctrl

__plugin_meta__ = PluginMetadata(
    name="phigros",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

_phigros = global_plugin_ctrl.create_plugin(names = ["phigros"], description = "Phigros相关功能",
                                            help_info = "/phigros search [songname] 搜索歌名为[songname]的phigros歌曲信息(支持模糊匹配)",
                                            default_on = True, priority = 1)
phigros = _phigros.base_plugin

@phigros.handle()
async def phigros_handle_func(event: GroupMessageEvent, args = CommandArg()):
    if not _phigros.check_plugin_ctrl(event.group_id): await phigros.finish("该插件在本群中已关闭")
    cmd_params = args.extract_plain_text()
    if _phigros.check_base_plugin_functions(cmd_params): return
    if " " not in cmd_params: return
    else:
        cmd_params_list = cmd_params.split(" ")
        if cmd_params_list[0] == "search":
            search_keyword = " ".join(cmd_params_list[1:])
            message = Message([MessageSegment.text(f"Search result for \"{search_keyword}\":"), await phigros_search_song(search_keyword)])
        else: return
    await phigros.finish(message)