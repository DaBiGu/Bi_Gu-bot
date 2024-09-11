from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment

from .config import Config
import random, json, os, datetime
import numpy as np

__plugin_meta__ = PluginMetadata(
    name="dice",
    description="",
    usage="",
    config=Config,
)

def roll_dice(dice_num: int, dice_face: int, dice_add: int = 0) -> str:
    result = []
    for _ in range(dice_num):
        result.append(random.randint(1, dice_face) + dice_add)
    return str(result)

config = get_plugin_config(Config)

rd = on_command("rd", aliases={"roll"})

@rd.handle()
async def rd_handle_func(args=CommandArg()):
    if _args := args.extract_plain_text():
        if "d" not in _args:
            await rd.finish("格式错误")
        else:
            dice_num, dice_face = _args.split("d")
            if "+" in dice_face:
                dice_face, dice_add = map(int, dice_face.split("+"))
                await rd.finish(roll_dice(int(dice_num), dice_face, dice_add))
            else:
                await rd.finish(roll_dice(int(dice_num), int(dice_face)))

def get_luckiness() -> int:
    weights = np.array([1]*10 + [8]*10)
    weights = weights / weights.sum()
    rolls = np.random.choice(range(1, 21), size = (1, 5), p = weights)
    return int(rolls.sum())

ys = on_command("ys", aliases={"今日运势"})

@ys.handle()
async def ys_handle_func(event: MessageEvent):
    user_id = str(event.user_id)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(os.getcwd() + "/src/data/dice/luckiness.json", "r") as f:
        record = json.load(f)
    if today not in record: record[today] = {}
    if user_id not in record[today]: 
        fortune = get_luckiness()
        love = get_luckiness()
        career = get_luckiness()
        record[today][user_id] = {"fortune": fortune, "love": love, "career": career}
        message_str = " 芙芙祈祷中...\n"
    else:
        fortune = record[today][user_id]["fortune"]
        love = record[today][user_id]["love"]
        career = record[today][user_id]["career"]
        message_str = " 你今天已经测过运势了哦\n"
    message = Message([MessageSegment.at(user_id), MessageSegment.text(message_str + f"今日运势为:\n财运: {fortune}\n桃花运: {love}\n事业运: {career}")])
    to_delete = [day for day in record if day != today] 
    for day in to_delete: del record[day]
    with open(os.getcwd() + "/src/data/dice/luckiness.json", "w") as f:
        json.dump(record, f)
    await ys.finish(message)