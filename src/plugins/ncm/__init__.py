from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageSegment, GroupMessageEvent

from .config import Config
from .ncm import draw_search_card, get_ncm_song_card, draw_lyrics_card

from utils import global_plugin_ctrl

__plugin_meta__ = PluginMetadata(
    name="ncm",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

_ncm = global_plugin_ctrl.create_plugin(names = ["ncm"], description = "网易云音乐相关功能",
                                        help_info = "/ncm search [keyword] [num] 网易云搜索前num首关键词为keyword的歌曲\n \
                                                     /ncm id [song_id] 获取[song_id]对应的歌曲卡片\n \
                                                     /ncm lyrics [song_id] 获取id为[song_id]歌曲的歌词卡片",
                                       default_on = True, priority = 1)

ncm = _ncm = _ncm.base_plugin

@ncm.handle()
async def ncm_handle_func(event: GroupMessageEvent, args = CommandArg()):
    if not _ncm.check_plugin_ctrl(event.group_id): await ncm.finish("该插件在本群中已关闭")
    cmd_params = args.extract_plain_text()
    if " " not in cmd_params: return
    else:
        cmd_params_list = cmd_params.split(" ")
        if cmd_params_list[0] == "search":
            search_keyword = " ".join(cmd_params_list[1:])
            response = await draw_search_card(search_keyword)
        elif cmd_params_list[0] == "id":
            #response = MessageSegment.music(type_ = "163", id_ = cmd_params_list[1])
            response = get_ncm_song_card(int(cmd_params_list[1]))
        elif cmd_params_list[0] == "lyrics":
            response = await draw_lyrics_card(int(cmd_params_list[1]))
    await ncm.finish(response)