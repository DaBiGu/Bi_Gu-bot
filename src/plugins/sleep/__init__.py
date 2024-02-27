from nonebot import get_plugin_config
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Event

from .config import Config
from .sleep_record import record_sleep, record_awake, get_average_sleep_duration
import time

__plugin_meta__ = PluginMetadata(
    name="sleep",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

sleep = on_command("sleep", aliases = {"gn"})
awake = on_command("awake")

def second_to_hms(seconds):
            h, r = divmod(seconds, 3600)
            m, s = divmod(r, 60)
            return f"{int(h)}小时{int(m)}分钟{int(s)}秒"

@sleep.handle()
async def sleep_handle(event: Event, args = CommandArg()):
    if cmd_params := args.extract_plain_text():
        if cmd_params == "status":
            avg = get_average_sleep_duration(event.get_user_id())
            avg_str = second_to_hms(avg)
            await awake.finish(message = event.get_user_id() + "本周平均睡觉时长" + avg_str)
    else:
        user_id = event.get_user_id()
        current_time = record_sleep(user_id)
        if current_time is not None:
            await sleep.finish(message = user_id + f"现在时间是{current_time}，已经记录你的睡觉时间了哦！" + "\n晚安好梦")
        else:
            await sleep.finish(message = user_id + "已经睡着了\n再次记录睡觉时间请先用/awake起床")

@awake.handle()
async def awake_handle(event: Event):
    user_id = event.get_user_id()
    [awake_time, average_sleep_duration] = record_awake(user_id)
    if awake_time == -1:
        await awake.finish(message = user_id + "清醒得很\n再次记录起床时间请先用/sleep睡觉")
    elif awake_time == -2:
        await awake.finish(message = user_id + "找不到你的睡觉记录\n请先用/sleep睡觉")
    else:
        sleep_duration = time.time() - float(awake_time)
        
        sleep_duration_str = second_to_hms(sleep_duration)
        average_sleep_duration_str = second_to_hms(average_sleep_duration)

        await awake.send(message = user_id + "睡觉时长" + sleep_duration_str + "\n早安新的一天开始了哦！")
        await awake.finish(message = user_id + "本周平均睡觉时长" + average_sleep_duration_str)






