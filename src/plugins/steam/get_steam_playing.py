import requests
from passwords import get_passwords

def get_steam_playing(steam_id: str) -> tuple[str | None, str | None]:
    headers = {
    'authority': 'api.steampowered.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en,zh-CN;q=0.9,zh;q=0.8,bg;q=0.7,zh-TW;q=0.6',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    params = {
    'key': get_passwords("steam_api_key"),
    'steamids': steam_id,
    }

    response = requests.get('https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/', params=params, headers=headers)
    username, isplaying = None, None
    data = response.json()
    if data["response"]["players"]:
        username = data["response"]["players"][0]["personaname"]
        if "gameextrainfo" in data["response"]["players"][0]:
            isplaying = data["response"]["players"][0]["gameextrainfo"]
    return [username, isplaying]