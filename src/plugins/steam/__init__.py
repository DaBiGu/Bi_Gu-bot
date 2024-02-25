from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.params import CommandArg

from .config import Config
from .get_steam_playing import get_steam_playing

__plugin_meta__ = PluginMetadata(
    name="steam",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

steam = on_command("steam")
@steam.handle()
async def steam_handle(args = CommandArg()):
    steam_id = args.extract_plain_text()
    steam_status = get_steam_playing(steam_id)
    if steam_status[1] == None:
        message = f"{steam_status[0]} 没在玩游戏"
    else:
        message = f"{steam_status[0]} 正在玩 {steam_status[1]}"
    await steam.finish(message = message)



