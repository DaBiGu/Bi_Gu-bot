import nonebot, os
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
from nonebot.adapters.console import Adapter as CONSOLEAdapter
from sys import path
path.append(os.getcwd() + "/passwords")
path.append(os.getcwd() + "/src")

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)

driver.register_adapter(CONSOLEAdapter)

nonebot.load_builtin_plugins('echo', 'single_session')


nonebot.load_from_toml("pyproject.toml")

if __name__ == "__main__":
    nonebot.run()