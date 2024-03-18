from nonebot import get_plugin_config
from nonebot import on_command, get_adapter
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.adapters.onebot.v11.adapter import Adapter

from .config import Config
from .sleep_record import record_sleep, record_awake, get_daily_sleep_duration
import time

__plugin_meta__ = PluginMetadata(
    name="sleep",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

LOCAL_TIME = -7

sleep = on_command("sleep", aliases = {"gn"})
awake = on_command("awake")

def second_to_hms(seconds):
            h, r = divmod(seconds, 3600)
            m, s = divmod(r, 60)
            return f"{int(h)}小时{int(m)}分钟{int(s)}秒"

@sleep.handle()
async def sleep_handle(event: MessageEvent, args = CommandArg()):
    user_id = event.get_user_id()
    if "message.group" in str(event.get_event_name()):
        onebot_adapter = get_adapter(Adapter)
        bot = list(onebot_adapter.bots.values())[0]
        group_members_raw = await bot.call_api("get_group_member_list", group_id = event.group_id)
        for member in group_members_raw:
            if str(member["user_id"]) == event.get_user_id():
                user_id = member["nickname"]
                break 
    if cmd_params := args.extract_plain_text():
        if cmd_params == "status":
            await sleep.send(message = f"{user_id}的本周睡眠时长统计如下:")
            await sleep.finish(message = get_daily_sleep_duration(user_id))
        elif ":" in cmd_params:
            if " " in cmd_params:
                time, user_timezone_str = cmd_params.split(" ")
                if "utc+" in user_timezone_str or "utc-" in user_timezone_str:
                    user_timezone = int(user_timezone_str[3:])
                    if user_timezone > 12 or user_timezone < -12:
                        await sleep.finish(message = "请输入合法的时区")
                    else:
                        deltatime = user_timezone - LOCAL_TIME
                        time = time.split(":")
                        hour, minute = (int(time[0]) - deltatime) % 24, int(time[1])
                else:
                    await sleep.finish(message = "格式错误,正确格式为: /sleep [hour:minute] [timezone]\n例如: /sleep 23:00 utc+8\n注意使用英文冒号")
            else:
                hour, minute = map(int, cmd_params.split(":"))
            current_time = record_sleep(user_id, hour, minute)
            if current_time == -1:
                await sleep.finish(message = user_id + "已经睡着了\n再次记录睡觉时间请先用/awake起床")
            elif current_time == -2:
                await sleep.finish(message = user_id + "非法记录:睡觉时间早于上一次起床时间\n请重新输入")
            else:
                await sleep.finish(message = user_id + f"已经记录你于{current_time}的睡觉时间了哦！" + "\n晚安好梦")
        else:
            await sleep.finish(message = "格式错误,正确格式为: /sleep [hour:minute]\n例如: /sleep 23:00\n注意使用英文冒号")
    else:
        user_id = event.get_user_id()
        current_time = record_sleep(user_id)
        if current_time == -1:
            await sleep.finish(message = user_id + "已经睡着了\n再次记录睡觉时间请先用/awake起床")
        elif current_time == -2:
            await sleep.finish(message = user_id + "非法记录:睡觉时间早于上一次起床时间\n请重新输入")
        else:
            await sleep.finish(message = user_id + f"已经记录你于{current_time}的睡觉时间了哦！" + "\n晚安好梦")

@awake.handle()
async def awake_handle(event: MessageEvent, args = CommandArg()):
    user_id = event.get_user_id()
    if "message.group" in str(event.get_event_name()):
        onebot_adapter = get_adapter(Adapter)
        bot = list(onebot_adapter.bots.values())[0]
        group_members_raw = await bot.call_api("get_group_member_list", group_id = event.group_id)
        for member in group_members_raw:
            if str(member["user_id"]) == event.get_user_id():
                user_id = member["nickname"]
                break 
    if cmd_params := args.extract_plain_text():
        if ":" in cmd_params:
            if " " in cmd_params:
                time, user_timezone_str = cmd_params.split(" ")
                if "utc+" in user_timezone_str or "utc-" in user_timezone_str:
                    user_timezone = int(user_timezone_str[3:])
                    if user_timezone > 12 or user_timezone < -12:
                        await awake.finish(message = "请输入合法的时区")
                    else:
                        deltatime = user_timezone - LOCAL_TIME
                        time = time.split(":")
                        hour, minute = (int(time[0]) - deltatime) % 24, int(time[1])
                else:
                    await awake.finish(message = "格式错误,正确格式为: /awake [hour:minute] [timezone]\n例如: /awake 7:00 utc+8\n注意使用英文冒号")
            hour, minute = map(int, cmd_params.split(":"))
            awake_time = record_awake(user_id, hour, minute)
        else:
            await awake.finish(message = "格式错误,正确格式为: /awake [hour:minute]\n例如: /awake 7:00\n注意使用英文冒号")
    else:
        awake_time = record_awake(user_id)
    if awake_time == -1:
        await awake.finish(message = user_id + "清醒得很\n再次记录起床时间请先用/sleep睡觉")
    elif awake_time == -2:
        await awake.finish(message = user_id + "找不到你的睡觉记录\n请先用/sleep睡觉")
    elif awake_time == -3:
        await awake.finish(message = user_id + "起床时间早于上一次睡觉时间\n请重新输入")
    else:
        sleep_duration = float(awake_time)
        sleep_duration_str = second_to_hms(sleep_duration)
        await awake.send(message = user_id + "睡觉时长" + sleep_duration_str + "\n早安新的一天开始了哦!")
        await awake.send(message = f"{user_id}的本周睡眠时长统计如下:")
        await awake.finish(message = get_daily_sleep_duration(user_id))






