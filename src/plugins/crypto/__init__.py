from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.params import CommandArg

from .config import Config
from .okx_market_data import get_market_data
from .okx_market_kline import get_crypto_kline
from .fear_greed_index import get_market_fear_greed_index

__plugin_meta__ = PluginMetadata(
    name="crypto",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

crypto = on_command("crypto")
@crypto.handle()
async def crypto_handle(args = CommandArg()):
    if cmd_params := args.extract_plain_text():
        if " " in cmd_params:
            cmd_params = cmd_params.split(" ")
            if len(cmd_params) == 2:
                crypto_name = cmd_params[0]
                time_interval = cmd_params[1]
                if time_interval not in ["15m", "1h", "4h", "1D", "3D", "1W"]:
                    await crypto.finish(message = "时间间隔不合法, 目前支持15m/1h/4h/1D/3D/1W")
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