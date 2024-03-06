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
    if crypto_name := args.extract_plain_text():
        message = get_crypto_kline(crypto_name)
        await crpyto.finish(message = message)
    else:
        message = get_market_data()
        await crpyto.finish(message = message)