from pyncm import apis
from plottable import Table, ColDef
from nonebot.adapters.onebot.v11.message import MessageSegment
from typing import Dict, List, Any, Tuple
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import pandas as pd
import requests, os, datetime, re

from sys import path
path.append(os.getcwd() + "/passwords")
path.append(os.getcwd() + "/src")
from passwords import get_passwords

from utils.fonts import get_font

def ncm_search_song(keyword: str, limit: int = 30) -> MessageSegment:
    search_result = apis.cloudsearch.GetSearchResult(keyword = keyword, stype=1, limit = limit)["result"]["songs"]
    limit = len(search_result)
    song_names, song_artists, song_ids = [], [], []
    for song in search_result:
        song_names.append(song["name"])
        _song_artists = [song["ar"][x]["name"] for x in range(len(song["ar"]))]
        _song_artists_str = " / ".join(_song_artists)
        song_artists.append(_song_artists_str)
        song_ids.append(song["id"])
    df = pd.DataFrame({"Song Name": song_names, "Artists": song_artists, "Song ID": song_ids})
    plt.figure(figsize=(20, 5 * limit / 10))
    Table(df, 
          textprops={"fontsize": 15, "ha": "center","fontfamily": "DengXian"},
          column_definitions=[
            ColDef(name = "index", width = 5),
            ColDef(name = "Song Name", width = 30),
            ColDef(name = "Artists", width = 20),
            ColDef(name = "Song ID", width = 20),
          ],       
          col_label_cell_kw={"facecolor":"#a5d8ff"},
          cell_kw={"facecolor":"#e7f5ff"},
          )
    output_path = os.getcwd() + f"/src/data/ncm/output/search_result_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(output_path, bbox_inches='tight', dpi=512)
    return MessageSegment.image("file:///" + output_path)

def get_ncm_song_card(song_id: int) -> MessageSegment:
    track_detail = apis.track.GetTrackDetail(song_id)
    song_name = track_detail["songs"][0]["name"]
    artists = "/".join([track_detail["songs"][0]["ar"][x]["name"] for x in range(len(track_detail["songs"][0]["ar"]))])
    pic_url = track_detail["songs"][0]["al"]["picUrl"]
    song_url = f"https://music.163.com/#/song?id={song_id}"
    return MessageSegment.music_custom(url = song_url, audio = "audio", title = song_name, content = artists, img_url = pic_url)

def parse_lyrics(raw_lyrics: str) -> Dict[str, str]:
    lines = raw_lyrics.strip().split('\n')
    lyrics_dict = {}
    for line in lines:
        if match := re.match(r'(\[\d{2}:\d{2}\.\d{2,3}\])\s*(.*)', line):
            time, text = match.groups()
            lyrics_dict[time] = text
    return lyrics_dict 

def get_raw_lyrics(song_id: int) -> Tuple[Dict[str, str], int]:
    lyrics = {}
    lyrics_raw = apis.track.GetTrackLyrics(song_id)
    song_type = 0
    for x in ["lrc", "tlyric", "romalrc"]:
        lyrics[x] = ""
        if x in lyrics_raw:
            lyrics[x] = lyrics_raw[x]["lyric"] if lyrics_raw[x]["lyric"] else ""
        if lyrics[x]: song_type += 1
    song_info = apis.track.GetTrackDetail(song_id)["songs"][0]
    lyrics["song_name"] = song_info["name"]
    lyrics["song_artists"] = " / ".join(song_info["ar"][x]["name"] for x in range(len(song_info["ar"])))
    combined_lyrics: List[Dict[str, str]] = []
    lrc_dict, tlyric_dict, romalrc_dict = [parse_lyrics(lyrics[x]) for x in ["lrc", "tlyric", "romalrc"]]
    timestamps = sorted(set(lrc_dict.keys()).union(tlyric_dict.keys()).union(romalrc_dict.keys()))
    for timestamp in timestamps:
        temp = {}
        lrc_text = lrc_dict.get(timestamp, '')
        if song_type >= 2: tlyric_text = tlyric_dict.get(timestamp, '')
        if song_type >= 3: romalrc_text = romalrc_dict.get(timestamp, '')
        if song_type == 3:
            if lrc_text and tlyric_text and romalrc_text: temp = {'lrc': lrc_text, 'tlyric': tlyric_text, 'romalrc': romalrc_text}
        elif song_type == 2:
            if lrc_text and tlyric_text: temp = {'lrc': lrc_text, 'tlyric': tlyric_text}
        else: 
            if lrc_text: temp = {'lrc': lrc_text}  
        if temp: combined_lyrics.append(temp)
    lyrics["combined_lyrics"] = combined_lyrics
    return (lyrics, song_type)

def draw_lyrics_card(song_id: int) -> MessageSegment:
    lyrics, song_type = get_raw_lyrics(song_id)
    song_info = {"title": lyrics["song_name"], "artists": lyrics["song_artists"]}
    combined_lyrics = lyrics["combined_lyrics"]
    max_line_width = 0
    background_color = '#14163E' 
    font_color_primary = '#FFFFFF'
    font_color_secondary = '#B3B6C4'
    title_font = get_font("noto-sans", size = 50, weight = 700)
    lyrics_font_primary = get_font("noto-sans", size = 38, weight = 700) if song_type >= 2 else get_font("noto-sans", size = 38, weight = 400)
    lyrics_font_secondary = get_font("noto-sans", size = 28, weight = 400)
    copyright_font = get_font("noto-sans", size = 18, weight = 400)
    padding_top = 40
    padding_between_blocks = 20
    padding_between_lines = 10
    padding_after_title = 30

    def get_text_height(font, text): return font.getbbox(text)[3] 
    def get_text_width(font, text): return font.getbbox(text)[2]
    
    copyright_str = "\u00A9" + f" Generated by Bi_Gu-bot at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    total_height = padding_top*3 + get_text_height(title_font, song_info['title']) + get_text_height(title_font, song_info['artists']) + padding_after_title + get_text_height(copyright_font, copyright_str)

    for block in combined_lyrics:
        total_height += get_text_height(lyrics_font_primary, block['lrc']) + padding_between_lines
        max_line_width = max(max_line_width, get_text_width(lyrics_font_primary, block['lrc']))
        if 'romalrc' in block:
            total_height += (get_text_height(lyrics_font_secondary, block['romalrc']) + 5)  # Romanized line
            max_line_width = max(max_line_width, get_text_width(lyrics_font_secondary, block['romalrc']))
        if 'tlyric' in block:
            total_height += (get_text_height(lyrics_font_secondary, block['tlyric']) + padding_between_blocks)  # Translated line
            max_line_width = max(max_line_width, get_text_width(lyrics_font_secondary, block['tlyric']))

    image = Image.new('RGB', (image_width:=max_line_width+200, total_height), background_color)
    draw = ImageDraw.Draw(image)

    x, y = 40, padding_top
    draw.text((x, y), f"{song_info['title']}", fill=font_color_primary, font=title_font)
    y += get_text_height(title_font, song_info['title']) + 10
    draw.text((x, y), f"{song_info['artists']}", fill=font_color_secondary, font=title_font)
    y += get_text_height(title_font, song_info['artists']) + padding_after_title 

    for block in combined_lyrics:
        draw.text((x, y), f"{block['lrc']}", fill=font_color_primary, font=lyrics_font_primary)
        y += get_text_height(lyrics_font_primary, block['lrc']) + padding_between_lines
        if 'romalrc' in block:
            draw.text((x, y), f"{block['romalrc']}", fill=font_color_secondary, font=lyrics_font_secondary)
            y += get_text_height(lyrics_font_secondary, block['romalrc']) + 5
        if 'tlyric' in block:
            draw.text((x, y), f"{block['tlyric']}", fill=font_color_secondary, font=lyrics_font_secondary)
            y += get_text_height(lyrics_font_secondary, block['tlyric']) + padding_between_blocks
    draw.text((image_width // 2, total_height - padding_top), copyright_str, font=copyright_font, fill=(255, 255, 255), anchor='mm')

    output_path = "D:/Bi_Gu-bot/Bi_Gu-bot_test/Bi_Gu-bot" + f"/src/data/ncm/output/lyrics_card_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"  
    image.save(output_path)
    return MessageSegment.image("file:///" + output_path) 



    