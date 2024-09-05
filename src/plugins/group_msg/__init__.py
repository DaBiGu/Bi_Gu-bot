from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_message, on_notice, on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, GroupRecallNoticeEvent
from .config import Config
from .chatcount import get_chatcount

import re, time, random, json, os, datetime

__plugin_meta__ = PluginMetadata(
    name="group_msg",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)


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

@m.handle()
async def repeater_and_chatcount(event: GroupMessageEvent, bot: Bot):
    group_id = str(event.group_id)
    user_id = str(event.user_id)
    global last_message, message_times
    message, raw_message, has_image = message_preprocess(str(event.message))
    if list(message)[0] == "/" or has_image: return
    if last_message.get(group_id) == message:
        message_times[group_id] = (message_times[group_id] + 1) % 3
        if message_times[group_id] == 0: message_times[group_id] = 1
    else:
        message_times[group_id] = 1
    if message_times.get(group_id) == shortest_times:
        for item in repeated_messages:
            if item[1] == group_id and item[0] == message:
                if time.time() - item[2] < 60: return
                else: repeated_messages.remove(item)
        if random.randint(1, 100) <= 40:
            await bot.send_group_msg(group_id = event.group_id, message = raw_message, auto_escape = False)
        repeated_messages.append([message, group_id, time.time()])
    last_message[group_id] = message

    with open(os.getcwd() + "/src/data/group_msg/chatcount.json", "r") as f:
        chatcount = json.load(f)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    if group_id not in chatcount: chatcount[group_id] = {}
    if today not in chatcount[group_id]: chatcount[group_id][today] = {}
    if user_id not in chatcount[group_id][today]: chatcount[group_id][today][user_id] = 1
    else: chatcount[group_id][today][user_id] += 1
    with open(os.getcwd() + "/src/data/group_msg/chatcount.json", "w") as f:
        json.dump(chatcount, f)

chatcount = on_command("chatcount", aliases={"cc"})
@chatcount.handle()
async def chatcount_handle(event: GroupMessageEvent, args = CommandArg()):
    cmd_params = args.extract_plain_text()
    if cmd_params:
        if cmd_params == "today": message = get_chatcount(str(event.group_id), 1)
        elif cmd_params == "week": message = get_chatcount(str(event.group_id), 7)
        elif cmd_params == "month": message = get_chatcount(str(event.group_id), 30)
        else: return
    else: message = get_chatcount(str(event.group_id), 7)
    await chatcount.finish(message = message)

antirecall = on_notice()

@antirecall.handle()
async def antirecall_handle(event: GroupRecallNoticeEvent, bot: Bot):
    group_id = event.group_id
    with open(os.getcwd() + "/src/data/group_msg/antirecall.json", "r") as f:
        group_list = json.load(f)
    if group_id not in group_list: return
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
    if raw_message["message"][0]["type"] == "text": message = raw_message["message"][0]["data"]["text"]
    if message:
        if "撤回了" in message and "一条消息" in message: return
        if username == operatorname:
            await bot.send_group_msg(group_id = group_id, message = f"{username}撤回了一条消息:\n{message}")
        else:
            await bot.send_group_msg(group_id = group_id, message = f"{operatorname}撤回了{username}的一条消息:\n{message}")


antirecall_ctrl = on_command("antirecall")

@antirecall_ctrl.handle()
async def antirecall_ctrl_handle(event: GroupMessageEvent, args = CommandArg()):
    group_id = event.group_id
    with open(os.getcwd() + "/src/data/group_msg/antirecall.json", "r") as f:
        group_list = json.load(f)
    cmd_params = args.extract_plain_text()
    if cmd_params:
        if cmd_params == "on":
            print(group_id, group_list)
            if group_id not in group_list:
                group_list.append(group_id)
                await antirecall_ctrl.send("已成功开启本群消息防撤回")
        elif cmd_params == "off":
            if group_id in group_list:
                group_list.remove(group_id)
                await antirecall_ctrl.send("已成功关闭本群消息防撤回")
    with open(os.getcwd() + "/src/data/group_msg/antirecall.json", "w") as f:
        json.dump(group_list, f)




