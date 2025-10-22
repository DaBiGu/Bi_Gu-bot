from nonebot import get_plugin_config, get_bot
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11.adapter import Bot
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.permission import SUPERUSER
from nonebot_plugin_apscheduler import scheduler
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11.event import PokeNotifyEvent, GroupMessageEvent, GroupDecreaseNoticeEvent, GroupIncreaseNoticeEvent

from .config import Config
from nonebot import on_command, on_fullmatch, on_notice, on_keyword
from nonebot.rule import to_me
from utils.utils import get_asset_path, get_IO_path
from utils.cooldown import Cooldown

from utils import global_plugin_ctrl

import json, time, datetime

__plugin_meta__ = PluginMetadata(
    name="miscellaneous",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

zm = on_fullmatch("在吗", rule=to_me())

@zm.handle()
async def zm_handle():
    await zm.finish("はい、芙芙会一直陪伴在大家身边")

poke = on_notice()

@poke.handle()
async def poke_handle(event: PokeNotifyEvent, bot: Bot):
    if event.is_tome():
        if event.group_id: await bot.call_api("group_poke", group_id = event.group_id, user_id = event.user_id)
        else: await bot.call_api("friend_poke", user_id = event.user_id)

ciallo = on_keyword(["ciallo", "Ciallo"])
last_ciallo_time = Cooldown(countdown = 300.0)

@ciallo.handle()
async def ciallo_handle(event: GroupMessageEvent):
    global last_ciallo_time
    if last_ciallo_time.use(event.group_id)[0]:
        await ciallo.finish(MessageSegment.record("file:///" + get_asset_path("ciallo.mp3")))
    else: return

leave = on_notice()
leave_ctrl = global_plugin_ctrl.create_plugin(names = ["leave"], description = "群友退群通知", default_on = True)

@leave.handle()
async def leave_handle(event: GroupDecreaseNoticeEvent, bot: Bot):
    if not leave_ctrl.check_plugin_ctrl(event.group_id): return
    user_info = await bot.call_api("get_stranger_info", user_id = event.user_id)
    nickname = user_info["nickname"]
    await leave.finish(f"{nickname} ({event.user_id}) 退群了, 呜呜呜")

welcome = on_notice()
welcome_ctrl = global_plugin_ctrl.create_plugin(names = ["welcome"], description = "欢迎新群友", default_on = True)

@welcome.handle()
async def welcome_handle(event: GroupIncreaseNoticeEvent):
    if not welcome_ctrl.check_plugin_ctrl(event.group_id): return
    message = Message([MessageSegment.at(event.user_id), MessageSegment.text(" 欢迎新群友，喜欢您来"),
                      MessageSegment.image("file:///" + get_asset_path("images/fufu.gif"))])
    await welcome.finish(message)

recall = on_command("recall", permission = SUPERUSER)

@recall.handle()
async def recall_handle(event: GroupMessageEvent, bot: Bot):
    if event.reply:
        await bot.call_api("delete_msg", message_id = event.reply.message_id)

_like = global_plugin_ctrl.create_plugin(names = ["like"], description = "qq资料卡点赞", default_on = True)
like = _like.base_plugin

async def execute_like(user_id: str, bot: Bot) -> str:
    with open(get_IO_path("qq_like", "json"), "r") as f: record = json.load(f)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    if user_id not in record: record[user_id] = "1970-01-01"
    status = "already_liked"
    if record[user_id] != today: 
        try: await bot.call_api("send_like", user_id = int(user_id), times = 10)
        except Exception: status = "like_failed"
        else: 
            record[user_id] = today
            status = "like_succeed"
    with open(get_IO_path("qq_like", "json"), "w") as f: json.dump(record, f)
    return status

@like.handle()
async def like_handle(event: GroupMessageEvent, bot: Bot, args = CommandArg()):
    if _like.check_base_plugin_functions(command_args:=args.extract_plain_text()): return
    with open(get_IO_path("qq_like", "json"), "r") as f: record = json.load(f)
    if command_args == "auto":
        if str(event.user_id) not in record["auto"]: 
            record["auto"].append(str(event.user_id))
            message = Message([MessageSegment.at(event.user_id), MessageSegment.text(" 添加成功，现在芙芙每天都会给你的资料卡点赞啦")])
        else: message = Message([MessageSegment.at(event.user_id), MessageSegment.text(" 已经添加过啦, 芙芙会记得点赞的")])
    else:
        status = await execute_like(str(event.user_id), bot)
        message = Message([MessageSegment.text("芙芙给你的资料卡点赞啦~一天内请勿重复使用哦"),
                           MessageSegment.image("file:///" + get_asset_path("images/fufu.gif"))]) if status == "like_succeed" \
                  else Message([MessageSegment.text("芙芙今天已经给你点过赞啦，明天再来吧")]) if status == "already_liked" \
                  else Message([MessageSegment.text("点赞失败了，请检查点赞权限设置")])
    with open(get_IO_path("qq_like", "json"), "w") as f: json.dump(record, f)
    await like.finish(message)

manual_like = on_command("execute like", permission = SUPERUSER)

@manual_like.handle()
@scheduler.scheduled_job("cron", hour = 4, minute = 0)
async def auto_like():
    with open(get_IO_path("qq_like", "json"), "r") as f: record = json.load(f)
    for user_id in record["auto"]:
        await execute_like(user_id, get_bot())

like.append_handler(like_handle)

gettime = on_command("time")

@gettime.handle()
async def gettime_handle():
    unix_time = int(time.time())
    local_time = datetime.datetime.now().astimezone()
    total_hours = local_time.utcoffset().total_seconds() / 3600
    await gettime.finish(f"Current time:\nUnix epoch: {unix_time}\nLocal time: {local_time.strftime('%Y-%m-%d %H:%M:%S')} [UTC{total_hours:+.0f}]")