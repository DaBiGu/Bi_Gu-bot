import datetime, json, os
from typing import List

def get_datelist(count: int) -> List[str]:
    return [(datetime.datetime.now() - datetime.timedelta(days = i)).strftime("%Y-%m-%d") for i in range(count)]

def get_chatcount(group_id: str, count: int) -> str:
    with open(os.getcwd() + "/src/data/group_msg/chatcount.json", "r") as f:
        raw_chatcount = json.load(f)
    datelist = get_datelist(count)
    chatcount = {}
    for date in datelist:
        if group_id not in raw_chatcount: return "本群暂无聊天记录"
        if date not in raw_chatcount[group_id]: continue
        for user in raw_chatcount[group_id][date]:
            if user not in chatcount: chatcount[user] = 0
            chatcount[user] += raw_chatcount[group_id][date][user]
    sorted_chatcount = dict(sorted(chatcount.items(), key = lambda item: item[1], reverse = True))
    return str(dict(list(sorted_chatcount.items())[:10])) if len(sorted_chatcount) > 10 else str(sorted_chatcount)