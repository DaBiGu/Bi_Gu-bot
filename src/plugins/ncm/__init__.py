from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageSegment

from .config import Config
from .ncm import ncm_search_song

__plugin_meta__ = PluginMetadata(
    name="ncm",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

ncm = on_command("ncm")

@ncm.handle()
async def ncm_handle_func(args = CommandArg()):
    cmd_params = args.extract_plain_text()
    if " " not in cmd_params: return
    else:
        cmd_params_list = cmd_params.split(" ")
        if cmd_params_list[0] == "search":
            if len(cmd_params_list) >= 3:
                response = ncm_search_song(cmd_params_list[1], int(cmd_params_list[2]))
            else:
                response = ncm_search_song(cmd_params_list[1])
        elif cmd_params_list[0] == "id":
            response = MessageSegment.music("163", cmd_params_list[1])
    await ncm.finish(response)


