from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command

from .config import Config

__plugin_meta__ = PluginMetadata(
    name="help",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

helper_message = "以下是所有的指令列表:\n \
    /crypto 查看过去2小时交易量涨幅300%及以上的币种\n \
    /crypto [name] 查看[name]币种过去24小时的15分钟k线图\n \
    /help 查看指令列表\n \
    /ncm search [keyword] [num] 网易云搜索前num首关键词为keyword的歌曲\n \
    /ncm id [song_id] 获取song_id对应的歌曲卡片\n \
    /roll xdy 掷x个y面骰子\n \
    /roll xdy+z 掷x个y面骰子,加z点修正值\n \
    /setu 返回随机色图\n \
    /setu [tags] 返回指定tags的色图; 可以传入多个tag, 以空格分隔\n \
    /sleep 开始睡觉并记录睡觉时间\n \
    /awake 结束睡觉, 查看本次睡觉时长和本周平均睡眠时长\n \
    /sleep status 查看本周平均睡眠时长\n \
    /steam [steamid] 查看用户steamid的steam游戏状态\n \
    /work start [name] 开始一项名为[name]的工作\n \
    /work stop 结束当前工作, 查看本次工作时长\n \
    /work today 查看本日工作统计"

_help = on_command("help", aliases = {"帮助"})

@_help.handle()
async def help_handle():
    await _help.finish(message = helper_message)