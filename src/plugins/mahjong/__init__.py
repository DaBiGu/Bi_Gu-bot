from nonebot import get_plugin_config, get_bot
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot_plugin_apscheduler import scheduler

from .config import Config
from .mahjongsoul import get_user_data, get_latest_match, create_match_result_image, search_user

from utils import global_plugin_ctrl
from utils.utils import get_IO_path
import json

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
                    with open(qh_json_path, "w", encoding = "utf-8") as f:
                        json.dump(data, f)
                    message = f"成功绑定ID为{user_id}的雀魂账号"
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