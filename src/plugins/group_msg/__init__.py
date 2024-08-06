from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_message, on_notice
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, GroupRecallNoticeEvent
from .config import Config

import re, time, random

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
async def repeater(event: GroupMessageEvent, bot: Bot):
    group_id = str(event.group_id)
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

"""
antirecall = on_notice()

@antirecall.handle()
async def antirecall_handle(event: GroupRecallNoticeEvent, bot: Bot):
    group_id = event.group_id
    message_id = event.message_id
    username = event.user_id
    if event.user_id == 1176129206: return
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
"""



