from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment, Message

from .config import Config

import datetime, os, json, random, requests

__plugin_meta__ = PluginMetadata(
    name="wife",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)


wife = on_command("wife", aliases={"群老婆"})

@wife.handle()
async def wife_handle(bot: Bot, event: GroupMessageEvent):
    group_id = event.group_id
    user_id = event.user_id
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(os.getcwd() + "/src/data/wife/record.json", "r") as f: record = json.load(f)
    if today not in record: record[today] = {}
    if group_id not in record[today]: record[today][group_id] = {}
    raw_group_members = await bot.get_group_member_list(group_id = group_id)
    single_members = []
    for member in raw_group_members:
        if member["user_id"] != user_id and member["user_id"] not in record[today][group_id]: single_members.append(member["user_id"])
    _wife = random.choice(single_members)
    record[today][group_id][user_id] = _wife
    record[today][group_id][wife] = user_id
    with open(os.getcwd() + "/src/data/wife/record.json", "w") as f: json.dump(record, f)
    with open(os.getcwd() + f"/src/data/wife/temp/{user_id}.png", "wb") as f: f.write(requests.get(f"https://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640").content)
    message = Message([MessageSegment.at(user_id), MessageSegment.text("你今天的群老婆是"), MessageSegment.at(_wife),
                       MessageSegment.image("file:///" + os.getcwd() + f"/src/data/wife/temp/{user_id}.png")])
    await wife.finish(message = message)