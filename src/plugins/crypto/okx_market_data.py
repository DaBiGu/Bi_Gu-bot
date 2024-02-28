import okx.MarketData as MarketData
import okx.PublicData as PublicData
import time, datetime

from sys import path
path.append("D:/Bi_Gu-bot/passwords")
from passwords import get_passwords

def get_market_data() -> str:
    api_info = {"flag": "0", "api_key": get_passwords("okx_api_key"),
            "api_secret_key": get_passwords("okx_api_secret_key"), "passphrase": get_passwords("okx_passphrase")}
    marketDataAPI = MarketData.MarketAPI(**api_info, debug = False)
    publicDataAPI = PublicData.PublicAPI(**api_info, debug = False)
    instrument_data = publicDataAPI.get_instruments(instType="SWAP")["data"]
    instrument_list = [x["instId"] for x in instrument_data if x["settleCcy"] == "USDT"]
    current_time = datetime.datetime.now()
    message = f"============= Volume Spike Detection at {current_time} =============\n"
    for x in instrument_list:
        before_time = int(round(time.time() * 1000)) - 3600000 * 5
        after_time = int(round(time.time() * 1000)) - 3600000
        result = marketDataAPI.get_candlesticks(instId=x, bar="2H", before = before_time, after = after_time)
        vols = [float(x[7]) for x in result["data"]]
        if vols:
            if vols[0] / vols[1] >= 3:
                increase = "{:.2f}".format(vols[0] / vols[1] * 100)
                message += f"Trading pair {x} has a volume spike, increasing by {increase}% times.\n"
    return message
        
