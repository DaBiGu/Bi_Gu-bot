import csv
import time
from datetime import datetime, timedelta
from typing import List
from typing import List, Union

def get_last_mstbt(data: List[List[str]], user_id: str) -> str | None:
    for row in data[::-1]:
        if row:
            if row[0] == user_id:
                return row[1]
    return None

def get_mstbt_times(data: List[List[str]], user_id: str) -> int:
    count = 0
    for row in data:
        if row:
            if row[0] == user_id:
                count += 1
    return count + 1

def get_mstbt_times_week(data: List[List[str]], user_id: str) -> int:
    today = datetime.strptime(datetime.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
    start_of_week = today - timedelta(days = today.weekday())
    end_of_week = start_of_week + timedelta(days = 6)
    start_of_week, end_of_week = datetime.timestamp(start_of_week), datetime.timestamp(end_of_week)
    count = 0
    for row in data:
        if row:
            if row[0] == user_id and float(row[1]) >= start_of_week and float(row[1]) <= end_of_week:
                count += 1
    return count + 1

def mstbt_record(user_id: str) -> tuple[str | None, int, int]:
    csv_path = f"D:/Bi_Gu-bot/Bi_Gu-bot/src/data/mstbt/mstbt.csv"
    with open(csv_path, mode = "a", encoding = "utf-8") as _: pass
    with open(csv_path, mode = "r", encoding = "utf-8") as file:
        data = list(csv.reader(file))
    last_mstbt = get_last_mstbt(data, user_id)
    mstbt_times = get_mstbt_times(data, user_id)
    mstbt_times_week = get_mstbt_times_week(data, user_id)
    current_time = time.time()
    new_record = [user_id, current_time]
    with open(csv_path, mode = "a", newline = '', encoding = "utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(new_record)
    return [last_mstbt, mstbt_times, mstbt_times_week]
