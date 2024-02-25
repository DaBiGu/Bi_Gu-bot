import csv, time
from datetime import datetime

def write_csv(user_id):
    csv_file = "D:/Bi_Gu-bot/Bi_Gu-bot/src/data/sleep/user_data.csv"
    
    with open(csv_file, mode = "r", encoding = "utf-8") as file:
        data = list(csv.reader(file))
     
    current_time = datetime.now()
    time_write = time.time()

    has_recorded = False

    for row in data:
        if row:
            if row[0] == user_id: 
                has_recorded = True
                if row[2] == "Sleep": return None
                elif row[2] == "Awake":
                    row[1] = time_write
                    row[2] = "Sleep"
                break

    if not has_recorded:
        data.append([user_id, time_write, "Sleep"])
    
    with open(csv_file, mode = "w", newline = '') as file:
        writer = csv.writer(file)
        writer.writerows(data)

    return current_time

def read_csv(user_id):
    awake_time = -2
    csv_file = "D:/Bi_Gu-bot/Bi_Gu-bot/src/data/sleep/user_data.csv"
    
    with open(csv_file, mode = "r", encoding = "utf-8") as file:
        data = list(csv.reader(file))
    
    for row in data:
        if row:
            if row[0] == user_id:
                if row[2] == "Sleep":
                    row[2] = "Awake"
                    awake_time = row[1]
                elif row[2] == "Awake": awake_time = -1

    with open(csv_file, mode = "w", newline = '') as file:
        writer = csv.writer(file)
        writer.writerows(data)

    return awake_time
    



