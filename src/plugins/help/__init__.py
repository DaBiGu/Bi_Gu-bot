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

helper_messages = ["芙芙目前支持的指令列表(按首字母顺序排列):\n \
———————— crypto ————————\n \
/crypto 查看过去2小时交易量涨幅300%及以上的币种\n \
/crypto index 查看当日市场恐慌&贪婪指数\n \
/crypto [name] 查看[name]币种过去24小时的15分钟k线图\n \
/crypto [name] [interval] 返回[name]币种的 15m/1h/4h/1D/1W k线图\n \
———————— group_msg ————————\n \
/antirecall on|off 开启/关闭群内消息防撤回\n \
/chatcount today|week|month 查看今日/本周/本月群内b话量top10\n \
———————— image ————————\n \
/喜报 [content] 绘制内容为[content]的喜报\n \
/悲报 [content] 绘制内容为[content]的悲报\n \
对图片回复 /对称 左|右|上|下 [percent] 将图片(以[percent]%为轴)进行对称翻转\n \
———————— mahjong ————————\n \
/qh [username] 查看[username]的近30局雀魂战绩\n \
———————— ncm ————————\n \
/ncm search [keyword] [num] 网易云搜索前num首关键词为keyword的歌曲\n \
/ncm id [song_id] 获取[song_id]对应的歌曲卡片\n \
/ncm lyrics [song_id] 获取id为[song_id]歌曲的歌词(施工中)\n \
———————— roll ————————\n \
/rd xdy 掷x个y面骰子\n \
/rd xdy+z 掷x个y面骰子,加z点修正值\n \
———————— setu ————————\n \
/setu 返回随机色图\n \
/setu search 对消息记录中的图片回复该指令进行以图搜图\n \
/setu [tags] 返回指定tags的色图; 可以传入多个tag, 以空格分隔\n \
———————— sleep ————————\n \
/sleep 开始睡觉并记录睡觉时间\n \
/sleep [hh:mm] 手动指定睡觉时间\n \
/sleep [hh:mm] [utc±t] 手动指定于指定时区的睡觉时间\n \
/awake 结束睡觉, 查看本次睡觉时长和本周睡眠状况统计\n \
/awake [hh:mm] 手动指定起床时间\n \
/awake [hh:mm] [utc±t] 手动指定于指定时区的起床时间\n \
/sleep status 查看本周睡眠状况统计",

"———————— steam ————————\n \
/steam [steamid] 查看用户[steamid]的steam游戏状态\n \
/steam random [steamid] 随机从用户[steamid]的库存推荐游戏\n \
/steam random [steamid] [appid] 从用户[steamid]的库存推荐id为[appid]的游戏\n \
/steam search [name] 搜索名为[name]的steam游戏\n \
/视奸群友 一键视奸群友游戏状态 \n \
使用/视奸群友 add|remove [steamid] 管理视奸群友列表\n \
———————— wife ————————\n \
/wife 今日随机群老婆 \n \
/wife -s 今日随机群老婆, 不@对方\n \
———————— work ————————\n \
/work start [name] 开始一项名为[name]的工作\n \
/work stop 结束当前工作, 查看本次工作时长\n \
/work today 查看本日工作统计\n \
———————— miscellaneous ————————\n \
/yuyu 我有玉玉症\n \
/fufu 芙芙可爱捏\n \
/help 查看指令列表"]

_help = on_command("help", aliases = {"帮助"})

@_help.handle()
async def help_handle():
    for i in range(len(helper_messages)):
        await _help.send(draw_help(helper_messages[i], i+1, len(helper_messages)))