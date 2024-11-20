from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.params import CommandArg

from .config import Config
from .github import get_github_chart

__plugin_meta__ = PluginMetadata(
    name="github",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

github = on_command("github")
@github.handle()
async def github_handle_func(args = CommandArg()):
    cmd_params = args.extract_plain_text()
    if " " in cmd_params:
        cmd_params_list = cmd_params.split(" ")
        if "-2d" in cmd_params_list:
            cmd_params_list.remove("-2d")
            username = " ".join(cmd_params_list)
            message = await get_github_chart(username, _2d = True)
        else: message = await get_github_chart(" ".join(cmd_params_list))
    else: message = await get_github_chart(cmd_params)
    await github.finish(message = message)