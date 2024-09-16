import datetime, json, os, requests
from typing import List, Dict
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from nonebot.adapters.onebot.v11.message import MessageSegment
from utils.utils import get_copyright_str, get_output_path, get_IO_path
from utils.fonts import get_font_path
from matplotlib import cm
from matplotlib.colors import Normalize
from pathlib import Path

def mix_color(color, white=(1, 1, 1), ratio=0.5):
    return [(1 - ratio) * c + ratio * w for c, w in zip(color, white)]

def get_datelist(count: int) -> List[str]:
    return [(datetime.datetime.now() - datetime.timedelta(days = i)).strftime("%Y-%m-%d") for i in range(count)]

def get_chatcount(group_id: str, count: int) -> Dict[str, int] | None:
    with open(get_IO_path("chatcount", "json"), "r") as f:
        raw_chatcount = json.load(f)
    datelist = get_datelist(count)
    chatcount = {}
    for date in datelist:
        if group_id not in raw_chatcount: return None
        if date not in raw_chatcount[group_id]: continue
        for user in raw_chatcount[group_id][date]:
            if user not in chatcount: chatcount[user] = 0
            chatcount[user] += raw_chatcount[group_id][date][user]
    sorted_chatcount = dict(sorted(chatcount.items(), key = lambda item: item[1], reverse = True))
    return dict(list(sorted_chatcount.items())[:10]) if len(sorted_chatcount) > 10 else sorted_chatcount

def draw_chatcount_bargraph(data: Dict[str, int], time_range: int, nicknames: Dict[int, str], kawaii: bool = False) -> MessageSegment:
    font_path = Path(get_font_path("yahei-consolas")) if not kawaii else Path(get_font_path("xiaolai"))
    _data = {}
    time_range_dict = {1: "今日", 7: "本周", 30: "本月"}
    for key, value in data.items():
        _data[nicknames[int(key)]] = value
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
        avatar = Image.open(avatars[bars.index(bar)])
        avatar_width = (xlim[1]-xlim[0]) * fig_height
        avatar_height = (ylim[1]-ylim[0]) * fig_width

        scale = bar.get_width() / avatar_width
        avatar_width *= scale
        avatar_height *= scale
        
        x = bar.get_x() + bar.get_width() / 2 - avatar_width / 2
        y = bar.get_height()
        ax.imshow(avatar, extent=(x, x + avatar_width, y, y + avatar_height), aspect='auto')
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2, f'{bar.get_height()}', ha='center', va='center', font = font_path)

    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xticklabels(_nicknames, font = font_path, fontsize = 12)
    fig.text(0.75, -0.1, get_copyright_str(), ha='center', font = font_path, fontsize = 12)
    plt.ylabel('b话量', font = font_path)
    plt.title(f'你群{time_range_dict[time_range]}top10 b话王', font = font_path, fontsize = 16, loc='center', x=0.5, y=1.05)
    fig.text(0.75, 0.9, f"数据范围: {get_datelist(time_range)[-1]} 00:00 至{get_datelist(time_range)[0]} 23:59", ha='center', font = font_path, fontsize = 12)
    plt.xticks(rotation=45)
    output_path = get_output_path("chatcount")
    plt.savefig(output_path, dpi = 300, bbox_inches = "tight")
    return MessageSegment.image("file:///" + output_path)
