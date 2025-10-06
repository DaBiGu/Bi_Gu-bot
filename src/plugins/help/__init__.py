from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.matcher import Matcher
from nonebot.message import run_postprocessor
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from typing import Optional
import json, re, datetime

from .config import Config

from .help import draw_help
from .helper_message import Helper_Messages
from .about import generate_bot_status_image, get_brief_bot_status, get_about_image, on_disconnect, on_connect, draw_funccount_bargraph

from utils import global_plugin_ctrl
from utils.utils import get_IO_path

__plugin_meta__ = PluginMetadata(
    name="help",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

helper_messages = Helper_Messages().get_helper_messages()
update_logs = Helper_Messages().get_update_logs()
funccount_json_path = get_IO_path("funccount", "json")

_help = on_command("help", aliases = {"帮助"})

@_help.handle()
async def help_handle():
    for i in range(len(helper_messages)):
        await _help.send(draw_help(helper_messages[i], i+1, len(helper_messages)))

_update_log = on_command("update log", priority = 1)

@_update_log.handle()
async def update_log_handle():
    for i in range(len(update_logs)):
        await _update_log.send(draw_help(update_logs[i], i+1, len(update_logs)))

_plugin_status = on_command("plugin status")
@_plugin_status.handle()
async def plugin_status_handle(event: GroupMessageEvent):
    on, off = global_plugin_ctrl.check_plugin_status(event.group_id)
    await _plugin_status.finish("本群插件状态\n\n开启的插件: " + " | ".join(sorted(on)) + "\n关闭的插件: " + " | ".join(sorted(off)))

_plugin_help = on_command("plugin help")
@_plugin_help.handle()
async def plugin_help_handle():
    await _plugin_help.finish(global_plugin_ctrl.get_help_info())

_plugin_count = on_command("plugin count", aliases={"pc"})
@_plugin_count.handle()
async def plugin_count_handle():
    await _plugin_count.finish(draw_funccount_bargraph())

_status = on_command("status")
@_status.handle()
async def status_handle(bot: Bot, args = CommandArg()):
    if cmd_params := args.extract_plain_text():
        if cmd_params == "-b":
            line1, line2 = get_brief_bot_status(bot_id = bot.self_id)
            await _status.finish(message = line1 + "\n" + line2)
    await _status.finish(generate_bot_status_image(bot_id = bot.self_id))

_about = on_command("about")
@_about.handle()
async def about_handle(bot: Bot, event: GroupMessageEvent):
    text = "https://github.com/DaBiGu/Bi_Gu-bot\n点个star谢谢喵"
    message = Message([get_about_image(), MessageSegment.text(text)])
    await _about.finish(message)

@run_postprocessor
async def count_handler_trigger(event: GroupMessageEvent, matcher: Matcher, exception: Optional[Exception]):
    passive_funcs = ["group_message"]
    _ = matcher.handlers
    handler = _[0] if _ else None
    if handler:
        match = re.search(r"Dependent\(call=([a-zA-Z_][a-zA-Z0-9_]*)_handle\)", str(handler))
        funcname = match.group(1) if match else None
        with open(funccount_json_path, "r") as f: funccount = json.load(f)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        if today not in funccount: funccount[today] = {}
        if funcname:
            if funcname in passive_funcs: return
            if funcname not in funccount[today]: funccount[today][funcname] = 0
            funccount[today][funcname] += 1
        with open(funccount_json_path, "w") as f: json.dump(funccount, f)