from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment, Message

from .config import Config

import datetime, os, json, random, requests, time

__plugin_meta__ = PluginMetadata(
    name="wife",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)


wife = on_command("wife", aliases={"群老婆"})

@wife.handle()
async def wife_handle(bot: Bot, event: GroupMessageEvent, args = CommandArg()):
    group_id = str(event.group_id)
    user_id = str(event.user_id)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    raw_group_members = await bot.get_group_member_list(group_id = event.group_id)
    with open(os.getcwd() + "/src/data/wife/record.json", "r") as f: record = json.load(f)
    if today not in record: record[today] = {}
    if group_id not in record[today]: record[today][group_id] = {}
    if user_id in record[today][group_id]:
        _wife = record[today][group_id][user_id]
    else:
        single_members = []
        for member in raw_group_members:
            if str(member["user_id"]) != user_id and str(member["user_id"]) not in record[today][group_id] and time.time() - member["last_sent_time"] <= 604800:
                single_members.append(str(member["user_id"]))
        _wife = random.choice(single_members)
        record[today][group_id][user_id] = _wife
        record[today][group_id][_wife] = user_id
    to_delete = [day for day in record if day != today] 
    for day in to_delete: del record[day]
    with open(os.getcwd() + "/src/data/wife/record.json", "w") as f: json.dump(record, f)
    with open(os.getcwd() + f"/src/data/wife/temp/{_wife}.png", "wb") as f: f.write(requests.get(f"https://q1.qlogo.cn/g?b=qq&nk={_wife}&s=640").content)
    target = MessageSegment.at(_wife)
    if option := args.extract_plain_text():
        if option == "-s": 
            for member in raw_group_members:
                if str(member["user_id"]) == _wife: target = MessageSegment.text(" @" + member["nickname"])
    message = Message([MessageSegment.at(user_id), MessageSegment.text(" 你今天的群老婆是 "), target,
                       MessageSegment.image("file:///" + os.getcwd() + f"/src/data/wife/temp/{_wife}.png")])
    await wife.finish(message = message)