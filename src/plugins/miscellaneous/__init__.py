from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11.adapter import Bot
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.permission import SUPERUSER
from nonebot.exception import IgnoredException
from nonebot.adapters.onebot.v11.event import PokeNotifyEvent, GroupMessageEvent, GroupDecreaseNoticeEvent, GroupIncreaseNoticeEvent

from .config import Config
from nonebot import on_command, on_fullmatch, on_notice, on_keyword
from nonebot.rule import to_me
from utils.utils import get_asset_path
from utils.cooldown import Cooldown

from utils import global_plugin_ctrl

__plugin_meta__ = PluginMetadata(
    name="miscellaneous",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

zm = on_fullmatch("在吗", rule=to_me())

@zm.handle()
async def welcome_handle_func():
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
async def ciallo_handle_func(event: GroupMessageEvent):
    global last_ciallo_time
    if last_ciallo_time.use(event.group_id)[0]:
        await ciallo.finish(MessageSegment.record("file:///" + get_asset_path("ciallo.mp3")))
    else: return

leave = on_notice()
leave_ctrl = global_plugin_ctrl.create_plugin(names = ["leave"], description = "群友退群通知", default_on = True)

@leave.handle()
async def leave_handle(event: GroupDecreaseNoticeEvent, bot: Bot):
    if not leave_ctrl.check_plugin_ctrl(event.group_id): raise IgnoredException("Plugin off in this group")
    user_info = await bot.call_api("get_stranger_info", user_id = event.user_id)
    nickname = user_info["nickname"]
    await leave.finish(f"{nickname} ({event.user_id}) 退群了, 呜呜呜")

welcome = on_notice()
welcome_ctrl = global_plugin_ctrl.create_plugin(names = ["welcome"], description = "欢迎新群友", default_on = True)

@welcome.handle()
async def welcome_handle(event: GroupIncreaseNoticeEvent):
    if not welcome_ctrl.check_plugin_ctrl(event.group_id): raise IgnoredException("Plugin off in this group")
    message = Message([MessageSegment.at(event.user_id), MessageSegment.text(" 欢迎新群友，喜欢您来"),
                      MessageSegment.image("file:///" + get_asset_path("images/fufu.gif"))])
    await welcome.finish(message)

recall = on_command("recall", permission = SUPERUSER)

@recall.handle()
async def recall_handle_func(event: GroupMessageEvent, bot: Bot):
    if event.reply:
        await bot.call_api("delete_msg", message_id = event.reply.message_id)