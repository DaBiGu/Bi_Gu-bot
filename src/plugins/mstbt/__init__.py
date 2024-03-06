from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.adapters import Event

from .config import Config
from .mstbt import mstbt_record
from ..setu import get_setu
from nonebot import on_command
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

amiya = on_command("amiya", aliases= {"阿米娅"})

@amiya.handle()
async def amiya_handle_func():
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
mstbt_counter = 0

_gk = on_command("工口")
@_gk.handle()
async def gk_handle_func():
    global gk_time
    gk_time = time.time()
    await _gk.finish(Message([MessageSegment.image("file:///" + os.getcwd() + "/src/data/mstbt/gongkou.png")]))

_sc = on_command("手冲", aliases= {"mstbt"})
@_sc.handle()
async def sc_handle_func(event: Event):
    mstbt_response = mstbt_record(event.get_user_id())
    if mstbt_response[0] is not None:
        current_time = time.time()
        time_diff_str = second_to_hms(current_time - float(mstbt_response[0]))
        message_str = f"{event.get_user_id()}上次手冲时间{time_diff_str}前\n你本周已经手冲了{mstbt_response[2]}次\n你总共已经手冲了{mstbt_response[1]}次"
    else:
        message_str = f"{event.get_user_id()}成功记录第1次手冲"
    random.seed(time.time())
    global gk_time, mstbt_counter
    if random.randint(1, 100) == 1 or (gk_time is not None and time.time() - gk_time <= 300):
        await _sc.send(Message([MessageSegment.image("file:///" + os.getcwd() + "/src/data/mstbt/shouchong.gif")]))
        await _sc.send("你触发了至臻手冲!")
        await _sc.send(Message(["你获得了手冲奖励：一张随机色图"]) + get_setu())
    else:
        await _sc.send(Message([MessageSegment.image("file:///" + os.getcwd() + "/src/data/mstbt/shouchong.png")]))
        _mstbt = random.randint(1, 20)
        mstbt_counter += _mstbt
        if _mstbt == 1:
            await _sc.send("你获得了手冲奖励...吗?")
            await _sc.send(Message([MessageSegment.image("file:///" + os.getcwd() + "/src/data/mstbt/eat_icecream.png")]))
        elif mstbt_counter >= 50:
            await _sc.send(Message(["你获得了手冲奖励：一张随机色图"]) + get_setu())
            mstbt_counter = 0
    await _sc.finish(message_str)
    

yuyu = on_command("玉玉", aliases= {"yuyu"})

@yuyu.handle()
async def yuyu_handle_func():
    await yuyu.finish(Message([MessageSegment.image("file:///" + os.getcwd() + "/src/data/mstbt/yuyu.gif")]))