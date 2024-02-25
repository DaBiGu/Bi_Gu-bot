from nonebot.adapters.onebot.v11.message import MessageSegment
import okx.MarketData as MarketData
import okx.PublicData as PublicData
import datetime, time
import pandas as pd
import mplfinance as mpf

from sys import path
path.append("D:/Bi_Gu-bot/passwords")
from passwords import get_passwords

def get_crypto_kline(crypto_name):
    api_info = {"flag": "0", "api_key": get_passwords("okx_api_key"),
            "api_secret_key": get_passwords("okx_api_secret_key"), "passphrase": get_passwords("okx_passphrase")}
    marketDataAPI = MarketData.MarketAPI(**api_info, debug = False)
    publicDataAPI = PublicData.PublicAPI(**api_info, debug = False)
    instrument_ID = f"{crypto_name}-USDT-SWAP"
    instrument_data = publicDataAPI.get_instruments(instType="SWAP")["data"]
    instrument_list = [x["instId"] for x in instrument_data if x["settleCcy"] == "USDT"]
    if instrument_ID not in instrument_list:
        return "找不到对应的币种"
    before_time = int(round(time.time() * 1000)) - 3600000 * 24
    result = marketDataAPI.get_candlesticks(instId = instrument_ID, bar="15m", before = before_time)["data"][::-1]
    times = [datetime.datetime.fromtimestamp(int(x[0])/1000) for x in result]
    open_price = [float(x[1]) for x in result]
    highest_price = [float(x[2]) for x in result]
    lowest_price = [float(x[3]) for x in result]
    close_price = [float(x[4]) for x in result]
    volume = [float(x[7]) for x in result]
    df = pd.DataFrame({"Open": open_price, "High": highest_price, "Low": lowest_price, "Close": close_price, "Volume": volume}
                      , index = pd.DatetimeIndex(times))
    
    binance_dark = {
        "base_mpl_style": "dark_background",
        "marketcolors": {
            "candle": {"up": "#3dc985", "down": "#ef4f60"},  
            "edge": {"up": "#3dc985", "down": "#ef4f60"},  
            "wick": {"up": "#3dc985", "down": "#ef4f60"},  
            "ohlc": {"up": "green", "down": "red"},
            "volume": {"up": "#247252", "down": "#82333f"},  
            "vcedge": {"up": "green", "down": "red"},  
            "vcdopcod": False,
            "alpha": 1,
        },
        "mavcolors": ("#ad7739", "#a63ab2", "#62b8ba"),
        "facecolor": "#1b1f24",
        "gridcolor": "#2c2e31",
        "gridstyle": "--",
        "y_on_right": True,
        "rc": {
            "axes.grid": True,
            "axes.grid.axis": "y",
            "axes.edgecolor": "#474d56",
            "axes.titlecolor": "red",
            "figure.facecolor": "#161a1e",
            "figure.titlesize": "x-large",
            "figure.titleweight": "semibold",
        },
        "base_mpf_style": "binance-dark",
    }
    mpf.plot(df, type="candle", volume = True, style = binance_dark, title = f"{instrument_ID} 15m Kline"
             , figratio = (16, 8), panel_ratios=(4, 1), savefig = "D:/Bi_Gu-bot/Bi_Gu-bot/src/plugins/crypto/mpfplot.png")
    return MessageSegment.image("file:///" + "D:/Bi_Gu-bot/Bi_Gu-bot/src/plugins/crypto/mpfplot.png")

