import requests
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
def get_setu(setu_tags: list[str] = None) -> Message:
    if setu_tags is not None:
        print(setu_tags)
        params = {"tags": setu_tags}
        url = "https://setu.yuban10703.xyz/setu"
        response = requests.get(url, params = params)
    else:
        url = "https://setu.yuban10703.xyz/setu"
        response = requests.get(url)
    img_url = response.json()["data"][0]["urls"]["original"]
    img_details = str({key: response.json()["data"][0][key] for key in ["artwork", "author", "tags"]})
    print(img_details)
    img_headers = {
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'Referer': 'https://www.pixiv.net/',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
    }

    img_response = requests.get(img_url, headers=img_headers)
    with open("./src/plugins/setu/setu.png", "wb") as f:
        f.write(img_response.content)
    return Message([MessageSegment.image("file:///" + "./src/plugins/setu/setu.png"),MessageSegment.text(img_details)])

