from nonebot import get_plugin_config, get_adapter
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11.adapter import Adapter
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.adapters.onebot.v11.event import MessageEvent

from .config import Config
from .mstbt import mstbt_record
from ..setu import get_setu
from nonebot import on_command, on_fullmatch
from nonebot.params import CommandArg

import time, random, os

__plugin_meta__ = PluginMetadata(
    name="mstbt",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

def second_to_hms(seconds):
    h, r = divmod(seconds, 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}小时{int(m)}分钟{int(s)}秒"

def draw_progress_bar(progress: float) -> str:
    filled_length = int(20 * progress)
    bar = "=" * filled_length + "-" * (20 - filled_length)
    return "[" + bar + "]"

amiya = on_command("amiya", aliases= {"阿米娅"})

@amiya.handle()
async def amiya_handle_func(event: MessageEvent):
    user_id = event.get_user_id()
    if user_id == "2097749210":
        if random.randint(1, 2) == 1:
            await amiya.finish("阿米娅早安晚安上班下班啥比驴")
        else:
            await amiya.finish("唉, 天天就知道阿米娅")
    else:
        await amiya.finish("阿米娅早安晚安上班下班啥比驴")

skd = on_command("懂哥")

@skd.handle()
async def skd_handle_func(args = CommandArg()):
    if args.extract_plain_text() == "工口":
        await skd.finish(Message([MessageSegment.image("file:///" + os.getcwd() + "/src/data/mstbt/gongkou.png")]))
    elif args.extract_plain_text() == "手冲":
        await skd.finish(Message([MessageSegment.image("file:///" + os.getcwd() + "/src/data/mstbt/shouchong.png")]))
    else:
        await skd.finish("我好想做上科大的狗啊")

gk_time = None

_gk = on_command("工口")
@_gk.handle()
async def gk_handle_func():
    global gk_time
    gk_time = time.time()
    await _gk.finish(Message([MessageSegment.image("file:///" + os.getcwd() + "/src/data/mstbt/gongkou.png")]))

_sc = on_command("手冲", aliases= {"mstbt"})
@_sc.handle()
async def sc_handle_func(event: MessageEvent, args = CommandArg()):
    username = event.get_user_id()
    if "message.group" in str(event.get_event_name()):
        onebot_adapter = get_adapter(Adapter)
        bot = list(onebot_adapter.bots.values())[0]
        group_members_raw = await bot.call_api("get_group_member_list", group_id = event.group_id)
        for member in group_members_raw:
            if str(member["user_id"]) == event.get_user_id():
                username = member["nickname"]
                break
    if args.extract_plain_text() == "counter":
        with open("./src/data/mstbt/mstbt_counter.txt", "r") as f:
            mstbt_counter = float(f.read())
        mstbt_progress = "{:.4f}".format(mstbt_counter / 50)
        mstbt_progress_percent = "{:.2f}".format(float(mstbt_progress) * 100)
        mstbt_progress_bar = draw_progress_bar(float(mstbt_progress))
        await _sc.finish(f"{mstbt_progress_bar} {mstbt_progress_percent}%\n这个进度条充满会有什么神奇的事情发生呢...")
    mstbt_response = mstbt_record(event.get_user_id())
    if mstbt_response[0] is not None:
        current_time = time.time()
        time_diff_str = second_to_hms(current_time - float(mstbt_response[0]))
        message_str = f"{username}上次手冲时间{time_diff_str}前\n你本周已经手冲了{mstbt_response[2]}次\n你总共已经手冲了{mstbt_response[1]}次"
    else:
        message_str = f"{event.get_user_id()}成功记录第1次手冲"
    random.seed(time.time())
    global gk_time
    if random.randint(1, 100) == 1 or (gk_time is not None and time.time() - gk_time <= 300):
        await _sc.send(Message([MessageSegment.image("file:///" + os.getcwd() + "/src/data/mstbt/shouchong.gif")]))
        await _sc.send("你触发了至臻手冲!")
        await _sc.send(Message(["你获得了手冲奖励：一张随机色图"]) + get_setu())
    else:
        await _sc.send(Message([MessageSegment.image("file:///" + os.getcwd() + "/src/data/mstbt/shouchong.png")]))
        _mstbt = random.uniform(1, 20)
        with open("./src/data/mstbt/mstbt_counter.txt", "r") as f:
            mstbt_counter = float(f.read())
        mstbt_counter += _mstbt
        if _mstbt == 1:
            await _sc.send("你获得了手冲奖励...吗?")
            await _sc.send(Message([MessageSegment.image("file:///" + os.getcwd() + "/src/data/mstbt/eat_icecream.png")]))
        elif mstbt_counter >= 50:
            await _sc.send(Message(["你获得了手冲奖励：一张随机色图"]) + get_setu())
            mstbt_counter = 0
        with open("./src/data/mstbt/mstbt_counter.txt", "w") as f:
            f.write(str(mstbt_counter))
    await _sc.finish(message_str)
    

yuyu = on_command("玉玉", aliases= {"yuyu"})

@yuyu.handle()
async def yuyu_handle_func():
    await yuyu.finish(Message([MessageSegment.image("file:///" + os.getcwd() + "/src/data/mstbt/yuyu.gif")]))

fufu = on_command("芙芙", aliases= {"fufu"})

@fufu.handle()
async def fufu_handle_func():
    await fufu.finish(Message([MessageSegment.image("file:///" + os.getcwd() + "/src/data/mstbt/fufu.gif")]))

sb = on_fullmatch("阿姨洗铁路")

@sb.handle()
async def sb_handle_func():
    await sb.finish("傻逼")

