import requests, time
from matplotlib import pyplot as plt
from matplotlib.patches import Patch
from nonebot.adapters.onebot.v11.message import MessageSegment
from typing import List, Dict
from utils.utils import get_copyright_str, get_output_path
import numpy as np

def forward(y):
    return 150 / (1 + np.exp(-y / 200))

def reverse(y):
    return -200 * np.log(150 / y - 1)

def get_user_data(username: str) -> MessageSegment:
    raw_user_data, rank_scores, pt_count = get_raw_user_data(username)
    color_map = {0: 'blue', 1: 'green', 2: 'red', 3: 'yellow'}
    scores = [game["score"] for game in raw_user_data]
    ranks = [game["rank"] for game in raw_user_data]
    rank_counts = [ranks.count(i) / len(ranks) * 100 for i in range(1, 5)]
    index = [i+1 for i in range(len(scores))]
    plt.style.use('default')
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
    fig, ax = plt.subplots(figsize=(20, 10))
    ax.plot(index, scores, color = 'black', alpha = 0.8)
    for i in range(len(scores)):
        ax.scatter(index[i], scores[i], marker = 'o', facecolor = color_map[ranks[i] - 1], edgecolor = 'black', s = 100)
    min_score = min([min(rank_score) for rank_score in rank_scores])
    max_score = max([max(rank_score) for rank_score in rank_scores])
    plt.title(f"{username}近30局对局统计", fontsize = 20)
    fig.text(0.8, 0.03, get_copyright_str(), ha='center', fontsize = 15)
    ax.set_ylim(min_score - 10000, max_score + 10000)
    ax.set_yticks(np.arange(int(min_score // 10000) * 10000, int(max_score // 10000 + 2) * 10000, 10000))
    legend = {"一位:" + "{:.2f}".format(rank_counts[0]) + "%": "blue", 
              "二位:" + "{:.2f}".format(rank_counts[1]) + "%": "green", 
              "三位:" + "{:.2f}".format(rank_counts[2]) + "%": "red", 
              "四位:" + "{:.2f}".format(rank_counts[3]) + "%": "yellow"}
    legend_elements = [Patch(facecolor=color, edgecolor='black', label=label) for label, color in legend.items()]
    legend_elements.append(plt.Line2D([0], [0], color = 'gray', alpha = 0.8, linestyle = '--', label='pt变化'))
    _ax = ax.twinx()
    pt_plus, pt_minus, pt_change = [], [], [0]
    for i in range(len(pt_count)):
        delta_pt = pt_count[i]
        pt_change.append(pt_change[i] + delta_pt)
        pt_plus += [delta_pt] if delta_pt > 0 else [0]
        pt_minus += [0] if delta_pt > 0 else [delta_pt]
    pt_change = pt_change[1:]
    _ax.bar(index, pt_plus, color = 'green', alpha = 0.2, width = 0.5)
    _ax.bar(index, pt_minus, color = 'red', alpha = 0.2, width = 0.5)
    _ax.plot(index, pt_change, color = 'gray', alpha = 0.8, linestyle = '--')
    _ax.set_ylim(-1000, 1000)
    _ax.set_yscale("function", functions=(forward, reverse))
    plt.legend(handles=legend_elements, loc = "upper left", fontsize = 15)
    vs = []
    for i in range(1, len(scores)-1):
        v1 = np.array([index[i]-index[i-1], scores[i]-scores[i-1]], dtype = np.float64)
        v2 = np.array([index[i]-index[i+1], scores[i]-scores[i+1]], dtype = np.float64)
        v1 /= np.linalg.norm(v1)
        v2 /= np.linalg.norm(v2)
        vs.append(v1 + v2)
    vs = [np.array([index[0]-index[1], scores[0]-scores[1]], dtype = np.float64), *vs, np.array([index[-1]-index[-2], scores[-1]-scores[-2]], dtype = np.float64)]
    vs = [v / np.linalg.norm(v) for v in vs]
    _vs = [np.array([v[0] * 0.65, v[1] * 3000]) for v in vs]
    for i in range(len(scores)):
        ax.text(index[i] + _vs[i][0], scores[i] + _vs[i][1], scores[i], fontsize = 12, ha = 'center', va = 'center')
    output_path = get_output_path(f"mahjongsoul_{username}")
    plt.savefig(output_path, dpi = 300, bbox_inches = "tight")
    return MessageSegment.image("file:///" + output_path)

def get_raw_user_data(username: str) -> tuple[List[Dict], List[List[int]], List[int]]:
    url = f"https://5-data.amae-koromo.com/api/v2/pl4/search_player/{username}?limit=20&tag=all"
    user_id = requests.get(url).json()[0]["id"]
    _url = f"https://5-data.amae-koromo.com/api/v2/pl4/player_records/{user_id}/{int(time.time() * 1000)}/1262304000000?limit=141&mode=16,12,9,8&descending=true"
    user_data = requests.get(_url).json()
    res, rank_scores, pt_count = [], [], []
    for game in user_data:
        sorted_players = sorted(game["players"], key = lambda x: x["score"], reverse = True)
        for player_info in sorted_players:
            if player_info["accountId"] == user_id:
                player_info["rank"] = sorted_players.index(player_info) + 1
                res.append(player_info)
                pt_count.append(player_info["gradingScore"])
        rank_scores.append([player["score"] for player in sorted_players])
    return res[:30][::-1], rank_scores[:30][::-1], pt_count[:30][::-1]