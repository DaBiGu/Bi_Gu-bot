from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command, get_bot
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment, Bot
from nonebot_plugin_apscheduler import scheduler

from .config import Config
from .get_steam_playing import get_steam_playing
from .data import Steam_Data
from .search_game import draw_search_result
from .recommend_random_game import draw_game_card, check_legal_game
from utils.utils import get_IO_path

import json, os, random

__plugin_meta__ = PluginMetadata(
    name="steam",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)
random_json_path = get_IO_path("steam_random", "json")
watchlist_json_path = get_IO_path("steam_watchlist", "json")

steam = on_command("steam")
@steam.handle()
async def steam_handle(event: GroupMessageEvent, bot: Bot, args = CommandArg()):
    group_id = str(event.group_id)
    user_id = str(event.user_id)
    group_info = await bot.get_group_info(group_id = event.group_id)
    group_member_list = await bot.get_group_member_list(group_id = event.group_id)
    group_name = group_info["group_name"]
    for member in group_member_list:
        if member["user_id"] == event.user_id:
            user_id = member["nickname"]
            break
    with open(random_json_path, "r") as f: recommend_list = json.load(f)
    cmd_params = args.extract_plain_text()
    if " " in cmd_params:
        search_keywords = cmd_params.split(" ")
        if search_keywords[0] == "search":
            game_name = " ".join(search_keywords[1:])
            message = MessageSegment.text(f"Search Result for {game_name}:")
            message += await draw_search_result(game_name)
        elif search_keywords[0] == "recommend":
            if len(search_keywords) == 2:
                steam_id = search_keywords[1]
                message = await draw_game_card(steamid = int(steam_id), recommended = True)
            elif len(search_keywords) == 3:
                steam_id, appid = search_keywords[1:]
                message = await draw_game_card(steamid = int(steam_id), appid = int(appid), recommended = True)
        elif search_keywords[0] == "random":
            if search_keywords[1] == "add":
                if group_name not in recommend_list: recommend_list[group_name] = {}
                if user_id not in recommend_list[group_name]: recommend_list[group_name][user_id] = []
                has_recommended = False
                for user_recommend in recommend_list[group_name].keys():
                    if search_keywords[2] in recommend_list[group_name][user_recommend]:
                        message = f"游戏{check_legal_game(int(search_keywords[2]))}已被本群的{user_recommend}推荐过了哦"
                        has_recommended = True
                        break
                if not has_recommended:
                    game_name = check_legal_game(int(search_keywords[2]))
                    if game_name:
                        recommend_list[group_name][user_id].append(search_keywords[2])
                        message = f"已添加游戏{game_name}到本群推荐列表"
                    else: message = f"找不到appid为{search_keywords[2]}的游戏"
                else: message = f"游戏{search_keywords[2]}已在本群推荐列表中"
            elif search_keywords[1] == "-a" or search_keywords[1] == "-all":
                random_game_list = []
                for group in recommend_list.keys():
                    for user_recommend in recommend_list[group].keys():
                        for appid in recommend_list[group][user_recommend]:
                            random_game_list.append([group, user_recommend, appid])
                random_game_info = random.choice(random_game_list)
                group_name, nickname, appid = random_game_info
                message = MessageSegment.at(event.user_id)
                message += " 芙芙今天推荐你玩这个游戏:"
                message += draw_game_card(appid = appid, recommended = False)
                message += f"推荐来自\"{group_name}\"的\"{nickname}\""
            else: return
    else:
        if cmd_params == "random":
            if group_name not in recommend_list: message = "本群群友还没有推荐过游戏哦"
            else:
                random_game_list = []
                for user_recommend in recommend_list[group_name].keys():
                    for appid in recommend_list[group_name][user_recommend]:
                        random_game_list.append([user_recommend, appid])
                random_game_info = random.choice(random_game_list)
                nickname, appid = random_game_info
                message = MessageSegment.at(event.user_id)
                message += " 芙芙今天推荐你玩这个游戏:"
                message += draw_game_card(appid = appid, recommended = False)
                message += f"推荐来自本群的\"{nickname}\""
        else:
            steam_id = args.extract_plain_text()
            username, game_status= get_steam_playing(steam_id)
            if username:
                if game_status: message = f"{username} 正在玩 {game_status}"
                else: message = f"{username} 没在玩游戏"
            else: message = f"找不到id为{steam_id}的用户"
    with open(random_json_path, "w") as f: json.dump(recommend_list, f)
    await steam.finish(message = message)

steam_data = Steam_Data()

"""
@scheduler.scheduled_job("interval", minutes = 1)
async def report_steam_status():
    to_sends = []
    global steam_data
    steam_status = steam_data.get_data()
    bot = get_bot()
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
"""

sjqy = on_command("视奸群友")
@sjqy.handle()
async def sjqy_handle(event: GroupMessageEvent, args = CommandArg()):
    group_id = str(event.group_id)
    if cmd_params := args.extract_plain_text():
        if " " in cmd_params:
            _, steam_id = cmd_params.split(" ")
            if _ == "add":
                with open(watchlist_json_path, "r") as f: steam_status = json.load(f)
                if group_id not in steam_status: steam_status[group_id] = []
                if steam_id not in steam_status[group_id]:
                    username, _ = get_steam_playing(steam_id)
                    if username:
                        steam_status[group_id].append(steam_id)
                        await sjqy.send(message = f"已添加{username}到本群视奸列表")
                    else: await sjqy.send(message = f"找不到id为{steam_id}的用户")
                else: await sjqy.send(message = f"{steam_id}已在本群视奸列表中")
                with open(watchlist_json_path, "w") as f: json.dump(steam_status, f)
            elif _ == "remove":
                with open(watchlist_json_path, "r") as f: steam_status = json.load(f)
                if group_id not in steam_status: steam_status[group_id] = []
                if steam_id in steam_status[group_id]:
                    steam_status[group_id].remove(steam_id)
                    username, _ = get_steam_playing(steam_id)
                    await sjqy.send(message = f"已从本群视奸列表移除{username}")
                else: await sjqy.send(message = f"{steam_id}不在本群视奸列表中")
                with open(watchlist_json_path, "w") as f: json.dump(steam_status, f)
            else: return
        elif cmd_params == "list":
            with open(watchlist_json_path, "r") as f: steam_status = json.load(f)
            message = "本群视奸列表如下:\n"
            if group_id in steam_status:
                for steam_id in steam_status[group_id]:
                    username, _ = get_steam_playing(steam_id)
                    message += f"{username} [{steam_id}]\n"
            else: message += "[empty]"
            message += "\n使用/视奸群友 add|remove [steam_id]管理列表"
            await sjqy.finish(message = message)
        else: return
    else:
        with open(watchlist_json_path, "r") as f: steam_status = json.load(f)
        group_id = str(group_id)
        if group_id in steam_status:
            message = "视奸群友中...\n"
            for steam_id in steam_status[group_id]:
                username, current_steam_status = get_steam_playing(steam_id)
                if username:
                    if current_steam_status is not None: message += f"\n{username} 正在玩 {current_steam_status}"
                    else: message += f"\n{username} 没在玩游戏"
                else: message += f"\n找不到id为{steam_id}的用户"
        else:
            message = "本群视奸列表为空\n使用/视奸群友 add [steam_id]添加群友到列表"
        await sjqy.finish(message = message)