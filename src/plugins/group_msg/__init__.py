from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_message, on_notice, on_command, on_keyword, on_regex
from nonebot.rule import to_me
from nonebot.params import CommandArg, RegexGroup
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, GroupRecallNoticeEvent, Message, MessageSegment
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from .config import Config
from .chatcount import get_chatcount, draw_chatcount_bargraph
from utils.utils import get_IO_path, random_trigger
from typing import Dict, Any, Optional

from utils import global_plugin_ctrl

import re, time, json, datetime

__plugin_meta__ = PluginMetadata(
    name="group_msg",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

morning_json_path = get_IO_path("morning", "json")
chatcount_json_path = get_IO_path("chatcount", "json")
gamelist_json_path = get_IO_path("gamelist", "json")
last_sent_time_json_path = get_IO_path("last_sent_time", "json")

# copied from https://github.com/Utmost-Happiness-Planet/nonebot-plugin-repeater/blob/main/nonebot_plugin_repeater/__init__.py
def message_preprocess(message: str):
    has_image = False
    raw_message = message
    images = {}
    _images = re.findall(r'\[CQ:image.*?]', message)
    if _images: has_image = True
    for i in _images:
        images.update({i: [re.findall(r'url=(.*?)[,\]]', i)[0][0], re.findall(r'file=(.*?)[,\]]', i)[0][0]]})
    for i in images:
        message = message.replace(i, f'[{images[i][1]}]')
    return message, raw_message, has_image

m = on_message(priority = 10, block = False)

last_message = {}
message_times = {}
repeated_messages = []
shortest_times = 2
MIN_REPEAT_INTERVAL = 180

@m.handle()
async def group_message_handle(event: GroupMessageEvent, bot: Bot):
    group_id = str(event.group_id)
    user_id = str(event.user_id)
    global last_message, message_times
    message, raw_message, has_image = message_preprocess(str(event.message))
    if not message: return
    if list(message)[0] == "/" or has_image: return
    if last_message.get(group_id) == message:
        message_times[group_id] = (message_times[group_id] + 1) % 3
        if message_times[group_id] == 0: message_times[group_id] = 1
    else:
        message_times[group_id] = 1
    if message_times.get(group_id) == shortest_times:
        for item in repeated_messages:
            if item[1] == group_id and item[0] == message:
                if time.time() - item[2] < MIN_REPEAT_INTERVAL: return
                else: repeated_messages.remove(item)
        if random_trigger(40): await bot.send_group_msg(group_id = event.group_id, message = raw_message, auto_escape = False)
        repeated_messages.append([message, group_id, time.time()])
    last_message[group_id] = message

    with open(chatcount_json_path, "r") as f: chatcount = json.load(f)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    if group_id not in chatcount: chatcount[group_id] = {}
    if today not in chatcount[group_id]: chatcount[group_id][today] = {}
    if user_id not in chatcount[group_id][today]: chatcount[group_id][today][user_id] = 1
    else: chatcount[group_id][today][user_id] += 1
    with open(chatcount_json_path, "w") as f: json.dump(chatcount, f)

    with open(last_sent_time_json_path, "r") as f: record = json.load(f)
    if group_id not in record: record[group_id] = {}
    record[group_id][user_id] = int(time.time())
    with open(last_sent_time_json_path, "w") as f: json.dump(record, f)

_chatcount = global_plugin_ctrl.create_plugin(names = ["chatcount", "cc"], description = "聊天统计",
                                              help_info = """
                                                            /chatcount|cc today|yesterday|week|month|year
                                                                查看今日/昨日/本周/本月/年度群内b话量top10
                                                                可选参数 -o 以默认风格绘制
                                                                *数据统计开始于2024-09-06
                                                          """,
                                              default_on = True, priority = 1)
chatcount = _chatcount.base_plugin

@chatcount.handle()
async def chatcount_handle(event: GroupMessageEvent, bot: Bot, args = CommandArg()):
    if not _chatcount.check_plugin_ctrl(event.group_id): await chatcount.finish("该插件在本群中已关闭")
    cmd_params = args.extract_plain_text()
    if _chatcount.check_base_plugin_functions(cmd_params): return
    nicknames = {}
    group_members_raw = await bot.call_api("get_group_member_list", group_id = event.group_id)
    for member in group_members_raw:
        nicknames[member["user_id"]] = member["nickname"]
    if cmd_params:
        if " " in cmd_params:
            _ = cmd_params.split(" ")
            time_range = " ".join(_[:-1]) if _[-1] == "-o" else " ".join(_)
            kawaii = False if _[-1] == "-o" else True
        else: time_range, kawaii = cmd_params, True
        if time_range in ["today", "yesterday", "week", "month", "year", "last week", "last month"]: 
            message = await draw_chatcount_bargraph(get_chatcount(str(event.group_id), time_range), time_range, nicknames, kawaii)
        elif time_range == "-o":
            message = await draw_chatcount_bargraph(get_chatcount(str(event.group_id), "week"), "week", nicknames, kawaii = False)
        else: message = "不支持的时间范围\n目前支持today|yesterday|(last) week|(last) month|year"
    else: message = await draw_chatcount_bargraph(get_chatcount(str(event.group_id), "week"), "week", nicknames)
    await chatcount.finish(message = message)

antirecall = on_notice()

antirecall_ctrl = global_plugin_ctrl.create_plugin(names = ["antirecall"], description = "消息防撤回", default_on = False)

@antirecall.handle()
async def antirecall_handle(event: GroupRecallNoticeEvent, bot: Bot):
    if not antirecall_ctrl.check_plugin_ctrl(event.group_id): return
    group_id = event.group_id
    message_id = event.message_id
    username = event.user_id
    if event.user_id == int(bot.self_id): return
    operatorname = event.operator_id
    raw_message = await bot.get_msg(message_id = message_id)
    group_members_raw = await bot.call_api("get_group_member_list", group_id = event.group_id)
    for member in group_members_raw:
        if member["user_id"] == event.user_id: username = member["nickname"]
        if member["user_id"] == event.operator_id: operatorname = member["nickname"]
    message = None
    for seg in raw_message["message"]:
        if seg["type"] == "text": message = seg["data"]["text"]
    if message:
        if "撤回了" in message and "一条消息" in message or "/recall" in message: return
        if username == operatorname:
            await bot.send_group_msg(group_id = group_id, message = f"{username}撤回了一条消息:\n{message}")
        else:
            await bot.send_group_msg(group_id = group_id, message = f"{operatorname}撤回了{username}的一条消息:\n{message}")

morning = on_command("早安", aliases = {"早", "早上好"}, rule=to_me())

@morning.handle()
async def morning_handle(event: GroupMessageEvent):
    group_id = str(event.group_id)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    now = datetime.datetime.now()
    with open(morning_json_path, "r") as f: record = json.load(f)
    if today not in record: record[today] = {}
    if group_id not in record[today]: record[today][group_id] = 0
    if now < datetime.datetime.combine(now.date(), datetime.time(6, 0)):
        message_str = " 还没六点，早安你个头，赶紧给我回去睡觉"
    else:
        record[today][group_id] += 1
        group_rank = record[today][group_id]
        total_rank = sum([record[today][x] for x in record[today]])
        message_str = " 早上好呀~" if now < datetime.datetime.combine(now.date(), datetime.time(9, 0)) \
            else " 起床了, 太阳都晒屁股啦" if now < datetime.datetime.combine(now.date(), datetime.time(12, 0)) \
            else " 这么晚才起, 该调作息啦" if now < datetime.datetime.combine(now.date(), datetime.time(18, 0)) \
            else " 天都黑啦, 你确定你不是吸血鬼?"
        message_str += f"\n你是本群第{group_rank}个, 今日第{total_rank}个对芙芙说早安的哦\n芙芙祝你度过愉快的一天~"
    to_delete = [day for day in record if day != today] 
    for day in to_delete: del record[day]
    with open(morning_json_path, "w") as f: json.dump(record, f)
    message = Message([MessageSegment.at(event.user_id), MessageSegment.text(message_str)])
    await morning.finish(message = message)

xm = on_keyword(keywords=["羡慕", "xm"], priority = 10)

xm_ctrl = global_plugin_ctrl.create_plugin(names = ["xm", "羡慕"], description = "这也羡慕那也羡慕", default_on = True)

@xm.handle()
async def xm_handle(event: GroupMessageEvent):
    if not xm_ctrl.check_plugin_ctrl(event.group_id): return
    if random_trigger(25): await xm.finish("这也羡慕那也羡慕")
    else: return

# copied from https://github.com/NumberSir/nonebot-plugin-questionmark
question = on_regex(r"^([?？¿!！¡\s]+)$", priority = 9)

@question.handle()
async def question_handle(rgx = RegexGroup()):
    if not rgx: return
    response = rgx[0] \
        .replace("¿", "d").replace("?", "¿").replace("？", "¿").replace("d", "?") \
        .replace("¡", "d").replace("!", "¡").replace("！", "¡").replace("d", "!")
    if random_trigger(25): await question.finish(response)
    else: return

@Bot.on_called_api
async def count_bot_messages(bot: Bot, exception: Optional[Exception], api: str, data: Dict[str, Any], result: Any):
    if api == "send_msg" or "send_group_msg":
        if "group_id" in data:
            group_id = str(data["group_id"])
            with open(chatcount_json_path, "r") as f: chatcount = json.load(f)
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            if group_id not in chatcount: chatcount[group_id] = {}
            if today not in chatcount[group_id]: chatcount[group_id][today] = {}
            if str(bot.self_id) not in chatcount[group_id][today]: chatcount[group_id][today][str(bot.self_id)] = 1
            else: chatcount[group_id][today][str(bot.self_id)] += 1
            with open(chatcount_json_path, "w") as f: json.dump(chatcount, f)

chatcount.append_handler(chatcount_handle); morning.append_handler(morning_handle)

_gamelist = global_plugin_ctrl.create_plugin(names = ["gamelist", "gl"], description = "群游戏列表", 
                                             help_info = """
                                                            /gamelist|gl 查看本群游戏列表
                                                            /gamelist add|remove [game] 添加/删除游戏 (需要管理员权限)
                                                            /gamelist join|quit [game] 加入/退出[game]列表 
                                                          """,
                                             default_on = True, priority = 1)

gamelist = _gamelist.base_plugin
permission = SUPERUSER | GROUP_ADMIN | GROUP_OWNER

@gamelist.handle()
async def gamelist_handle(event: GroupMessageEvent, bot: Bot, args = CommandArg()):
    user_id, group_id = str(event.user_id), str(event.group_id)
    if not _gamelist.check_plugin_ctrl(event.group_id): await gamelist.finish("该插件在本群中已关闭")
    cmd_params = args.extract_plain_text()
    if _gamelist.check_base_plugin_functions(cmd_params): return
    with open(gamelist_json_path, "r") as f: data = json.load(f)
    message = None
    if cmd_params:
        if " " in cmd_params:
            _ = cmd_params.split(" ")
            action, game = _[0], " ".join(_[1:])
            if action == "add":
                if not await permission(bot, event): await gamelist.finish("你没有权限执行此操作")
                if group_id not in data: data[group_id] = {}
                if game not in data[group_id]: 
                    data[group_id][game] = []
                    message = f"成功添加{game}到本群游戏列表"
                else: message = f"{game}已在本群游戏列表中"
            elif action == "remove":
                if not await permission(bot, event): await gamelist.finish("你没有权限执行此操作")
                if game in data[group_id]:
                    del data[group_id][game]
                    message = f"成功从本群游戏列表删除{game}"
                else: message = f"{game}不在本群游戏列表中"
            elif action == "join":
                if game not in data[group_id]: message = f"本群游戏列表中找不到名为{game}的游戏"
                elif user_id in data[group_id][game]: message = Message([MessageSegment.at(event.user_id), MessageSegment.text(f" 你已在{game}游戏名单中，请勿重复加入")])
                else:
                    data[group_id][game].append(user_id)
                    message = Message([MessageSegment.at(event.user_id), MessageSegment.text(f" 成功加入{game}游戏名单")])
            elif action == "quit":
                if game not in data[group_id]: message = f"本群游戏列表中找不到名为{game}的游戏"
                elif user_id not in data[group_id][game]: message = Message([MessageSegment.at(event.user_id), MessageSegment.text(f" 你不在{game}游戏名单中，请先使用/gamelist join {game}加入")])
                else:
                    data[group_id][game].remove(user_id)
                    message = Message([MessageSegment.at(event.user_id), MessageSegment.text(f" 成功退出{game}游戏名单")])
            else: return
        else: return
    else: 
        group_members_raw = await bot.call_api("get_group_member_list", group_id = event.group_id)
        nicknames = {}
        for member in group_members_raw: nicknames[member["user_id"]] = member["nickname"]
        if group_id not in data: message = "本群暂无游戏列表"
        else:
            message = "====== 本群游戏列表 ======"
            for game in data[group_id]: 
                message += f"\n{game}: " + ", ".join([nicknames[int(user_id)] if int(user_id) in nicknames else user_id for user_id in data[group_id][game]])
    with open(gamelist_json_path, "w") as f: json.dump(data, f)
    if message: await gamelist.finish(message)

gamelist.append_handler(gamelist_handle)