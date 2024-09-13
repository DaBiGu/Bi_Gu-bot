from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command, get_adapter
from nonebot.adapters.onebot.v11.event import MessageEvent
from nonebot.adapters.onebot.v11.adapter import Adapter
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11.message import MessageSegment, Message
import time

from .config import Config
from .work_recorder import start_work, stop_work
from .today_work_analysis import today_work_analysis
from utils.utils import second_to_hms

__plugin_meta__ = PluginMetadata(
    name="work",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

work = on_command("work") 

@work.handle()
async def work_handle(event: MessageEvent, args = CommandArg()):
    username = event.get_user_id()
    if "message.group" in str(event.get_event_name()):
        onebot_adapter = get_adapter(Adapter)
        bot = list(onebot_adapter.bots.values())[0]
        group_members_raw = await bot.call_api("get_group_member_list", group_id = event.group_id)
        for member in group_members_raw:
            if str(member["user_id"]) == event.get_user_id():
                username = member["nickname"]
                break 
    if work_command := args.extract_plain_text().split(" "):
        work_command_name = work_command[0]
        if work_command_name == "start":
            work_status = start_work(user_id = event.get_user_id(), work_id = work_command[1])
            if work_status == -1:
                await work.finish(message = "有正在进行的工作,请用/work stop结束当前工作")
            else:
                await work.finish(message = f"{username}成功开始工作{work_command[1]}\n当前时间{work_status}")
        elif work_command_name == "stop":
            work_status = stop_work(user_id = event.get_user_id())
            if work_status[0] == -1:
                await work.finish(message = "没有正在进行的工作,请用/work start开始工作")
            else:
                work_duration = time.time() - float(work_status[0]) 
                work_duration_str = second_to_hms(work_duration)
                await work.finish(message = f"{username}成功结束工作{work_status[1]}\n工作时长{work_duration_str}")
        elif work_command_name == "today":
            _today_work_analysis, work_time = today_work_analysis(user_id = event.get_user_id())
            work_time_str = second_to_hms(work_time)
            await work.finish(message = Message([_today_work_analysis, MessageSegment.text(f"{username}今日工作总时长{work_time_str}")]))

