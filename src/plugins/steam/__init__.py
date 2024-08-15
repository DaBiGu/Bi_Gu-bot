from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command, get_bot
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from nonebot_plugin_apscheduler import scheduler

from .config import Config
from .get_steam_playing import get_steam_playing
from .data import Steam_Data
from .search_game import draw_search_result
from .recommend_random_game import draw_game_card

import json, os

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
    cmd_params = args.extract_plain_text()
    if " " in cmd_params:
        search_keywords = cmd_params.split(" ")
        if search_keywords[0] == "search":
            game_name = " ".join(search_keywords[1:])
            message = MessageSegment.text(f"Search Result for {game_name}:")
            message += draw_search_result(game_name)
        elif search_keywords[0] == "random":
            steam_id = search_keywords[1]
            message = draw_game_card(steam_id)
    else:
        steam_id = args.extract_plain_text()
        username, game_status= get_steam_playing(steam_id)
        if username:
            if game_status: message = f"{username} 正在玩 {game_status}"
            else: message = f"{username} 没在玩游戏"
        else: message = f"找不到id为{steam_id}的用户"
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

sjqy = on_command("视奸群友")
@sjqy.handle()
async def sjqy_handle(event: GroupMessageEvent, args = CommandArg()):
    group_id = str(event.group_id)
    if cmd_params := args.extract_plain_text():
        if " " in cmd_params:
            _, steam_id = cmd_params.split(" ")
            if _ == "add":
                with open(os.getcwd() + "/src/data/steam/steam.json", "r") as f: steam_status = json.load(f)
                if group_id not in steam_status: steam_status[group_id] = []
                if steam_id not in steam_status[group_id]:
                    username, _ = get_steam_playing(steam_id)
                    if username:
                        steam_status[group_id].append(steam_id)
                        await sjqy.send(message = f"已添加{username}到本群视奸列表")
                    else: await sjqy.send(message = f"找不到id为{steam_id}的用户")
                else: await sjqy.send(message = f"{steam_id}已在本群视奸列表中")
                with open(os.getcwd() + "/src/data/steam/steam.json", "w") as f: json.dump(steam_status, f)
            elif _ == "remove":
                with open(os.getcwd() + "/src/data/steam/steam.json", "r") as f: steam_status = json.load(f)
                if group_id not in steam_status: steam_status[group_id] = []
                if steam_id in steam_status[group_id]:
                    steam_status[group_id].remove(steam_id)
                    username, _ = get_steam_playing(steam_id)
                    await sjqy.send(message = f"已从本群视奸列表移除{username}")
                else: await sjqy.send(message = f"{steam_id}不在本群视奸列表中")
                with open(os.getcwd() + "/src/data/steam/steam.json", "w") as f: json.dump(steam_status, f)
            else: return
        elif cmd_params == "list":
            with open(os.getcwd() + "/src/data/steam/steam.json", "r") as f: steam_status = json.load(f)
            if group_id in steam_status:
                message = "本群视奸列表如下:\n"
                for steam_id in steam_status[group_id]:
                    username, _ = get_steam_playing(steam_id)
                    message += f"{username} [{steam_id}]\n"      
            message += "\n使用/视奸群友 add|remove [steam_id]管理列表"
            await sjqy.finish(message = message)
        else: return
    else:
        with open(os.getcwd() + "/src/data/steam/steam.json", "r") as f: steam_status = json.load(f)
        group_id = str(group_id)
        if group_id in steam_status:
            message = ""
            for steam_id in steam_status[group_id]:
                username, current_steam_status = get_steam_playing(steam_id)
                if username:
                    if current_steam_status is not None: message += f"{username} 正在玩 {current_steam_status}\n"
                    else: message += f"{username} 没在玩游戏\n"
                else: message += f"找不到id为{steam_id}的用户\n"
            message += "EOF"
        await sjqy.finish(message = message)
