from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import get_bot, require, on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg

from .config import Config
from .okx_market_data import get_market_data
from .okx_market_kline import get_crypto_kline

__plugin_meta__ = PluginMetadata(
    name="crypto_test",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

@scheduler.scheduled_job("interval", hours = 10)
async def still_alive():
    bot = get_bot("3483605368")
    print("Still alive")
    await bot.send_group_msg(group_id = 157563170, message = "又活了一天,我还没似呢")

@scheduler.scheduled_job("interval", hours = 2)
async def send_market_data():
    bot = get_bot("3483605368")
    print("Sending market data")
    message = get_market_data()
    await bot.send_group_msg(group_id = 157563170, message = message)

crpyto = on_command("crypto")
@crpyto.handle()
async def crypto_handle(args = CommandArg()):
    if crypto_name := args.extract_plain_text():
        message = get_crypto_kline(crypto_name)
        await crpyto.finish(message = message)
    else:
        message = get_market_data()
        await crpyto.finish(message = message)