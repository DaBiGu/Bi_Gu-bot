import nonebot, os
from sys import path
path.append(os.getcwd() + "/passwords")
path.append(os.getcwd() + "/src")

from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
from utils.onebot_file_compat import install as install_onebot_file_compat

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)

# NTQQ runs in the SnowLuma container on Linux, which cannot see host paths,
# so local files have to be inlined before they reach the adapter.
install_onebot_file_compat()

nonebot.load_builtin_plugins('echo', 'single_session')


nonebot.load_from_toml("pyproject.toml")

if __name__ == "__main__":
    nonebot.run()