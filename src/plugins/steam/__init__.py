from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command, get_bot
from nonebot.params import CommandArg
from nonebot_plugin_apscheduler import scheduler

from .config import Config
from .get_steam_playing import get_steam_playing
from .data import Steam_Data

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
    if steam_status[0] is None:
        message = f"找不到id为{steam_id}的用户"
    elif steam_status[1] is None:
        message = f"{steam_status[0]} 没在玩游戏"
    else:
        message = f"{steam_status[0]} 正在玩 {steam_status[1]}"
    await steam.finish(message = message)

steam_data = Steam_Data()

@scheduler.scheduled_job("interval", minutes = 1)
async def report_steam_status():
    to_sends = []
    global steam_data
    steam_status = steam_data.get_data()
    bot = get_bot("1176129206")
    for group_id, steam_ids in steam_status.items():
        for steam_id, game_status in steam_ids.items():
            username, current_steam_status = get_steam_playing(steam_id)
            if game_status != current_steam_status and current_steam_status is not None:
                steam_status[group_id][steam_id] = current_steam_status
                to_send = (group_id, username, current_steam_status)
                if to_send not in to_sends: to_sends.append(to_send)
    steam_data.set_data(steam_status)
    for group_id, username, current_steam_status in to_sends:
        await bot.send_group_msg(group_id = group_id, message = f"{username} 正在玩 {current_steam_status}")


