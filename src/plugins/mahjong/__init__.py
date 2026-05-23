from nonebot import get_plugin_config, get_bot
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot_plugin_apscheduler import scheduler

from .config import Config
from .mahjongsoul import get_user_data, get_latest_match, create_match_result_image, search_user
from .tenhou import (
    get_user_summary as th_get_user_summary,
    get_latest_match as th_get_latest_match,
    create_match_result_image as th_create_match_result_image,
    get_dan_change as th_get_dan_change,
)

from utils import global_plugin_ctrl
from utils.utils import get_IO_path
import json, os

__plugin_meta__ = PluginMetadata(
    name="mahjong",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

_qh = global_plugin_ctrl.create_plugin(names = ["qh", "雀魂"], description = "雀魂战绩查询",
                                       help_info = """
                                                   /qh [username] 查看[username]的近30局雀魂战绩
                                                   /qh search [username] 搜索雀魂玩家[username]
                                                   /qh add|bind [user_id] 添加雀魂账号[user_id]到列表，群内自动播报最新战绩
                                                   /qh delete|unbind [user_id] 解除雀魂账号[user_id]的绑定
                                                   """,
                                       default_on = True, priority = 1)

qh = _qh.base_plugin

qh_json_path = get_IO_path("mahjongsoul", "json")

@qh.handle()
async def qh_handle(event: GroupMessageEvent, args = CommandArg()):
    if not _qh.check_plugin_ctrl(event.group_id): await qh.finish("该插件在本群中已关闭")
    cmd_params = args.extract_plain_text()
    if _qh.check_base_plugin_functions(cmd_params): return
    if " " in cmd_params:
        cmd_params_list = cmd_params.split(" ")
        if cmd_params_list[0] == "search":
            search_keyword = " ".join(cmd_params_list[1:])
            message = search_user(search_keyword)
        elif cmd_params_list[0] in ["add", "bind"]:
            user_id = " ".join(cmd_params_list[1:])
            try: user_id = int(user_id)
            except Exception: message = "用户ID不合法, 请检查输入"
            if not get_latest_match(user_id): message = f"未找到ID为{user_id}的玩家对局数据"
            else:
                with open(qh_json_path, "r", encoding = "utf-8") as f:
                    data = json.load(f)
                if str(event.group_id) not in data: data[str(event.group_id)] = {}
                if str(user_id) in data[str(event.group_id)]: message = f"ID为{user_id}的玩家已经绑定过了"
                else:
                    data[str(event.group_id)][str(user_id)] = {}
                    with open(qh_json_path, "w", encoding = "utf-8") as f: json.dump(data, f)
                    message = f"成功绑定ID为{user_id}的雀魂账号"
        elif cmd_params_list[0] in ["delete", "unbind"]:
            user_id = " ".join(cmd_params_list[1:])
            try: user_id = int(user_id)
            except Exception: message = "用户ID不合法, 请检查输入"
            else:
                with open(qh_json_path, "r", encoding = "utf-8") as f:
                    data = json.load(f)
                if str(event.group_id) not in data or str(user_id) not in data[str(event.group_id)]: message = f"ID为{user_id}的玩家尚未绑定"
                else:
                    data[str(event.group_id)].pop(str(user_id))
                    with open(qh_json_path, "w", encoding = "utf-8") as f: json.dump(data, f)
                    message = f"成功解绑ID为{user_id}的雀魂账号"
        else: return
    else: message = get_user_data(cmd_params)
    await qh.finish(message = message)

qh.append_handler(qh_handle)

@scheduler.scheduled_job("interval", minutes = 5)
async def qh_check_new_match():
    with open(qh_json_path, "r", encoding = "utf-8") as f:
        data = json.load(f)
    for group_id in data:
        for user_id in data[group_id]:
            latest_match = get_latest_match(int(user_id))
            if latest_match:
                if not data[group_id][user_id] or data[group_id][user_id]["gameId"] != latest_match["gameId"]:
                    data[group_id][user_id] = latest_match
                    with open(qh_json_path, "w", encoding = "utf-8") as f:
                        json.dump(data, f)
                    latest_match_message = create_match_result_image(latest_match, int(user_id))
                    await get_bot().send_group_msg(group_id = int(group_id), message = latest_match_message)


_th = global_plugin_ctrl.create_plugin(names = ["th", "tenhou", "天凤"], description = "天凤战绩查询",
                                       help_info = """
                                                   /th [username] 查看[username]的天凤近期对局战绩
                                                   /th add|bind [username] 添加天凤账号[username]到列表，群内自动播报最新战绩
                                                   /th delete|unbind [username] 解除天凤账号[username]的绑定
                                                   """,
                                       default_on = True, priority = 1)

th = _th.base_plugin

th_json_path = get_IO_path("tenhou", "json")

if not os.path.exists(th_json_path):
    os.makedirs(os.path.dirname(th_json_path), exist_ok=True)
    with open(th_json_path, "w", encoding = "utf-8") as f: json.dump({}, f)

@th.handle()
async def th_handle(event: GroupMessageEvent, args = CommandArg()):
    if not _th.check_plugin_ctrl(event.group_id): await th.finish("该插件在本群中已关闭")
    cmd_params = args.extract_plain_text().strip()
    if _th.check_base_plugin_functions(cmd_params): return
    if " " in cmd_params:
        cmd_params_list = cmd_params.split(" ")
        if cmd_params_list[0] in ["add", "bind"]:
            username = " ".join(cmd_params_list[1:]).strip()
            if not username: message = "用户名不能为空"
            elif not th_get_latest_match(username): message = f"未找到天凤玩家「{username}」的对局数据"
            else:
                with open(th_json_path, "r", encoding = "utf-8") as f:
                    data = json.load(f)
                if str(event.group_id) not in data: data[str(event.group_id)] = {}
                if username in data[str(event.group_id)]: message = f"天凤玩家「{username}」已经绑定过了"
                else:
                    data[str(event.group_id)][username] = {}
                    with open(th_json_path, "w", encoding = "utf-8") as f: json.dump(data, f, ensure_ascii = False)
                    message = f"成功绑定天凤账号「{username}」"
        elif cmd_params_list[0] in ["delete", "unbind"]:
            username = " ".join(cmd_params_list[1:]).strip()
            with open(th_json_path, "r", encoding = "utf-8") as f:
                data = json.load(f)
            if str(event.group_id) not in data or username not in data[str(event.group_id)]:
                message = f"天凤玩家「{username}」尚未绑定"
            else:
                data[str(event.group_id)].pop(username)
                with open(th_json_path, "w", encoding = "utf-8") as f: json.dump(data, f, ensure_ascii = False)
                message = f"成功解绑天凤账号「{username}」"
        else: return
    elif cmd_params:
        message = th_get_user_summary(cmd_params)
    else: return
    await th.finish(message = message)

th.append_handler(th_handle)

@scheduler.scheduled_job("interval", minutes = 5)
async def th_check_new_match():
    with open(th_json_path, "r", encoding = "utf-8") as f:
        data = json.load(f)
    for group_id in data:
        for username in data[group_id]:
            latest_match = th_get_latest_match(username)
            if latest_match:
                stored = data[group_id][username]
                if not stored or stored.get("_key") != latest_match["_key"]:
                    data[group_id][username] = {"_key": latest_match["_key"]}
                    with open(th_json_path, "w", encoding = "utf-8") as f:
                        json.dump(data, f, ensure_ascii = False)
                    msg = th_create_match_result_image(latest_match, username)
                    await get_bot().send_group_msg(group_id = int(group_id), message = msg)
                    change = th_get_dan_change(username)
                    if change:
                        (before_dan, before_pt), (after_dan, after_pt) = change
                        from .tenhou import DAN_LIST_4
                        before_idx = next((i for i, d in enumerate(DAN_LIST_4) if d[0] == before_dan), -1)
                        after_idx = next((i for i, d in enumerate(DAN_LIST_4) if d[0] == after_dan), -1)
                        if after_idx > before_idx >= 0:
                            text = f"恭喜{username}在刚才的对局中升段：{before_dan} {before_pt}pt → {after_dan} {after_pt}pt)"
                            await get_bot().send_group_msg(group_id = int(group_id), message = text)
                        elif 0 <= after_idx < before_idx:
                            text = f"很遗憾，{username}在刚才的对局中掉段了：{before_dan} {before_pt}pt → {after_dan} {after_pt}pt)"
                            await get_bot().send_group_msg(group_id = int(group_id), message = text)