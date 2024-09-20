from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment, Message
from utils.utils import get_output_path, get_IO_path

from .config import Config

import datetime, os, json, random, requests, time

__plugin_meta__ = PluginMetadata(
    name="wife",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

wife_json_path = get_IO_path("wife_record", "json")
last_sent_time_json_path = get_IO_path("last_sent_time", "json")

wife = on_command("wife", aliases={"群老婆"})

@wife.handle()
async def wife_handle(bot: Bot, event: GroupMessageEvent, args = CommandArg()):
    group_id = str(event.group_id)
    user_id = str(event.user_id)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    raw_group_members = await bot.get_group_member_list(group_id = event.group_id)
    with open(wife_json_path, "r") as f: record = json.load(f)
    with open(last_sent_time_json_path, "r") as f: last_sent_time = json.load(f)
    if today not in record: record[today] = {}
    if group_id not in record[today]: record[today][group_id] = {}
    record[today]["514299983"]["987099115"] = "2464190200"
    record[today]["514299983"]["2464190200"] = "987099115"
    if user_id in record[today][group_id]:
        _wife = record[today][group_id][user_id]
    else:
        single_members = []
        for member in raw_group_members:
            if group_id in last_sent_time:
                if str(member["user_id"]) != user_id and str(member["user_id"]) not in record[today][group_id]:
                    if str(member["user_id"]) in last_sent_time[group_id]:
                        if time.time() - last_sent_time[group_id][str(member["user_id"])] <= 129600:
                            single_members.append(str(member["user_id"]))
        if not single_members: message = "本群没有符合条件的群友"
        _wife = random.choice(single_members)
        record[today][group_id][user_id] = _wife
        record[today][group_id][_wife] = user_id
    with open(wife_json_path, "w") as f: json.dump(record, f)
    avatar_path = get_output_path(f"wife_{_wife}", temp = True)
    with open(avatar_path, "wb") as f: f.write(requests.get(f"https://q1.qlogo.cn/g?b=qq&nk={_wife}&s=640").content)
    target = MessageSegment.at(_wife)
    if option := args.extract_plain_text():
        if option == "-s": 
            for member in raw_group_members:
                if str(member["user_id"]) == _wife: target = MessageSegment.text(" @" + member["nickname"])
    message = Message([MessageSegment.at(user_id), MessageSegment.text(" 你今天的群老婆是 "), target,
                       MessageSegment.image("file:///" + avatar_path)])
    await wife.finish(message = message)

wife_count = on_command("rbq", aliases={"群魅魔"})
@wife_count.handle()
async def wife_count_handle(bot: Bot, event: GroupMessageEvent):
    group_id = str(event.group_id)
    user_id = str(event.user_id)
    count = 0
    with open(wife_json_path, "r") as f: record = json.load(f)
    for date in record:
        if group_id in record[date]:
            if user_id in record[date][group_id]:
                count += 1
    message = MessageSegment.at(user_id) + MessageSegment.text(f" 自2024-09-21以来已经成为{count}次群友的老婆了, 可喜可贺")
    await wife_count.finish(message = message)