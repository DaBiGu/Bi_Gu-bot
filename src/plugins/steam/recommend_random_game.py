import requests, random, datetime, os
from typing import Dict, Any
from nonebot.adapters.onebot.v11 import MessageSegment

from sys import path
path.append(os.getcwd() + "/passwords")
path.append(os.getcwd() + "/src")
from passwords import get_passwords

from PIL import Image, ImageDraw, ImageFont
from utils.fonts import get_font

lookup_url = "https://api.isthereanydeal.com/games/lookup/v1"
info_url = "https://api.isthereanydeal.com/games/info/v2"
api_key = get_passwords("isthereanydeal_api_key")

def check_legal_game(appid: int) -> str | None:
    try: game_id = requests.get(lookup_url, params={"key": api_key, "appid": appid}).json()["game"]["id"]
    except KeyError: return None
    game_info = requests.get(url = info_url, params = {"key": api_key, "id": game_id}).json()
    return game_info["title"]

def get_random_game(steamid: int, appid: int = None) -> Dict[str, int]:
    games = requests.get("https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001",
                         params = {'key': get_passwords("steam_api_key"), 'steamid': steamid, 'include_played_free_games': True}).json()["response"]["games"]
    if appid:
        for game in games:
            if game["appid"] == appid: return game
    return random.choice(games)

def get_player_info(steamid: int) -> Dict[str, str]:
    url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002"
    params = {'key': get_passwords("steam_api_key"),'steamids': steamid}
    player_info = requests.get(url, params=params).json()["response"]["players"][0]
    with open(os.getcwd() + f"/src/data/steam/temp/avatar_{steamid}.png", "wb") as f:
        f.write(requests.get(player_info["avatarfull"]).content)
    _player_info = {"nickname": player_info["personaname"], "avatar": os.getcwd() + f"/src/data/steam/temp/avatar_{steamid}.png"}
    return _player_info

def get_random_game_info(steamid: int = None, appid: int = None, recommended: bool = True) -> Dict[str, Any]:
    game_steam = get_random_game(steamid, appid) if recommended else {"appid": appid}
    game_id = requests.get(lookup_url, params={"key": api_key, "appid": game_steam["appid"]}).json()["game"]["id"]
    game_info = requests.get(url = info_url, params = {"key": api_key, "id": game_id}).json()
    for review in game_info["reviews"]:
        if review["source"] == "Steam":
            _ = review["score"]
            review_count = review["count"]
            review_score = "Overwhelmingly Positive" if 95 <= _ <= 100 and review_count >= 500 \
            else "Very Positive" if 85 <= _ <= 100 and review_count >= 50 else "Positive" if 80 <= _ <= 100 \
            else "Mostly Positive" if 70 <= _ <= 79 else "Mixed" if 40 <= _ <= 69 else "Mostly Negative" if 20 <= _ <= 39 \
            else "Overwhelmingly Negative" if 0 <= _ <= 19 and review_count >= 500 else "Very Negative" if 0 <= _ <= 19 and review_count >= 50 else "Negative"
            review_score += f" ({review_count} reviews)"
    with open(os.getcwd() + f"/src/data/steam/temp/{game_info['title']}.png", "wb") as f:
        f.write(requests.get(game_info["assets"]["banner600"]).content)
    _game_info = {"name": game_info["title"], 
                  "banner_path": os.getcwd() + f"/src/data/steam/temp/{game_info['title']}.png",
                  "release_date": game_info["releaseDate"],
                  "review_score": review_score,
                  "user_tags": game_info["tags"]
    }
    if recommended:
        _game_info.update({
                  "nickname": get_player_info(steamid)["nickname"],
                  "avatar": get_player_info(steamid)["avatar"],
                  "playtime_2weeks": game_steam["playtime_2weeks"] if "playtime_2weeks" in game_steam else 0,
                  "playtime_forever": game_steam["playtime_forever"] if "playtime_forever" in game_steam else 0
        })
    return _game_info

def draw_game_card(steamid: int = None, appid: int = None, recommended: bool = True) -> MessageSegment:
    game_info = get_random_game_info(steamid, appid, recommended)
    banner = Image.open(game_info["banner_path"]).resize((1200, 688))
    
    card_width = 1600
    card_height = 2000 if recommended else 1500
    background_color = (224, 243, 250)
    card = Image.new("RGB", (card_width, card_height), background_color)
    
    draw = ImageDraw.Draw(card)
    game_name = game_info["name"]
    draw.text((50, 50), game_name, font=get_font("noto-sans", size = 80, weight = 500), fill=(0, 0, 0))
    
    release_date = f"Released: {game_info['release_date']}"
    draw.text((50, 150), release_date, font=get_font("noto-sans", size = 60, weight = 400), fill=(0, 0, 0))
    
    card.paste(banner, (100, 250))    
    review_text_color = (91, 139, 199) if "Positive" in game_info["review_score"] else (163, 76, 37) if "Negative" in game_info["review_score"] else (185, 160, 116)
    reviews_text = f"Overall user reviews:\n{game_info['review_score']}"
    draw.text((120, 960), reviews_text, font=get_font("noto-sans", size = 48, weight = 500), fill=review_text_color)
    
    tags_y = 1100
    x_offset = 100
    for tag in game_info["user_tags"]:
        bbox = draw.textbbox((0, 0), tag, font=get_font("noto-sans", size = 48, weight = 400))
        tag_width = bbox[2] - bbox[0]
        draw.text((x_offset + 10, tags_y + 5), tag, font=get_font("noto-sans", size = 48, weight = 400), fill=(0, 0, 0))
        x_offset += tag_width + 40
        if x_offset + tag_width > card_width - 100:
            x_offset = 100
            tags_y += 60

    if recommended:
        avatar = Image.open(game_info["avatar"]).resize((368, 368))
        avatar_x = 50
        avatar_y = 1500
        frame_width = 5
        draw.rectangle([avatar_x - frame_width, avatar_y - frame_width, avatar_x + 368 + frame_width, avatar_y + 368 + frame_width], outline=review_text_color, width=frame_width)
        card.paste(avatar, (avatar_x, avatar_y))
        recommendation_message = f"Recommended by {game_info['nickname']}"
        draw.text((avatar_x + 425, avatar_y + 50), recommendation_message, font=get_font("noto-sans", size = 50, weight = 500), fill=(0, 0, 0))
        playtime_2weeks = f"Playtime in 2 weeks: {game_info['playtime_2weeks'] // 60} hr(s) {game_info['playtime_2weeks'] % 60} min(s)"
        playtime_forever = f"Total playtime: {game_info['playtime_forever'] // 60} hr(s) {game_info['playtime_forever'] % 60} min(s)"
        draw.text((avatar_x + 425, avatar_y + 150), playtime_2weeks, font=get_font("noto-sans", size = 50, weight = 400), fill=(0, 0, 0))
        draw.text((avatar_x + 425, avatar_y + 250), playtime_forever, font=get_font("noto-sans", size = 50, weight = 400), fill=(0, 0, 0))
    
    draw.text((40, card_height-80), "\u00A9" + f" Generated by Bi_Gu-bot at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fill=(0, 0, 0, 255), font=get_font("noto-sans", size = 40, weight = 400))
    output_path = os.getcwd() + f"/src/data/steam/output/random_game_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    card.save(output_path)
    return MessageSegment.image("file:///" + output_path) 