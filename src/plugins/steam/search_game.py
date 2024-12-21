import requests, json
from typing import List, Dict
from PIL import Image, ImageDraw
from nonebot.adapters.onebot.v11 import MessageSegment
from passwords import get_passwords
from utils.fonts import get_font
from utils.utils import get_copyright_str, get_output_path

async def search_game(game_name: str) -> List[Dict[str, str]]:
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
            if not price_info or not game_info["assets"]: continue
            image_url = game_info["assets"]["banner400"]
            name = game_info["title"]
            temp_file_path = get_output_path(f"steam_search_{name}", temp = True)
            with open(temp_file_path, "wb") as f:
                f.write(requests.get(image_url).content)
            current_price, regular_price = [price_info[0]["deals"][0][x]["amount"] for x in ["price", "regular"]]
            if current_price == regular_price == 0: current_price = regular_price = history_low = "Free to Play"
            else:
                history_low = price_info[0]["deals"][0]["storeLow"]["amount"]
                current_price, regular_price, history_low = [f"{x:.2f} CNY" for x in [current_price, regular_price, history_low]]
            discount = price_info[0]["deals"][0]["cut"]
            game = {"name": name, "banner_path": temp_file_path, "current_price": current_price, 
                    "regular_price": regular_price, "history_low": history_low, "discount": f"-{discount}%"}
            games.append(game)
    return sorted(games, key=lambda x: int(x["discount"].strip('-%')), reverse=True)

async def draw_search_result(game_name: str) -> MessageSegment:
    background_color = (50, 50, 50)  
    text_color = (255, 255, 255)     
    banner_size = (400, 187)         
    padding = 30                     
    item_spacing = 80                
    discount_bg_color = (88, 127, 53)  
    discount_text_color = (195, 255, 101)  

    games = await search_game(game_name)

    font_size, discount_font_size = 30, 50
    font = get_font("noto-sans", size = 40, weight = 400)
    title_font = get_font("noto-sans", size = 40, weight = 500)
    discount_font = get_font("noto-sans", size = 50, weight = 700)

    total_height = len(games) * (banner_size[1] + padding + item_spacing) + 80
    image_width = banner_size[0] + 1500 

    image = Image.new("RGB", (image_width, total_height), background_color)
    draw = ImageDraw.Draw(image)

    y_offset = padding
    for game in games:
        banner = Image.open(game["banner_path"]).resize(banner_size)
        image.paste(banner, (padding, y_offset))
        
        text_x = banner_size[0] + 2 * padding
        text_y = y_offset
        
        draw.text((text_x, text_y - 10), game["name"], font=title_font, fill=text_color)
        text_y += font_size + padding / 2 + 10
        
        discount_box_width = 150  
        discount_box_height = discount_font_size + padding / 2
        discount_box_x = text_x 
        discount_box_y = text_y + 20

        draw.rectangle([discount_box_x, discount_box_y, discount_box_x + discount_box_width, discount_box_y + discount_box_height],
                    fill=discount_bg_color)
        
        discount_bbox = draw.textbbox((0, 0), game["discount"], font=discount_font)
        discount_text_width = discount_bbox[2] - discount_bbox[0]
        discount_text_height = discount_bbox[3] - discount_bbox[1]
        
        discount_text_x = discount_box_x + (discount_box_width - discount_text_width) / 2
        discount_text_y = discount_box_y + (discount_box_height - discount_text_height) / 2 - 18

        draw.text((discount_text_x, discount_text_y), game["discount"], font=discount_font, fill=discount_text_color, align="center")
        
        price_text_x = discount_box_x + discount_box_width + padding
        if game["current_price"] == game["history_low"] != "Free to Play":
            draw.text((price_text_x, text_y+5), f"Current Price: {game['current_price']} (History Low)", font=font, fill=discount_text_color)
        else:
            draw.text((price_text_x, text_y+5), f"Current Price: {game['current_price']}", font=font, fill=text_color)
        text_y += font_size + padding / 2
        
        original_price_x = price_text_x
        draw.text((original_price_x, text_y+5), f"Regular Price: {game['regular_price']}", font=font, fill=text_color)
        
        text_y += font_size + padding / 2
        draw.text((text_x, text_y+10), f"History Low Price: {game['history_low']}", font=font, fill=text_color)
        
        y_offset += banner_size[1] + padding + item_spacing

    draw.text((40, total_height - 80), get_copyright_str(), fill=(255, 255, 255, 255), font=font)
    output_path = get_output_path("steam_search_result")
    image.save(output_path)
    return MessageSegment.image("file:///" + output_path)