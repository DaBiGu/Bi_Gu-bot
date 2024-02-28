from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.params import CommandArg

from .config import Config
import random

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
