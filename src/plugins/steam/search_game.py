import requests, json, os, datetime, shutil
from typing import List, Dict
from PIL import Image, ImageDraw, ImageFont
from nonebot.adapters.onebot.v11 import MessageSegment

from sys import path
path.append("D:/Bi_Gu-bot/passwords")
from passwords import get_passwords

def search_game(game_name: str) -> List[Dict[str, str]]:
    api_key = get_passwords("isthereanydeal_api_key")
    search_url = "https://api.isthereanydeal.com/games/search/v1"
    info_url = "https://api.isthereanydeal.com/games/info/v2"
    price_url = "https://api.isthereanydeal.com/games/prices/v2"
    games = []
    response = requests.get(search_url, params= {"key": api_key, "title": game_name}).json()
    if response:
        for item in response:
            game = {}
            if item["type"] not in ["game", "dlc"]: continue
            game_info = requests.get(url = info_url, params = {"key": api_key, "id": item["id"]}).json()
            if "appid" not in game_info: continue
            price_info = requests.post(url = price_url, params = {"key": api_key, "country": "CN", "nondeals": True, "shops": 61}, data = json.dumps([item["id"]])).json()
            if not price_info: continue
            image_url = game_info["assets"]["banner400"]
            name = game_info["title"]
            with open(os.getcwd() + f"/src/data/steam/temp/{name}.png", "wb") as f:
                f.write(requests.get(image_url).content)
            current_price, regular_price = [price_info[0]["deals"][0][x]["amount"] for x in ["price", "regular"]]
            if current_price == regular_price == 0: current_price = regular_price = history_low = "Free to Play"
            else:
                history_low = price_info[0]["deals"][0]["storeLow"]["amount"]
                current_price, regular_price, history_low = [f"{x:.2f} CNY" for x in [current_price, regular_price, history_low]]
            discount = price_info[0]["deals"][0]["cut"]
            game = {"name": name, "banner_path": os.getcwd() + f"/src/data/steam/temp/{name}.png", 
                    "current_price": current_price, "regular_price": regular_price, "history_low": history_low, "discount": f"-{discount}%"}
            games.append(game)
    return games

def draw_search_result(game_name: str) -> MessageSegment:
    background_color = (50, 50, 50)  
    text_color = (255, 255, 255)     
    banner_size = (400, 187)         
    padding = 20                     
    discount_bg_color = (88, 127, 53)  
    discount_text_color = (195, 255, 101)  

    games = search_game(game_name)

    font_path = os.getcwd() + "/src/data/steam/fonts/NotoSans-Regular.ttf"
    bold_font_path = os.getcwd() + "/src/data/steam/fonts/NotoSans-Bold.ttf"
    semibold_font_path = os.getcwd() + "/src/data/steam/fonts/NotoSans-SemiBold.ttf"
    font_size = 30
    discount_font_size = 50
    font = ImageFont.truetype(font_path, font_size)
    title_font = ImageFont.truetype(semibold_font_path, font_size)
    discount_font = ImageFont.truetype(bold_font_path, discount_font_size)

    total_height = len(games) * (banner_size[1] + padding) + 80
    image_width = banner_size[0] + 1000 

    image = Image.new("RGB", (image_width, total_height), background_color)
    draw = ImageDraw.Draw(image)

    y_offset = padding
    for game in games:
        banner = Image.open(game["banner_path"]).resize(banner_size)
        image.paste(banner, (padding, y_offset))
        
        text_x = banner_size[0] + 2 * padding
        text_y = y_offset
        
        draw.text((text_x, text_y), game["name"], font=title_font, fill=text_color)
        text_y += font_size + padding / 2
        
        discount_box_width = 150  
        discount_box_height = discount_font_size + padding / 2
        discount_box_x = text_x 
        discount_box_y = text_y + 10

        draw.rectangle([discount_box_x, discount_box_y, discount_box_x + discount_box_width, discount_box_y + discount_box_height],
                    fill=discount_bg_color)
        
        discount_bbox = draw.textbbox((0, 0), game["discount"], font=discount_font)
        discount_text_width = discount_bbox[2] - discount_bbox[0]
        discount_text_height = discount_bbox[3] - discount_bbox[1]
        
        discount_text_x = discount_box_x + (discount_box_width - discount_text_width) / 2
        discount_text_y = discount_box_y + (discount_box_height - discount_text_height) / 2 - 15

        draw.text((discount_text_x, discount_text_y), game["discount"], font=discount_font, fill=discount_text_color, align="center")
        
        price_text_x = discount_box_x + discount_box_width + padding
        draw.text((price_text_x, text_y), f"Current Price: {game['current_price']}", font=font, fill=text_color)
        text_y += font_size + padding / 2
        
        original_price_x = price_text_x
        draw.text((original_price_x, text_y), f"Regular Price: {game['regular_price']}", font=font, fill=text_color)
        
        text_y += font_size + padding / 2
        draw.text((text_x, text_y), f"History Low Price: {game['history_low']}", font=font, fill=text_color)
        
        y_offset += banner_size[1] + padding

    draw.text((40, total_height-50), "\u00A9" + f" Generated by Bi_Gu-bot at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fill=(255, 255, 255, 255), font=font)
    image.save(os.getcwd() + f"/src/data/steam/output/search_result_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")

    folderpath = os.getcwd() + "/src/data/steam/temp"
    for filename in os.listdir(folderpath):
        filepath = os.path.join(folderpath, filename)
        os.remove(filepath) if os.path.isfile(filepath) else shutil.rmtree(filepath)
    return MessageSegment.image("file:///" + os.getcwd() + f"/src/data/steam/output/search_result_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png") 