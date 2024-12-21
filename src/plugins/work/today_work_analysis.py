import matplotlib.pyplot as plt
import datetime, csv
from typing import List
from nonebot.adapters.onebot.v11.message import MessageSegment
from utils.utils import get_output_path, get_IO_path

def today_work_analysis(user_id: str) -> tuple[MessageSegment, float]:
    csv_path = get_IO_path(f"work_{user_id}", "csv")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)
    today_start = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + datetime.timedelta(days=1)
    timebounds = [float(datetime.datetime.timestamp(x)) for x in [today_start, today_end]]
    start_index, stop_index = -1, -1
    for i in range(len(data)):
        if float(data[i][2]) >= timebounds[0]:
            start_index = i
            break
    for i in range(len(data)-1, 0, -1):
        if float(data[i][2]) < timebounds[1]:
            stop_index = i
            break
    work_time_list, work_id_list = [], []
    for i in range(0,len(data[start_index:stop_index]), 2):
        work_time_list.append(float(data[i+1][2]) - float(data[i][2]))
        work_id_list.append(data[i][3])
    work_total_time = sum(work_time_list)
    work_time_list, work_id_list = merge_same_work(work_time_list, work_id_list)
    plt.figure(figsize=(10,8), facecolor='white')
    plt.style.use('default')
    plt.rcParams["font.sans-serif"] = ["SimHei"]
    plt.pie(work_time_list, labels=work_id_list, autopct='%1.2f%%', textprops={'fontsize': 30})
    output_path = get_output_path(f"work_{user_id}")
    plt.savefig(output_path)
    return [MessageSegment.image("file:///" + output_path), work_total_time]

def merge_same_work(work_time_list: List[float], work_id_list: List[str]) -> tuple[List[float], List[str]]:
    work_time_dict = {}
    for i in range(len(work_id_list)):
        if work_id_list[i] in work_time_dict:
            work_time_dict[work_id_list[i]] += work_time_list[i]
        else:
            work_time_dict[work_id_list[i]] = work_time_list[i]
    _work_time_list = list(work_time_dict.values())
    _work_id_list = list(work_time_dict.keys())
    return [_work_time_list, _work_id_list]