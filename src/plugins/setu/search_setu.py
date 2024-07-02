from saucenao_api import SauceNao
from typing import List, Dict

import re

from sys import path
path.append("D:/Bi_Gu-bot/passwords")
from passwords import get_passwords

def search_setu(setu_url: str, search_num: int = 1) -> List[Dict[str, str]]:
    saucenao = SauceNao(get_passwords("saucenao_api"))
    #md5_value = extract_MD5(setu_url)
    #target_url = f"https://gchat.qpic.cn/gchatpic_new/0/0-0-{md5_value}/0?term=0"
    #results = saucenao.from_url(target_url)
    results = saucenao.from_url(setu_url)
    results_dict_list = []
    for i in range(max(search_num, len(results))):
        results_dict = {}
        if results[i].title: results_dict["title"] = results[i].title
        if results[i].similarity: results_dict["similarity"] = results[i].similarity
        if results[i].author: results_dict["author"] = results[i].author
        if results[i].urls: results_dict["url"] = results[i].urls[0]
        if "source" in results[i].raw["data"]: results_dict["url"] = results[i].raw["data"]["source"]
        results_dict_list.append(results_dict)
    return results_dict_list

def extract_MD5(url: str) -> str:
    md5_pattern = re.compile(r"[a-fA-F0-9]{32}")
    md5_values = md5_pattern.findall(url)
    return md5_values[0]