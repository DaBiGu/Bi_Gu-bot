from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from .config import Config

import re

__plugin_meta__ = PluginMetadata(
    name="repeater",
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
        await bot.send_group_msg(group_id = event.group_id, message = raw_message, auto_escape = False)
    last_message[group_id] = message

