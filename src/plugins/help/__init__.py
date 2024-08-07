from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command

from .config import Config

from .help import draw_help

__plugin_meta__ = PluginMetadata(
    name="help",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

helper_message = "芙芙目前支持的指令列表:\n \
—————— crypto ——————\n \
/crypto 查看过去2小时交易量涨幅300%及以上的币种\n \
/crypto index 查看当日市场恐慌&贪婪指数\n \
/crypto [name] 查看[name]币种过去24小时的15分钟k线图\n \
/crypto [name] [interval] 返回[name]币种的 15m/1h/4h/1D/1W k线图\n \
—————— image ——————\n \
/喜报 [content] 绘制内容为[content]的喜报\n \
/悲报 [content] 绘制内容为[content]的悲报\n \
对图片回复 /对称 左|右|上|下 [percent] 将图片(以[percent]%为轴)进行对称翻转\n \
—————— mahjong ——————\n \
/qh [username] 查看[username]的近30局雀魂战绩\n \
—————— ncm ——————\n \
/ncm search [keyword] [num] 网易云搜索前num首关键词为keyword的歌曲\n \
/ncm id [song_id] 获取[song_id]对应的歌曲卡片\n \
—————— roll ——————\n \
/roll xdy 掷x个y面骰子\n \
/roll xdy+z 掷x个y面骰子,加z点修正值\n \
—————— setu ——————\n \
/setu 返回随机色图\n \
/setu search 对消息记录中的图片回复该指令进行以图搜图\n \
/setu [tags] 返回指定tags的色图; 可以传入多个tag, 以空格分隔\n \
—————— sleep ——————\n \
/sleep 开始睡觉并记录睡觉时间\n \
/sleep [hh:mm] 手动指定睡觉时间\n \
/sleep [hh:mm] [utc±t] 手动指定于指定时区的睡觉时间\n \
/awake 结束睡觉, 查看本次睡觉时长和本周睡眠状况统计\n \
/awake [hh:mm] 手动指定起床时间\n \
/awake [hh:mm] [utc±t] 手动指定于指定时区的起床时间\n \
/sleep status 查看本周睡眠状况统计\n \
—————— steam ——————\n \
/steam [steamid] 查看用户[steamid]的steam游戏状态\n \
/视奸群友 一键视奸群友游戏状态 \n \
使用/视奸群友 add|remove [steamid] 管理视奸群友列表\n \
—————— work ——————\n \
/work start [name] 开始一项名为[name]的工作\n \
/work stop 结束当前工作, 查看本次工作时长\n \
/work today 查看本日工作统计\n \
————— miscellaneous —————\n \
/yuyu 我有玉玉症\n \
/fufu 芙芙可爱捏\n \
/help 查看指令列表"

_help = on_command("help", aliases = {"帮助"})

@_help.handle()
async def help_handle():
    await _help.finish(message = draw_help(helper_message))