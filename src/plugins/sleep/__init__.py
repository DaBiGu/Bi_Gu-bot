from nonebot import get_plugin_config
from nonebot import on_command
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Event

from .config import Config
from .csv_writer import write_csv, read_csv

__plugin_meta__ = PluginMetadata(
    name="sleep",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

sleep = on_command("sleep", aliases = {"gn"})
awake = on_command("awake")

@sleep.handle()
async def sleep_handle(event: Event):
    user_id = event.get_user_id()
    current_time = write_csv(user_id)
    if current_time is not None:
        await sleep.finish(message = user_id + f"现在时间是{current_time}，已经记录你的睡觉时间了哦！" + "\n晚安好梦")
    else:
        await sleep.finish(message = user_id + "已经睡着了\n再次记录睡觉时间请先用/awake起床")

@awake.handle()
async def awake_handle(event: Event):
    user_id = event.get_user_id()
    awake_time = read_csv(user_id)
    if awake_time == -1:
        await awake.finish(message = user_id + "清醒得很\n再次记录起床时间请先用/sleep睡觉")
    elif awake_time == -2:
        await awake.finish(message = user_id + "找不到你的睡觉记录\n请先用/sleep睡觉")
    else:
        import time
        sleep_duration = time.time() - float(awake_time)
        def second_to_hms(seconds):
            h, r = divmod(seconds, 3600)
            m, s = divmod(r, 60)
            return f"{int(h)}小时{int(m)}分钟{int(s)}秒"
        
        sleep_duration_str = second_to_hms(sleep_duration)

        await awake.finish(message = user_id + "睡觉时长" + sleep_duration_str + "\n早安新的一天开始了哦！")






