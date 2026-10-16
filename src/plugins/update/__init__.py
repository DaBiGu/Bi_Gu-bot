from nonebot import get_plugin_config, get_bot
from nonebot.plugin import PluginMetadata
from nonebot.permission import SUPERUSER
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot_plugin_apscheduler import scheduler
from nonebot.log import logger

from .config import Config
from .draw_update_message import draw_update_message
from ..help.about import on_disconnect
from utils.utils import get_data_path, get_asset_path
from utils.chrome import chromedriver_filename, chromedriver_platform_tag
from utils.platforms import get_platform, restart_argv, restart_hint

import subprocess, os, sys, asyncio, requests, zipfile, shutil

__plugin_meta__ = PluginMetadata(
    name="update",
    description="",
    usage="",
    config=Config,
)

config = get_plugin_config(Config)
permission = SUPERUSER

update = on_command("update", priority = 2)


def request_restart() -> bool:
    argv = restart_argv(os.getpid())
    if argv is None:
        logger.info(f"平台由进程管理器托管（{restart_hint()}），退出进程以触发重启")
        return False
    subprocess.Popen(argv)
    return True


def exit_for_restart() -> None:
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)

@update.handle()
async def update_handle(bot: Bot, event: GroupMessageEvent):
    if not await permission(bot, event):
        await update.finish(message = "你没有权限执行此操作")
    def git_pull() -> tuple[int, str]:
        proc = subprocess.run(["git", "pull"], cwd = os.getcwd(),
                capture_output = True, text = True, timeout = 300)
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    try:
        returncode, output = await asyncio.to_thread(git_pull)
    except subprocess.TimeoutExpired:
        await update.finish(message = "git pull 超时，未做任何改动，也不会重启")
    except FileNotFoundError:
        await update.finish(message = "找不到 git 命令，无法执行更新")
    if returncode != 0:
        await update.finish(message = f"git pull 失败（退出码 {returncode}），已放弃更新且不会重启：\n{output.strip()[:600]}")
    if "Already up to date" in output:
        await update.finish(message = "Already up to date")
    await update.send(message = draw_update_message(output))
    await on_disconnect(bot)
    if not request_restart(): exit_for_restart()

_reboot = on_command("reboot")

@scheduler.scheduled_job("cron", hour = 3, minute = 30)
async def reboot():
    await on_disconnect(get_bot())
    if not request_restart(): exit_for_restart()

@_reboot.handle()
async def reboot_handle(bot: Bot, event: GroupMessageEvent):
    if not await permission(bot, event):
        await update.finish(message = "你没有权限执行此操作")
    await _reboot.send(message = "芙芙重启中...")
    await reboot()

_update_chromedriver = on_command("update chromedriver", priority = 1, permission = permission)
@scheduler.scheduled_job("cron", hour = 0, minute = 0)
@_update_chromedriver.handle()
async def update_chromedriver():
    request_url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
    platform_tag = chromedriver_platform_tag()
    driver_name = chromedriver_filename()
    zip_dir = f"chromedriver-{platform_tag}"

    download_url = None
    for data in requests.get(request_url).json()["channels"]["Stable"]["downloads"]["chromedriver"]:
        if data["platform"] == platform_tag:
            download_url = data["url"]
            break
    if not download_url:
        logger.error(f"未在 Chrome for Testing 清单中找到 {platform_tag} 平台的 chromedriver")
        return

    archive = get_data_path("chromedriver.zip", temp = True)
    with open(archive, "wb") as file: file.write(requests.get(download_url).content)
    with zipfile.ZipFile(archive, "r") as file: file.extractall(get_data_path(temp = True))

    output_path = get_asset_path("chrome")
    target = os.path.join(output_path, driver_name)
    if os.path.exists(target): os.remove(target)
    shutil.move(get_data_path(f"{zip_dir}/{driver_name}", temp = True), output_path)
    if get_platform() != "windows":
        os.chmod(os.path.join(output_path, driver_name), 0o755)

    logger.info(f"chromedriver 已更新（{platform_tag} -> {driver_name}）")