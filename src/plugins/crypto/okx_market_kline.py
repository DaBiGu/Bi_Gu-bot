from nonebot.adapters.onebot.v11.message import MessageSegment
import okx.MarketData as MarketData
import okx.PublicData as PublicData
import datetime, time
import pandas as pd
import mplfinance as mpf
from passwords import get_passwords
from utils.utils import get_copyright_str, get_output_path

def get_crypto_kline(crypto_name: str, time_interval: str = "15m") -> MessageSegment:
    api_info = {"flag": "0", "api_key": get_passwords("okx_api_key"),
            "api_secret_key": get_passwords("okx_api_secret_key"), "passphrase": get_passwords("okx_passphrase")}
    time_interval_repl = {"15m": "15m", "1h": "1H", "4h": "4H", "1D": "1Dutc", "3D": "3Dutc", "1W": "1Wutc", "1d": "1Dutc", "3d": "3Dutc", "1w": "1Wutc"}
    _time_interval = time_interval_repl[time_interval]
    time_interval_dict = {"15m": 900, "1H": 3600, "4H": 14400, "1Dutc": 86400, "3Dutc": 259200, "1Wutc": 604800}
    marketDataAPI = MarketData.MarketAPI(**api_info, debug = False)
    publicDataAPI = PublicData.PublicAPI(**api_info, debug = False)
    instrument_ID = f"{crypto_name}-USDT-SWAP"
    instrument_data = publicDataAPI.get_instruments(instType="SWAP")["data"]
    instrument_list = [x["instId"] for x in instrument_data if x["settleCcy"] == "USDT"]
    if instrument_ID not in instrument_list:
        return "找不到对应的币种"
    before_time = int(round(time.time() * 1000)) - 3600000 * 24 / 900 * time_interval_dict[_time_interval]
    result = marketDataAPI.get_candlesticks(instId = instrument_ID, bar = _time_interval, before = int(before_time))["data"][::-1]
    times = [datetime.datetime.fromtimestamp(int(x[0])/1000) for x in result]
    open_price = [float(x[1]) for x in result]
    highest_price = [float(x[2]) for x in result]
    lowest_price = [float(x[3]) for x in result]
    close_price = [float(x[4]) for x in result]
    volume = [float(x[7]) for x in result]
    df = pd.DataFrame({"Open": open_price, "High": highest_price, "Low": lowest_price, "Close": close_price, "Volume": volume}
                      , index = pd.DatetimeIndex(times))
    df["20ma"] = df["Close"].rolling(window = 20).mean()
    df["upper_band"] = df["20ma"] + 2 * df["Close"].rolling(window = 20).std()
    df["lower_band"] = df["20ma"] - 2 * df["Close"].rolling(window = 20).std()
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
    bollinger_bands = [mpf.make_addplot(df["20ma"], color = "#f52fe4", width = 1), 
                       mpf.make_addplot(df["upper_band"], color = "#f0b30c", width = 1),
                       mpf.make_addplot(df["lower_band"], color = "#872ff5", width = 1)]
    fig, axlist = mpf.plot(df, type="candle", volume = True, style = binance_dark, title = f"{instrument_ID} {time_interval} Kline", 
                    figratio = (20, 12), panel_ratios=(4, 1), addplot = bollinger_bands, returnfig = True, block = False)
    fig.text(0.8, 0.92, get_copyright_str(), ha='center', fontsize = 10, color = "white")
    output_path = get_output_path("crypto_kline")
    fig.savefig(output_path)
    return MessageSegment.image("file:///" + output_path)