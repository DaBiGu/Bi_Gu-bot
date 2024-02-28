import csv
import time
from datetime import datetime, timedelta
from typing import List, Union

def get_last_status(data: List[List[str]]) -> str | None:
    return data[-1][1] if data else None

def get_average_sleep_duration(user_id: str) -> float:
    csv_path = f"D:/Bi_Gu-bot/Bi_Gu-bot/src/data/sleep/user_data/{user_id}.csv"
    with open(csv_path, mode = "r", encoding = "utf-8") as file:
        data = list(csv.reader(file))
    today = datetime.strptime(datetime.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
    start_of_week = today - timedelta(days = today.weekday())
    end_of_week = start_of_week + timedelta(days = 6)
    start_of_week, end_of_week = datetime.timestamp(start_of_week), datetime.timestamp(end_of_week)
    sleep_durations = []
    start_index, stop_index = -1, -1
    for i in range(len(data)):
        if float(data[i][0]) >= start_of_week:
            start_index = i
            break
    for i in range(len(data)-1, 0, -1):
        if float(data[i][0]) < end_of_week:
            stop_index = i
            break
    for i in range(0,len(data[start_index:stop_index]), 2):
        sleep_durations.append(float(data[i+1][0]) - float(data[i][0]))
    return sum(sleep_durations) / len(sleep_durations)

def record_sleep(user_id: str) -> datetime | None:
    sleep_time = None
    csv_path = f"D:/Bi_Gu-bot/Bi_Gu-bot/src/data/sleep/user_data/{user_id}.csv"
    with open(csv_path, mode = "a", encoding = "utf-8") as _: pass
    with open(csv_path, mode = "r", encoding = "utf-8") as file:
        data = list(csv.reader(file))
    user_last_status = get_last_status(data)
    if user_last_status == "Awake" or user_last_status == None:
        to_write = [time.time(), "Sleep"]
        sleep_time = datetime.now()

    with open(csv_path, mode = "a", newline = '') as file:
        writer = csv.writer(file)
        writer.writerow(to_write)
    return sleep_time

def record_awake(user_id: str) -> tuple[float | int, float]:
    last_sleep_time = -2
    csv_path = f"D:/Bi_Gu-bot/Bi_Gu-bot/src/data/sleep/user_data/{user_id}.csv"
    with open(csv_path, mode = "a", encoding = "utf-8") as _: pass
    with open(csv_path, mode = "r", encoding = "utf-8") as file:
        data = list(csv.reader(file))
    user_last_status = get_last_status(data)
    if not user_last_status: return -1
    if user_last_status == "Sleep":
        last_sleep_time = data[-1][0]
        to_write = [time.time(), "Awake"]  
    with open(csv_path, mode = "a", newline = '') as file:
        writer = csv.writer(file)
        writer.writerow(to_write) 
    average_sleep_duration = get_average_sleep_duration(user_id)
    return [last_sleep_time, average_sleep_duration]