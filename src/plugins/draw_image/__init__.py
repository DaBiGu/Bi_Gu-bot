from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageSegment
from utils.utils import get_output_path
from utils.cooldown import Cooldown

from .config import Config
from .good_bad_news import draw_good_news, draw_bad_news
from .symmetric import _symmetric
from .gen_ba import gen_ba
from .quote import draw_quote_from_reply, draw_quote_from_search, get_search_result_text, draw_quote_from_id

from utils import global_plugin_ctrl

import requests, os, datetime

__plugin_meta__ = PluginMetadata(
    name="draw_image",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

_xb = global_plugin_ctrl.create_plugin(names = ["喜报", "xb"], description = "绘制喜报", 
                                      help_info = "/喜报 [content] 绘制内容为[content]的喜报", default_on = True,
                                      priority = 1)

_bb = global_plugin_ctrl.create_plugin(names = ["悲报", "bb"], description = "绘制悲报", 
                                      help_info = "/悲报 [content] 绘制内容为[content]的悲报", default_on = True,
                                      priority = 1)

xb, bb = _xb.base_plugin, _bb.base_plugin

@xb.handle()
async def xb_handle(event: GroupMessageEvent, args = CommandArg()):
    if not _xb.check_plugin_ctrl(event.group_id): await xb.finish("该插件在本群中已关闭")
    if _xb.check_base_plugin_functions(text:=args.extract_plain_text()): return
    message = await draw_good_news(text)
    await xb.finish(message = message)

@bb.handle()
async def bb_handle(event: GroupMessageEvent, args = CommandArg()):
    if not _bb.check_plugin_ctrl(event.group_id): await bb.finish("该插件在本群中已关闭")
    if _bb.check_base_plugin_functions(text:=args.extract_plain_text()): return
    message = await draw_bad_news(text)
    await bb.finish(message = message)

last_symmetric_time = Cooldown(countdown = 60.0)

symmetric_ctrl = global_plugin_ctrl.create_plugin(names = ["对称", "symmetric"], description = "图片对称",
                                             help_info = "对图片回复 /对称 左|右|上|下 [percent] 将图片(以[percent]%为轴)进行对称翻转",
                                             default_on = True, priority = 1)
symmetric = symmetric_ctrl.base_plugin
@symmetric.handle()
async def symmetric_handle(event: GroupMessageEvent, args = CommandArg()):
    if not symmetric_ctrl.check_plugin_ctrl(event.group_id): await symmetric.finish("该插件在本群中已关闭")
    cmd_params = args.extract_plain_text() 
    if symmetric_ctrl.check_base_plugin_functions(cmd_params): return
    source_url = None
    for seg in event.reply.message:
        if seg.type == "image":
            source_url = seg.data.get("url")
            break
    if source_url:
        original_img_path = get_output_path("symmetric_original", temp = True)
        with open(original_img_path, "wb") as f:
            f.write(requests.get(source_url).content)
        directions = {"左": "left", "右": "right", "上": "up", "下": "down", 
                      "left": "left", "right": "right", "up": "up", "down": "down"}
        direction, percent = cmd_params.split(" ") if " " in cmd_params else (cmd_params, 50)
        if direction in directions: direction = directions.get(direction) 
        else: direction = "left"
        message = await _symmetric(original_img_path, direction, int(percent))
        if isinstance(message, MessageSegment):
            if not last_symmetric_time.use(event.group_id)[0]:
                remaining_time = last_symmetric_time.use(event.group_id)[1]
                await symmetric.finish(f"该功能还有{remaining_time}秒冷却时间")
            else: await symmetric.finish(message = message)
        else: await symmetric.finish(message = message)
    else:
        await symmetric.finish("找不到源图片\ntips: 不支持表情, 可以截图后进行操作; bot无法获取自己发送的图片")

_ba = global_plugin_ctrl.create_plugin(names = ["ba", "bagen"], description = "生成ba风格标题",
                                      help_info = "/ba [left] [right] 生成自定义ba风格标题",
                                      default_on = True, priority = 1)
ba = _ba.base_plugin

@ba.handle()
async def ba_handle(event: GroupMessageEvent, args = CommandArg()):
    if not _ba.check_plugin_ctrl(event.group_id): await ba.finish("该插件在本群中已关闭")
    if cmd_params := args.extract_plain_text():
        if _ba.check_base_plugin_functions(cmd_params): return
        left, right = cmd_params.split(" ") if " " in cmd_params else (cmd_params, "")
        message = await gen_ba(left, right)
        await ba.finish(message = message)

_q = global_plugin_ctrl.create_plugin(names = ["q", "quote"], description = "引用消息生成卡片",
                                      help_info = "/q 对群内某条消息进行回复后发送该指令，生成引用图\n"
                                                  "/q -s [keyword] 随机返回本群包含关键词的引用卡片\n"
                                                  "/q -s [keyword] -all 返回本群包含关键词的全部引用文本\n"
                                                  "/q -id [id] 按编号返回对应引用卡片",
                                      default_on = True, priority = 1)
q = _q.base_plugin

@q.handle()
async def q_handle(event: GroupMessageEvent, bot: Bot, args = CommandArg()):
    if not _q.check_plugin_ctrl(event.group_id): await q.finish("该插件在本群中已关闭")
    if _q.check_base_plugin_functions(cmd_params := args.extract_plain_text()): return
    cmd_params = cmd_params.strip()
    if not cmd_params:
        message = await draw_quote_from_reply(bot, event)
        await q.finish(message = message)

    params = cmd_params.split()
    if len(params) >= 2 and params[0] == "-s":
        keyword = params[1]
        if "-all" in params[2:]: await q.finish(get_search_result_text(event.group_id, keyword))
        message = await draw_quote_from_search(bot, event, keyword)
        await q.finish(message = message)

    if len(params) == 2 and params[0] == "-id":
        if not params[1].isdigit(): await q.finish("编号必须是正整数")
        message = await draw_quote_from_id(bot, event, int(params[1]))
        await q.finish(message = message)

    await q.finish("参数格式错误\n"
                   "/q\n"
                   "/q -s [keyword]\n"
                   "/q -s [keyword] -all\n"
                   "/q -id [id]")

xb.append_handler(xb_handle); bb.append_handler(bb_handle); symmetric.append_handler(symmetric_handle)
ba.append_handler(ba_handle); q.append_handler(q_handle)