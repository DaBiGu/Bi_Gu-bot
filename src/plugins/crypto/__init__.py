from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.params import CommandArg

from .config import Config
from .okx_market_data import get_market_data
from .okx_market_kline import get_crypto_kline

__plugin_meta__ = PluginMetadata(
    name="crypto",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

crpyto = on_command("crypto")
@crpyto.handle()
async def crypto_handle(args = CommandArg()):
    if cmd_params := args.extract_plain_text():
        if " " in cmd_params:
            cmd_params = cmd_params.split(" ")
            if len(cmd_params) == 2:
                crypto_name = cmd_params[0]
                time_interval = cmd_params[1]
                if time_interval not in ["15m", "1h", "4h", "1D", "3D", "1W"]:
                    await crpyto.finish(message = "时间间隔不合法, 目前支持15m/1h/4h/1D/3D/1W")
                else:
                    message = get_crypto_kline(crypto_name, time_interval)
                    await crpyto.finish(message = message)
        else:
            message = get_crypto_kline(cmd_params)
            await crpyto.finish(message = message)
    else:
        message = get_market_data()
        await crpyto.finish(message = message)