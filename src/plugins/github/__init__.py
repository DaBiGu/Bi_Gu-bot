from nonebot import get_plugin_config
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg

from .config import Config
from .github import get_github_chart

from utils import global_plugin_ctrl

__plugin_meta__ = PluginMetadata(
    name="github",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)

_github = global_plugin_ctrl.create_plugin(names = ["github"], description = "查看github用户数据",
                                          help_info = """
                                                        /github [username] 查看[username]的github contributions chart
                                                            可选参数 -2d 返回原始2d图
                                                      """,
                                          default_on = True, priority = 1)
github = _github.base_plugin

@github.handle()
async def github_handle_func(args = CommandArg()):
    cmd_params = args.extract_plain_text()
    if _github.check_base_plugin_functions(cmd_params): return
    if " " in cmd_params:
        cmd_params_list = cmd_params.split(" ")
        if "-2d" in cmd_params_list:
            cmd_params_list.remove("-2d")
            username = " ".join(cmd_params_list)
            message = await get_github_chart(username, _2d = True)
        else: message = await get_github_chart(" ".join(cmd_params_list))
    else: message = await get_github_chart(cmd_params)
    await github.finish(message = message)