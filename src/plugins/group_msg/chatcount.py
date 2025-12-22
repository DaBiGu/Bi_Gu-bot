import json
from typing import Dict
from utils.utils import get_IO_path, get_datelist

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