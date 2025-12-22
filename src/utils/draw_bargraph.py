from typing import List, Dict
import matplotlib.pyplot as plt
import requests, datetime
from PIL import Image
from nonebot.adapters.onebot.v11.message import MessageSegment
from utils.utils import get_copyright_str, get_output_path, get_IO_path
from utils.fonts import get_font_path
from matplotlib import cm
from matplotlib.colors import Normalize
from matplotlib.font_manager import FontProperties
from .utils import get_datelist

def mix_color(color, white=(1, 1, 1), ratio=0.5):
    return [(1 - ratio) * c + ratio * w for c, w in zip(color, white)]

def get_fontprop(path: str, size: int = None) -> FontProperties:
    return FontProperties(fname = path, size = size) if size else FontProperties(fname = path)

async def draw_bargraph(data: Dict[str, int], title: str, ylabel: str, nicknames: Dict[int, str], time_range: str = None, kawaii: bool = True) -> MessageSegment:
    support_time_range = time_range is not None
    font_path = get_font_path("noto-sans-regular") if not kawaii else get_font_path("xiaolai")
    _data = {}
    time_range_dict = {"today": "今日", "yesterday": "昨日", "week": "本周", "month": "本月", "year": "本年", "last week": "上周", "last month": "上月"}
    if support_time_range: title = title.replace("{time_range}", time_range_dict.get(time_range, time_range))
    for key, value in data.items():
        if int(key) in nicknames: _data[nicknames[int(key)]] = value
        else: _data[key] = value

    user_ids = list(data.keys())
    _nicknames = list(_data.keys())
    counts = list(_data.values())
    avatars = []
    for user in user_ids:
        temp_path = get_output_path(f"user_avatar_{user}", temp = True)
        with open(temp_path, "wb") as f: f.write(requests.get(f"https://q1.qlogo.cn/g?b=qq&nk={user}&s=100").content)
        avatars.append(temp_path)

    plt.style.use('default')
    norm = Normalize(vmin = min(counts), vmax = max(counts))
    colors = cm.rainbow(norm(counts))
    colors = [mix_color(color[:3], ratio = 0.5) + [1.0] for color in colors] if kawaii else "skyblue"
    if kawaii: plt.xkcd()
    fig = plt.figure(figsize=(12, 6))
    ax = plt.gca()
    bars = ax.bar(_nicknames, counts, color = colors)
    ax.set_ylim(0, int(max(counts) * 1.2))
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    fig_width, fig_height = fig.get_size_inches()
    
    for bar in bars:
        avatar = Image.open(avatars[bars.index(bar)]).convert("RGB")
        avatar_width = (xlim[1]-xlim[0]) * fig_height
        avatar_height = (ylim[1]-ylim[0]) * fig_width

        scale = bar.get_width() / avatar_width
        avatar_width *= scale
        avatar_height *= scale
        
        x = bar.get_x() + bar.get_width() / 2 - avatar_width / 2
        y = bar.get_height()
        ax.imshow(avatar, extent=(x, x + avatar_width, y, y + avatar_height), aspect='auto')
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2, f'{bar.get_height()}', ha='center', va='center', fontproperties = get_fontprop(font_path))

    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xticklabels(_nicknames, fontproperties = get_fontprop(font_path, 12))
    ax.set_yticklabels([int(y) for y in ax.get_yticks()], fontproperties = get_fontprop(font_path, 12))
    fig.text(0.75, -0.1, get_copyright_str(), ha='center', fontproperties = get_fontprop(font_path, 12))
    plt.ylabel(ylabel, fontproperties = get_fontprop(font_path, 12))
    plt.title(title, fontproperties = get_fontprop(font_path, 16), loc='center', x=0.5, y=1.05)
    if support_time_range:
        now = "23:59" if time_range in ["yesterday", "last week", "last month"] else datetime.datetime.now().strftime("%H:%M")
        fig.text(0.75, 0.9, f"数据范围: {get_datelist(time_range)[0]} 00:00 至{get_datelist(time_range)[-1]} {now}", ha='center', fontproperties = get_fontprop(font_path, 12))
    plt.xticks(rotation=45)
    output_path = get_output_path("bargraph")
    plt.savefig(output_path, dpi = 300, bbox_inches = "tight")
    return MessageSegment.image("file:///" + output_path)