from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from .config import Config
from .okx_market_data import get_market_data
from .okx_market_kline import get_crypto_kline
from .fear_greed_index import get_market_fear_greed_index

from utils import global_plugin_ctrl

__plugin_meta__ = PluginMetadata(
    name="crypto",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)


_crypto = global_plugin_ctrl.create_plugin(names = ["crypto"], description = "okx市场数据", 
                                          help_info = """
                                                        /crypto 查看过去2小时交易量涨幅300%及以上的币种
                                                        /crypto index 查看当日市场恐慌&贪婪指数
                                                        /crypto [name] 查看[name]币种过去24小时的15分钟k线图
                                                        /crypto [name] [interval] 返回[name]币种的 15m/1h/4h/1D/1W k线图
                                                      """,
                                          default_on = True, priority = 1)
crypto = _crypto.base_plugin

@crypto.handle()
async def crypto_handle(event: GroupMessageEvent, args = CommandArg()):
    if not _crypto.check_plugin_ctrl(event.group_id): await crypto.finish("该插件在本群中已关闭")
    if cmd_params := args.extract_plain_text():
        if _crypto.check_base_plugin_functions(cmd_params): return
        if " " in cmd_params:
            cmd_params = cmd_params.split(" ")
            if len(cmd_params) == 2:
                crypto_name = str(cmd_params[0]).upper()
                time_interval = cmd_params[1]
                if time_interval not in ["1m", "5m", "15m", "1h", "4h", "1D", "3D", "1W", "1d", "3d", "1w"]:
                    await crypto.finish(message = "时间间隔不合法, 目前支持1m/5m/15m/1h/4h/1D/3D/1W")
                else:
                    message = get_crypto_kline(crypto_name, time_interval)
                    await crypto.finish(message = message)
        else:
            if cmd_params == "index":
                message = get_market_fear_greed_index()
                await crypto.finish(message = message)
            else:
                message = get_crypto_kline(cmd_params)
                await crypto.finish(message = message)
    else:
        message = get_market_data()
        await crypto.finish(message = message)

crypto.append_handler(crypto_handle)