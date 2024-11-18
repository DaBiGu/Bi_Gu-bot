import json, random
from thefuzz import process
from typing import Dict, Any
from PIL import Image, ImageDraw, ImageFont
from utils.utils import get_asset_path, get_copyright_str, get_output_path
from utils.fonts import get_font
from nonebot.adapters.onebot.v11 import MessageSegment

json_path = get_asset_path("phigros/music-info.json")
tips_path = get_asset_path("phigros/tips.txt")

def search_similar_song(songname: str) -> str:
    with open(json_path, "r", encoding="utf-8") as f: music_info = json.load(f)
    return process.extractOne(songname, [music["title"] for music in music_info])[0]

def get_song_info(songname: str) -> Dict[str, Any]:
    with open(json_path, "r", encoding="utf-8") as f: song_info = json.load(f)
    for song in song_info:
        if song["title"] == songname:
            return song
        
def song_preprocess(_song: Dict[str, Any]) -> Dict[str, Any]:
    song = {}
    song["cover_url"] = get_asset_path(f"phigros/Illustration/{_song['sid']}.png")
    song["title"] = _song["title"]
    song["artist"] = _song["composer"]
    for difficulty in ["EZ", "HD", "IN", "AT"]:
        if difficulty in _song["chartDetail"]:
            song[difficulty] = _song["chartDetail"][difficulty]["rating"]

    return song
    
def get_embedded_font(size: int) -> ImageFont:
    return ImageFont.FreeTypeFontFamily(get_font("Saira", size = size), get_font("sourcehan-sans", size = size))

def create_song_image(song_data: Dict[str, Any]) -> MessageSegment:
    cover_img = Image.open(song_data["cover_url"])
    
    width, height = 1600, 900  
    background_color = (45, 45, 45)
    difficulty_colors = {"EZ":(50, 205, 50),"HD":(30, 144, 255),"IN":(255, 69, 0),"AT":(169, 169, 169)}
    
    img = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(img)
    difficulty_font = get_embedded_font(32) 
    
    cover_width = width - 600 
    cover_height = int(cover_width * (1080 / 2048))
    cover_resized = cover_img.resize((cover_width, cover_height))
    cover_x = (width - cover_width) // 2
    cover_y = 50
    img.paste(cover_resized, (cover_x, cover_y))

    title_y = cover_y + cover_resized.height + 80
    draw.text((width // 2, title_y), song_data["title"], font=get_embedded_font(48), fill=(255, 255, 255), anchor="mm")

    artist_y = title_y + 60
    draw.text((width // 2, artist_y), song_data["artist"], font=get_embedded_font(36), fill=(255, 255, 255), anchor="mm")

    difficulty_texts = []
    for key in ["EZ", "HD", "IN", "AT"]:
        if key in song_data: difficulty_texts.append((f"{key} {song_data[key]}", difficulty_colors[key]))

    difficulty_y = artist_y + 90

    total_width = 0
    for idx, (text, _) in enumerate(difficulty_texts):
        text_width = difficulty_font.getbbox(text)[2]
        total_width += text_width
        if idx < len(difficulty_texts) - 1: total_width += difficulty_font.getbbox(" / ")[2]

    x = (width - total_width) // 2
    for idx, (text, color) in enumerate(difficulty_texts):
        draw.text((x, difficulty_y), text, font=difficulty_font , fill=color, anchor="lm")
        x += difficulty_font.getbbox(text)[2]
        if idx < len(difficulty_texts) - 1:
            draw.text((x, difficulty_y), " / ", font=difficulty_font , fill=(255, 255, 255), anchor="lm")
            x += difficulty_font.getbbox(" / ")[2] 
    with open(tips_path, "r", encoding="utf-8") as f: tips = f.readlines()
    tip = random.choice(tips).strip()
    draw.text((20, height - 80), f"Tip: {tip}", fill=(255, 255, 255), font=get_embedded_font(24))
    draw.text((20, height - 40), get_copyright_str(), fill=(255, 255, 255), font=get_embedded_font(24))

    output_path = get_output_path("phigros_search_song")

    img.save(output_path)
    return MessageSegment.image("file:///" + output_path) 

def phigros_search_song(songname: str) -> MessageSegment:
    song_data = song_preprocess(get_song_info(search_similar_song(songname)))
    return create_song_image(song_data)