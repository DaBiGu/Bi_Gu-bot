from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command, on_fullmatch
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from utils.utils import get_output_path
from utils.cooldown import Cooldown

from .config import Config
from .good_bad_news import draw_good_news, draw_bad_news
from .symmetric import _symmetric
from .gen_ba import gen_ba

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
async def xb_handle_func(event: GroupMessageEvent, args = CommandArg()):
    if not _xb.check_plugin_ctrl(event.group_id): await xb.finish("该插件在本群中已关闭")
    text = args.extract_plain_text()
    message = await draw_good_news(text)
    await xb.finish(message = message)

@bb.handle()
async def bb_handle_func(event: GroupMessageEvent, args = CommandArg()):
    if not _bb.check_plugin_ctrl(event.group_id): await bb.finish("该插件在本群中已关闭")
    text = args.extract_plain_text()
    message = await draw_bad_news(text)
    await bb.finish(message = message)

last_symmetric_time = Cooldown(countdown = 180.0)

_symmetric = global_plugin_ctrl.create_plugin(names = ["对称", "symmetric"], description = "图片对称",
                                             help_info = "对图片回复 /对称 左|右|上|下 [percent] 将图片(以[percent]%为轴)进行对称翻转",
                                             default_on = True, priority = 1)
symmetric = _symmetric.base_plugin
@symmetric.handle()
async def symmetric_handle(event: GroupMessageEvent, args = CommandArg()):
    if not _symmetric.check_plugin_ctrl(event.group_id): await symmetric.finish("该插件在本群中已关闭")
    cmd_params = args.extract_plain_text() 
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
    if not ba.check_plugin_ctrl(event.group_id): await ba.finish("该插件在本群中已关闭")
    if cmd_params := args.extract_plain_text():
        left, right = cmd_params.split(" ") if " " in cmd_params else (cmd_params, "")
        message = await gen_ba(left, right)
        await ba.finish(message = message)