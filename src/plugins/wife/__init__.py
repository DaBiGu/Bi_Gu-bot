from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment, Message
from utils.utils import get_output_path, get_IO_path
from utils.draw_bargraph import draw_bargraph
from utils import global_plugin_ctrl

from .config import Config

import datetime, json, random, requests, time, numpy
import matplotlib.pyplot as plt
from typing import List

__plugin_meta__ = PluginMetadata(
    name="wife",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

wife_today_json_path = get_IO_path("wife_record_today", "json")
wife_all_json_path = get_IO_path("wife_record_all", "json")
wife_cp_json_path = get_IO_path("wife_record_cp", "json")
last_sent_time_json_path = get_IO_path("last_sent_time", "json")
luckiness_json_path = get_IO_path("luckiness", "json")

wife_ctrl = global_plugin_ctrl.create_plugin(names = ["wife", "群老婆"], description = "群老婆",
                                         help_info = """
                                                        /wife 今日随机群老婆
                                                            可选参数 -s 不@对方
                                                            可选参数 -f [@target] 强娶[target]为群老婆
                                                                *只有25%概率成功并且每天只能使用一次
                                                        /rbq 查看成为群老婆次数
                                                            数据统计开始于2024-09-21
                                                    """,
                                         default_on = True, priority = 2)

wife = wife_ctrl.base_plugin

WIFE_REJECT_LIST = ["1968539712"]

@wife.handle()
async def wife_handle(bot: Bot, event: GroupMessageEvent, args = CommandArg()):
    if not wife_ctrl.check_plugin_ctrl(event.group_id): await wife.finish("该插件在本群中已关闭")
    if wife_ctrl.check_base_plugin_functions(args.extract_plain_text()): return   
    group_id = str(event.group_id)
    user_id = str(event.user_id)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    raw_group_members = await bot.get_group_member_list(group_id = event.group_id)
    group_member_qqs = [str(member["user_id"]) for member in raw_group_members]
    with open(wife_today_json_path, "r") as f: record = json.load(f)
    with open(wife_all_json_path, "r") as f: _record = json.load(f)
    with open(wife_cp_json_path, "r") as f: cp_record = json.load(f)
    with open(last_sent_time_json_path, "r") as f: last_sent_time = json.load(f)
    with open(luckiness_json_path, "r") as f: luckiness_record = json.load(f)
    def update_wife_count(group_id: str, user_ids: List[str], delete: bool):
        if group_id not in _record: _record[group_id] = {}
        for user_id in user_ids:
            if user_id not in _record[group_id]: _record[group_id][user_id] = {"wife_count": 0, "force_count": 0, "forced_count": 0, "last_force_wife_date": "1970-01-01"}
            _record[group_id][user_id]["wife_count"] += -1 if delete else 1
    def update_force_wife_count(group_id: str, user_id: str, force_target: str, succeed: bool):
        if succeed: 
            _record["force_wife_count"]["success"] += 1
            _record[group_id][user_id]["force_count"] += 1
            _record[group_id][force_target]["forced_count"] += 1
        else: _record["force_wife_count"]["fail"] += 1
    def set_force_wife_date(group_id: str, user_ids: List[str]):
        if group_id not in _record: _record[group_id] = {}
        for user_id in user_ids:
            if user_id not in _record[group_id]: _record[group_id][user_id] = {"wife_count": 0, "force_count": 0, "forced_count": 0, "last_force_wife_date": "1970-01-01"}
        for user_id in user_ids: _record[group_id][user_id]["last_force_wife_date"] = today
    def get_force_wife_date(group_id: str, user_id: str):
        return _record[group_id][user_id]["last_force_wife_date"]
    def calculate_luckiness(date: str, user_id: str) -> int:
        if date not in luckiness_record: return 25
        if user_id not in luckiness_record[date]: return 25
        return luckiness_record[date][user_id]["love"] * 0.1 + 25
    if today not in record: record[today] = {}
    if group_id not in record[today]: record[today][group_id] = {}
    if user_id in record[today][group_id]:
        _wife = record[today][group_id][user_id]
    else:
        single_members = []
        for member in raw_group_members:
            if group_id in last_sent_time:
                if str(member["user_id"]) != user_id and str(member["user_id"]) not in record[today][group_id]:
                    if str(member["user_id"]) in last_sent_time[group_id]:
                        if time.time() - last_sent_time[group_id][str(member["user_id"])] <= 129600:
                            if str(member["user_id"]) not in WIFE_REJECT_LIST:
                                single_members.append(str(member["user_id"]))
        if not single_members: message = "本群没有符合条件的群友"
        _wife = random.choice(single_members)
        record[today][group_id][user_id] = _wife
        record[today][group_id][_wife] = user_id
        update_wife_count(group_id, [user_id, _wife], delete = False)
    target = MessageSegment.at(_wife)
    force_wife_message = ""
    if option := args.extract_plain_text():
        if "-f" in option:
            force_target = "-114514"
            for seg in event.message:
                if seg.type == "at": 
                    force_target = str(seg.data.get("qq"))
                    break
            if force_target in group_member_qqs:
                if get_force_wife_date(group_id, user_id) != today:
                    if force_target == user_id: force_wife_message = " 强娶失败！不能强娶自己\n"
                    else:
                        if force_target not in WIFE_REJECT_LIST: set_force_wife_date(group_id, [user_id])
                        force_wife_random = random.randint(1, 100)
                        cps = cp_record[group_id] if group_id in cp_record else [["0"]]
                        def find_cp(user_id: str):
                            for cp in cps:
                                if user_id in cp: return cp[cp.index(user_id) - 1]
                            return None
                        if find_cp(force_target):
                            force_wife_random = -1 if user_id == find_cp(force_target) else 114514
                        if force_target in WIFE_REJECT_LIST: force_wife_random = 1919810
                        if force_wife_random <= calculate_luckiness(today, user_id):
                            force_wife_message = " 强娶成功！"
                            update_force_wife_count(group_id, user_id, force_target, succeed = True)
                            if user_id in record[today][group_id]: 
                                original_wife = record[today][group_id][user_id] # get B
                                for _ in [user_id, original_wife]: del record[today][group_id][_] # delete A to B, B to A
                                update_wife_count(group_id, [user_id, original_wife], delete = True)
                            record[today][group_id][user_id] = force_target # record A to C
                            update_wife_count(group_id, [user_id], delete = False)
                            if force_target in record[today][group_id]: # check if C to D exists
                                original_wife = record[today][group_id][force_target] # get D
                                for _ in [force_target, original_wife]: del record[today][group_id][_] # delete C to D, D to C
                                update_wife_count(group_id, [force_target, original_wife], delete = True)
                            record[today][group_id][force_target] = user_id # record C to A
                            update_wife_count(group_id, [force_target], delete = False)
                            _wife = force_target
                            target = MessageSegment.at(force_target)
                        elif force_wife_random == 114514: force_wife_message = " 强娶失败！坚决抵制牛头人行为\n"
                        else: 
                            force_wife_message = " 强娶失败!"
                            if force_wife_random != 1919810: update_force_wife_count(group_id, user_id, force_target, succeed = False)
                else: force_wife_message = " 强娶失败！今天已经强娶过了\n"
            else: force_wife_message = " 强娶失败！找不到对象: 请@要强娶的群友\n"
        if "-s" in option: 
            for member in raw_group_members:
                if str(member["user_id"]) == _wife: target = MessageSegment.text(" @" + member["nickname"])
    avatar_path = get_output_path(f"wife_{_wife}", temp = True)
    with open(avatar_path, "wb") as f: f.write(requests.get(f"https://q1.qlogo.cn/g?b=qq&nk={_wife}&s=640").content)
    def reverse_str(s: str): return s[:-1][::-1] + '\n' if s.endswith('\n') else s[::-1]
    if (datetime.datetime.now().month == 4 and datetime.datetime.now().day == 1) or random.randint(1, 100) == 1:
        message = Message([MessageSegment.at(user_id), reverse_str(force_wife_message), MessageSegment.text(reverse_str(" 你今天的群老婆是 ")), target,
                           MessageSegment.image("file:///" + avatar_path)][::-1])
    else:
        message = Message([MessageSegment.at(user_id), force_wife_message, MessageSegment.text(" 你今天的群老婆是 "), target,
                           MessageSegment.image("file:///" + avatar_path)])
    to_delete = [day for day in record if day != today] 
    for day in to_delete: del record[day]
    with open(wife_today_json_path, "w") as f: json.dump(record, f)
    with open(wife_all_json_path, "w") as f: json.dump(_record, f)
    await wife.finish(message = message)

wife_count = on_command("rbq", aliases={"群魅魔"}, priority = 2)
@wife_count.handle()
async def wife_count_handle(event: GroupMessageEvent):
    if not wife_ctrl.check_plugin_ctrl(event.group_id): await wife_count.finish("该插件在本群中已关闭")
    group_id = str(event.group_id)
    user_id = str(event.user_id)
    _wife_count, force_count, forced_count = 0, 0, 0
    with open(wife_all_json_path, "r") as f: record = json.load(f)
    if group_id in record:
        if user_id in record[group_id]:
            _wife_count = record[group_id][user_id]["wife_count"]
            force_count = record[group_id][user_id]["force_count"]
            forced_count = record[group_id][user_id]["forced_count"]
    message = MessageSegment.at(user_id) + MessageSegment.text(f" 自2024-09-21以来已经成为{_wife_count}次群友的老婆了, 自2025-12-22以来强娶成功了{force_count}次, 被强娶成功了{forced_count}次, 可喜可贺")
    await wife_count.finish(message = message)

wife_count_list = on_command("rbq list", priority = 1)
@wife_count_list.handle()
async def wife_count_list_handle(bot: Bot,event: GroupMessageEvent):
    if not wife_ctrl.check_plugin_ctrl(event.group_id): await wife_count_list.finish("该插件在本群中已关闭") 
    group_id = str(event.group_id)
    nicknames = {}
    group_members_raw = await bot.call_api("get_group_member_list", group_id = event.group_id)
    for member in group_members_raw:
        nicknames[member["user_id"]] = member["nickname"]
    with open(wife_all_json_path, "r") as f: record = json.load(f)
    sorted_wife_count = dict(sorted([(user_id, user_data.get("wife_count", 0)) for user_id, user_data in record[group_id].items()], key = lambda x: x[1], reverse = True))
    if len(sorted_wife_count) > 10: sorted_wife_count = dict(list(sorted_wife_count.items())[:10])
    message = await draw_bargraph(sorted_wife_count, '你群top10群老婆排行榜', '成为群老婆次数', nicknames)
    await wife_count_list.finish(message = message)

wife_status = on_command("wife status", priority = 1)
@wife_status.handle()
async def wife_status_handle(event: GroupMessageEvent):
    if not wife_ctrl.check_plugin_ctrl(event.group_id): await wife_status.finish("该插件在本群中已关闭")
    with open(wife_all_json_path, "r") as f: record = json.load(f)
    data = record["force_wife_count"]
    labels = list(data.keys())
    values = list(data.values())
    colors = ['#00A86B', '#911F21']  # soft green & muted red
    plt.style.use('default')
    plt.style.use('dark_background')
    fig, ax = plt.subplots(facecolor='#222222')
    ax.set_facecolor('#222222')
    def make_autopct(values):
        def _(pct):
            total = sum(values)
            val = int(round(pct * total / 100.0))
            return f"{val}\n({pct:.3f}%)"
        return _
    wedges, texts, autotexts = ax.pie(values,
        labels=labels, colors=colors, startangle=90,
        autopct=make_autopct(values), pctdistance=0.5,
        textprops={'color': 'white', 'weight': 'bold'}
    )
    for text in texts: text.set_fontsize(14)
    for autotext in autotexts: autotext.set_fontsize(12)
    ax.set_title(f"force_wife_count", color='white', fontsize=16, fontweight='bold')
    output_path = get_output_path("force_wife_count")
    plt.savefig(output_path, dpi = 300, bbox_inches = "tight")
    await wife_status.finish(MessageSegment.image("file:///" + output_path))

wife_bind = on_command("wife bind", aliases={"wife -b"}, priority = 1)
@wife_bind.handle()
async def wife_bind_handle(bot: Bot, event: GroupMessageEvent, args = CommandArg()):
    if not wife_ctrl.check_plugin_ctrl(event.group_id): await wife_bind.finish("该插件在本群中已关闭")
    permission = SUPERUSER
    if not await permission(bot, event):
        await wife_bind.finish("你没有权限执行此操作")
    with open(wife_cp_json_path, "r") as f: record = json.load(f)
    raw_group_members = await bot.get_group_member_list(group_id = event.group_id)
    group_id = str(event.group_id)
    def check_legal_member(user_id: str):
        for member in raw_group_members:
            if str(member["user_id"]) == user_id: return member["nickname"]
        return None
    bind_status = -1
    if cmd_params := args.extract_plain_text():
        if " " in cmd_params: 
            targets = cmd_params.split(" ")
            if len(targets) == 2:
                if check_legal_member(targets[0]) and check_legal_member(targets[1]):
                    if targets[0] == targets[1]: bind_status = 0
                    else:
                        if group_id not in record: record[group_id] = []
                        if targets in record[group_id]: bind_status = 1
                        else:
                            cps = [item for _ in record[group_id] for item in _]
                            if targets[0] in cps or targets[1] in cps: bind_status = 2
                            else:
                                record[group_id].append(targets)
                                bind_status = 3
    message = f"群cp绑定成功:\n{check_legal_member(targets[0])}({targets[0]}) x {check_legal_member(targets[1])}({targets[1]})" if bind_status == 3 \
    else f"群cp绑定失败: 要绑定的群友已经心有所属了" if bind_status == 2 \
    else f"{check_legal_member(targets[0])}({targets[0]}) x {check_legal_member(targets[1])}({targets[1]}) 已经绑定过了" if bind_status == 1 \
    else f"群cp绑定失败: 不能绑定自己" if bind_status == 0 \
    else "群cp绑定失败, 请检查输入\n 正确的输入格式为/wife bind|-b [qq1] [qq2]"
    with open(wife_cp_json_path, "w") as f: json.dump(record, f)
    await wife_bind.finish(message = message)

wife.append_handler(wife_handle); wife_count.append_handler(wife_count_handle);