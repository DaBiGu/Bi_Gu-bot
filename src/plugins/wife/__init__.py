from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment, Message
from utils.utils import get_output_path, get_IO_path

from .config import Config

import datetime, json, random, requests, time

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
    target = MessageSegment.at(_wife)
    force_wife_message = ""
    if option := args.extract_plain_text():
        if "-f" in option:
            for seg in event.message:
                if seg.type == "at": 
                    force_target = str(seg.data.get("qq"))
                    break
            force_wife_random = random.randint(1, 100)
            await bot.send_group_msg(group_id = group_id, message = str(force_wife_random))
            if force_wife_random <= 25:
                if force_target: 
                    force_wife_message = " 强娶成功!"
                    record[today][group_id][user_id] = force_target
                    if force_target in record[today][group_id]: 
                        original_wife = record[today][group_id][force_target]
                        for _ in [force_target, original_wife]: del record[today][group_id][_]
                    record[today][group_id][force_target] = user_id
                    _wife = force_target
                    target = MessageSegment.at(force_target)
                else: force_wife_message = " 找不到要强娶的对象, 请检查输入格式\n"
            else: force_wife_message = " 强娶失败!"
        if "-s" in option: 
            for member in raw_group_members:
                if str(member["user_id"]) == _wife: target = MessageSegment.text(" @" + member["nickname"])
    avatar_path = get_output_path(f"wife_{_wife}", temp = True)
    with open(avatar_path, "wb") as f: f.write(requests.get(f"https://q1.qlogo.cn/g?b=qq&nk={_wife}&s=640").content)
    message = Message([MessageSegment.at(user_id), force_wife_message, MessageSegment.text(" 你今天的群老婆是 "), target,
                       MessageSegment.image("file:///" + avatar_path)])
    with open(wife_json_path, "w") as f: json.dump(record, f)
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