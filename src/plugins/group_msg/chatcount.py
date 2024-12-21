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

def get_datelist(time_range: str) -> List[str]:
    last_day = datetime.datetime.now() - datetime.timedelta(days = 1) if time_range == "yesterday" else datetime.datetime.now()
    first_day = last_day - datetime.timedelta(days = last_day.weekday()) if time_range == "week" else last_day.replace(day = 1) if time_range == "month" else \
                last_day.replace(month = 1, day = 1) if time_range == "year" else last_day
    datelist, current_day = [], first_day
    while current_day <= last_day:
        datelist.append(current_day.strftime("%Y-%m-%d"))
        current_day += datetime.timedelta(days = 1)
    return datelist

def get_chatcount(group_id: str, time_range: str) -> Dict[str, int] | None:
    with open(get_IO_path("chatcount", "json"), "r") as f:
        raw_chatcount = json.load(f)
    datelist = get_datelist(time_range)
    chatcount = {}
    for date in datelist:
        if group_id not in raw_chatcount: return None
        if date not in raw_chatcount[group_id]: continue
        for user in raw_chatcount[group_id][date]:
            if user not in chatcount: chatcount[user] = 0
            chatcount[user] += raw_chatcount[group_id][date][user]
    sorted_chatcount = dict(sorted(chatcount.items(), key = lambda item: item[1], reverse = True))
    return dict(list(sorted_chatcount.items())[:10]) if len(sorted_chatcount) > 10 else sorted_chatcount

async def draw_chatcount_bargraph(data: Dict[str, int], time_range: str, nicknames: Dict[int, str], kawaii: bool = True) -> MessageSegment:
    font_path = Path(get_font_path("noto-sans-regular")) if not kawaii else Path(get_font_path("xiaolai"))
    _data = {}
    time_range_dict = {"today": "今日", "yesterday": "昨日", "week": "本周", "month": "本月", "year": "本年"}
    for key, value in data.items():
        _data[nicknames[int(key)]] = value if int(key) in nicknames else key
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
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2, f'{bar.get_height()}', ha='center', va='center', font = font_path)

    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xticklabels(_nicknames, font = font_path, fontsize = 12)
    ax.set_yticklabels([int(y) for y in ax.get_yticks()], font = font_path, fontsize = 12)
    fig.text(0.75, -0.1, get_copyright_str(), ha='center', font = font_path, fontsize = 12)
    plt.ylabel('b话量', font = font_path)
    plt.title(f'你群{time_range_dict[time_range]}top10 b话王', font = font_path, fontsize = 16, loc='center', x=0.5, y=1.05)
    now = "23:59" if time_range == "yesterday" else datetime.datetime.now().strftime("%H:%M")
    fig.text(0.75, 0.9, f"数据范围: {get_datelist(time_range)[0]} 00:00 至{get_datelist(time_range)[-1]} {now}", ha='center', font = font_path, fontsize = 12)
    plt.xticks(rotation=45)
    output_path = get_output_path("chatcount")
    plt.savefig(output_path, dpi = 300, bbox_inches = "tight")
    return MessageSegment.image("file:///" + output_path)