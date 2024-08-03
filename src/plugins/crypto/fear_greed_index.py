import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
from matplotlib.colors import LinearSegmentedColormap
from nonebot.adapters.onebot.v11.message import MessageSegment
import requests, datetime, os

def get_market_fear_greed_index():
    radius = 0.4
    width = 0.1
    cmap = LinearSegmentedColormap.from_list("_", ['green', 'yellow', 'red'])
    url = "https://api.alternative.me/fng/"
    response = requests.get(url)
    data = response.json()
    index = data['data'][0]['value']
    _type = data['data'][0]['value_classification']
    value = int(index)
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'aspect': 'equal'})
    fig.patch.set_facecolor('#222222')
    ax.set_facecolor('#222222')
    num_colors = 100 
    for i in range(num_colors):
        color = cmap(i / num_colors)
        start_angle = i * (180 / num_colors)
        end_angle = start_angle + (180 / num_colors)
        ax.add_patch(Wedge((0.5, 0.5), radius + width, start_angle, end_angle, width=width, color=color))
    angle = 180 - value * 1.8 
    p_length = (radius + width / 2 + 0.05) / 8  
    p_width = 0.03 / 8 

    x_bias = np.cos(np.radians(angle)) * 0.3 + 0.5
    y_bias = np.sin(np.radians(angle)) * 0.3 + 0.5

    pointer = plt.Polygon([(p_length * np.cos(np.radians(angle)) + x_bias, p_length * np.sin(np.radians(angle)) + y_bias), 
                           ((p_length - p_width) * np.cos(np.radians(angle - 90)) + x_bias, (p_length - p_width) * np.sin(np.radians(angle - 90)) + y_bias), 
                           ((p_length - p_width) * np.cos(np.radians(angle + 90)) + x_bias, (p_length - p_width) * np.sin(np.radians(angle + 90)) + y_bias)], 
                           closed=True, color='#D3D3D3')
    ax.add_patch(pointer)
    index_color = '#FF474C' if value < 20 else "#FFA500" if value < 40 else "gray" if value < 60 else "#9ACD32" if value < 80 else "green"
    ax.text(0.5, 0.5, f'{value}', ha='center', va='center', fontsize=48, fontweight='bold', color='white')
    ax.text(0.5, 0.3, f'{_type}', ha='center', va='center', fontsize=48, fontweight='bold', color=index_color)
    ax.text(0.59, 0.08, "Crypto Market Fear & Greed Index", ha='center', fontsize = 18, color = "white", fontweight='bold')
    ax.text(0.55, 0.02, "\u00A9" + f" Generated by Bi_Gu-bot at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ha='center', fontsize = 15, color = "white")
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    fig.savefig(os.getcwd() + "/src/data/crypto/index.png")
    return MessageSegment.image("file:///" + os.getcwd() + "/src/data/crypto/index.png")