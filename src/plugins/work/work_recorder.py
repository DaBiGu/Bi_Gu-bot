import csv, time
from datetime import datetime

def get_current_work_status(data, user_id):
    for row in data[::-1]:
        if row:
            if row[0] == user_id:
                return row
    return None

def start_work(user_id, work_id):
    csv_path = f"D:/Bi_Gu-bot/Bi_Gu-bot/src/data/work/user_data/{user_id}.csv"
    # create separate csv file for user (if not exist)
    with open(csv_path, mode = "a", encoding = "utf-8") as _: pass
    # read csv file into data
    with open(csv_path, mode = "r", encoding = "utf-8") as file:
        data = list(csv.reader(file))
    # get current time
    current_time = datetime.now()
    time_write = time.time()
    to_write = None
    print(data)
    current_work_status = get_current_work_status(data, user_id)
    print(current_work_status)
    if current_work_status:
        if current_work_status[1] == "WORK": return -1
        elif current_work_status[1] == "STOP":
            to_write = [user_id, "WORK", time_write, work_id]
    else:
        to_write = [user_id, "WORK", time_write, work_id]

    with open(csv_path, mode = "a", newline = '', encoding = "utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(to_write)

    return current_time
    
def stop_work(user_id):
    result = []
    csv_path = f"D:/Bi_Gu-bot/Bi_Gu-bot/src/data/work/user_data/{user_id}.csv"
    to_write = None
    with open(csv_path, mode = "a", encoding = "utf-8") as _: pass
    with open(csv_path, mode = "r", encoding = "utf-8") as file:
        data = list(csv.reader(file))
    current_work_status = get_current_work_status(data, user_id)
    if current_work_status:
        if current_work_status[1] == "STOP": result = [-1, None]
        elif current_work_status[1] == "WORK":
            to_write = [user_id, "STOP", time.time(), current_work_status[3]]
            result = [current_work_status[2], current_work_status[3]]
    else: result = [-1, None]
    with open(csv_path, mode = "a", newline = '', encoding = "utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(to_write)
    return result