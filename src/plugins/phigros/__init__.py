from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.params import CommandArg

from .config import Config
from .search_song import phigros_search_song

__plugin_meta__ = PluginMetadata(
    name="phigros",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

phigros = on_command("phigros")

@phigros.handle()
async def phigros_handle_func(args = CommandArg()):
    cmd_params = args.extract_plain_text()
    if " " not in cmd_params: return
    else:
        cmd_params_list = cmd_params.split(" ")
        if cmd_params_list[0] == "search":
            search_keyword = " ".join(cmd_params_list[1:])
            response = phigros_search_song(search_keyword)
        else: return
    await phigros.finish(response)