import time, re, csv, datetime
from typing import List
import numpy as np
import matplotlib.pyplot as plt
from nonebot.adapters.onebot.v11.message import MessageSegment
from utils.utils import get_output_path, get_IO_path, second_to_hms

def get_last_status(data: List[List[str]]) -> str | None:
    return data[-1][1] if data else None

def get_daily_sleep_duration(user_id: str) -> MessageSegment:
    csv_path = get_IO_path(f"sleep_{user_id}", "csv")
    with open(csv_path, mode = "r", encoding = "utf-8") as file:
        data = list(csv.reader(file))
    today = datetime.datetime.strptime(datetime.datetime.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
    start_of_week = today - datetime.timedelta(days = today.weekday())
    start_of_each_day = [datetime.datetime.timestamp(start_of_week + datetime.timedelta(days = i)) for i in range(8)]
    sleep_durations_day = []
    sorted_data = sorted(data, key = lambda x: float(x[0]))
    for i in range(len(start_of_each_day) - 1):
        start_of_day, end_of_day = start_of_each_day[i], start_of_each_day[i+1] - 1
        start_index, stop_index = None, None
        for j in range(len(sorted_data)):
            if float(sorted_data[j][0]) >= start_of_day:
                start_index = j
                break
        for j in range(len(sorted_data)-1, 0, -1):
            if float(sorted_data[j][0]) < end_of_day:
                stop_index = j
                break
        _data = []
        if (start_index is not None) and (stop_index is not None):
            if start_index > stop_index: _data = [0, 0]
            else:
                if sorted_data[start_index][1] == "Awake": _data.append(float(sorted_data[start_index-1][0]))
                _data += [float(x[0]) for x in sorted_data[start_index:stop_index]]
                if sorted_data[stop_index][1] == "Awake": _data.append(float(sorted_data[stop_index][0]))
        else: _data = [0, 0]
        sleep_durations_day.append(sum([float(_data[i+1]) - float(_data[i]) for i in range(0, len(_data), 2)]))
    average_sleep_duration = np.mean([x for x in sleep_durations_day if x != 0])
    average_sleep_duration_str = re.sub(r"\d+s", "", second_to_hms(average_sleep_duration, eng=True))
    plt.style.use('default')
    plt.figure(figsize = (10, 5))
    sleep_durations_name = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    bars = plt.bar(sleep_durations_name, [x/3600 for x in sleep_durations_day], width = 0.5)
    for bar, value in zip(bars, sleep_durations_day):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), re.sub(r"\d+s", "", second_to_hms(value, eng=True)), ha = "center", va = "bottom")
    plt.text(0, average_sleep_duration/3600, f"Average: {average_sleep_duration_str}", ha = "center", va = "bottom", color = "r")
    plt.axhline(y = average_sleep_duration/3600, color = "r", linestyle = "--", label = "Average")
    plt.title(f"{user_id}'s daily sleep duration of the week", fontweight = "bold")
    plt.ylabel("Sleep duration (h)")
    plt.legend()
    output_path = get_output_path(f"sleep_{user_id}")
    plt.savefig(output_path, dpi = 300, bbox_inches = "tight")
    return MessageSegment.image("file:///" + output_path)

def record_sleep(user_id: str, hour: int = None, minute: int = None) -> datetime.datetime | int:
    sleep_time = -1
    csv_path = get_IO_path(f"sleep_{user_id}", "csv")
    with open(csv_path, mode = "a", encoding = "utf-8") as _: pass
    with open(csv_path, mode = "r", encoding = "utf-8") as file:
        data = list(csv.reader(file))
    user_last_status = get_last_status(data)
    to_write = None
    if user_last_status == "Awake" or user_last_status == None:
        last_awake_time = data[-1][0] if data else 0
        if (hour is not None) and (minute is not None):
            sleep_time = find_closest_time(hour, minute)
            if datetime.datetime.timestamp(sleep_time) < float(last_awake_time): sleep_time = -2
            to_write = [datetime.datetime.timestamp(sleep_time), "Sleep"]
        else:
            to_write = [time.time(), "Sleep"]
            sleep_time = datetime.datetime.now()
    if to_write:
        with open(csv_path, mode = "a", newline = '') as file:
            writer = csv.writer(file)
            writer.writerow(to_write)
    return sleep_time

def record_awake(user_id: str, hour: int = None, minute: int = None) -> float | int:
    last_sleep_time = -2
    csv_path = get_IO_path(f"sleep_{user_id}", "csv")
    with open(csv_path, mode = "a", encoding = "utf-8") as _: pass
    with open(csv_path, mode = "r", encoding = "utf-8") as file:
        data = list(csv.reader(file))
    user_last_status = get_last_status(data)
    if not user_last_status: return -2
    to_write, awake_time = None, None
    if user_last_status == "Sleep":
        last_sleep_time = data[-1][0]
        if (hour is not None) and (minute is not None):
            awake_time = datetime.datetime.timestamp(find_closest_time(hour, minute))
            if awake_time < float(last_sleep_time): return -3
            else:
                to_write = [awake_time, "Awake"]
        else:
            to_write = [time.time(), "Awake"]  
    else: return -1
    if to_write:
        with open(csv_path, mode = "a", newline = '') as file:
            writer = csv.writer(file)
            writer.writerow(to_write) 
    if awake_time:
        return awake_time - float(last_sleep_time)
    else:
        return time.time() - float(last_sleep_time)

def find_closest_time(hour: int, minute: int) -> datetime.datetime:
    target_time = datetime.time(hour, minute)
    current_time = datetime.datetime.now()
    yesterday_time = datetime.datetime.combine(datetime.datetime.today() - datetime.timedelta(days = 1), target_time)
    today_time = datetime.datetime.combine(datetime.datetime.today(), target_time)
    return yesterday_time if abs(current_time - yesterday_time) < abs(current_time - today_time) else today_time
