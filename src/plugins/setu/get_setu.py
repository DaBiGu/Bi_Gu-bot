import requests, os, datetime
from nonebot.adapters.onebot.v11.message import Message, MessageSegment

def get_setu(setu_tags: list[str] = None) -> Message:
    headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en,zh-CN;q=0.9,zh;q=0.8,bg;q=0.7,zh-TW;q=0.6',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    }
    if setu_tags is not None:
        params = {"tags": setu_tags}
        url = "https://setu.yuban10703.xyz/setu"
        response = requests.get(url, params = params, headers=headers)
    else:
        url = "https://setu.yuban10703.xyz/setu"
        response = requests.get(url, headers=headers)
    if "data" not in response.json():
        return MessageSegment.text(f"没有找到指定tag{setu_tags}的色图")
    img_url = response.json()["data"][0]["urls"]["original"]
    img_details = str({key: response.json()["data"][0][key] for key in ["artwork", "author", "tags"]})
    img_headers = {
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'Referer': 'https://www.pixiv.net/',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
    }

    img_response = requests.get(img_url, headers=img_headers)
    output_path = os.getcwd() + f"/src/data/setu/setu_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    with open(output_path, "wb") as f: f.write(img_response.content)
    return Message([MessageSegment.image("file:///" + os.getcwd() + output_path), MessageSegment.text(img_details)])

