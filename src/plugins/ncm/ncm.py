from pyncm import apis
from plottable import Table, ColDef
from nonebot.adapters.onebot.v11.message import MessageSegment
from typing import Dict, List, Any, Tuple
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import pandas as pd
import re, requests
from utils.fonts import get_font
from utils.utils import get_copyright_str, get_output_path

def ncm_search_song(keyword: str, limit: int = 20) -> Dict[str, Any]:
    search_result = apis.cloudsearch.GetSearchResult(keyword = keyword, stype=1, limit = limit)["result"]["songs"]
    limit = len(search_result)
    songs = []
    for song in search_result:
        song_info = {}
        song_info["title"] = song["name"]
        song_info["artist"] = " / ".join([song["ar"][x]["name"] for x in range(len(song["ar"]))])
        song_info["song_id"] = song["id"]
        temp_path = get_output_path(f"ncm_cover_{song_info['song_id']}", temp = True)
        with open(temp_path, "wb") as f:
            f.write(requests.get(song["al"]["picUrl"]).content)
        song_info["cover_path"] = temp_path
        songs.append(song_info)
    return songs

async def draw_search_card(keyword: str, limit: int = 20) -> MessageSegment:
    songs = ncm_search_song(keyword, limit)[:limit]  

    cover_size = (200, 200)  
    title_font_size = 36
    details_font_size = 28   
    line_spacing_title_artist = 15  
    line_spacing_artist_id = 10     
    max_text_width = 340            
    column_spacing = 800          
    header_font_size = 42
    footer_font_size = 28

    title_font = get_font("noto-sans", size = title_font_size, weight = 700)
    details_font = get_font("noto-sans", size = details_font_size, weight = 400)
    header_font = get_font("noto-sans", size = header_font_size, weight = 700)
    footer_font = get_font("noto-sans", size = footer_font_size, weight = 400)
    header_text = f"Search result for '{keyword}':"
    footer_text = get_copyright_str()

    temp_canvas = Image.new("RGB", (1, 1))
    temp_draw = ImageDraw.Draw(temp_canvas)

    def wrap_text(text, font, max_width, max_chars=20):
        lines, current_line = [], []
        words = text.split()
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = temp_draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            if width <= max_width and len(test_line) <= max_chars: current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line: lines.append(' '.join(current_line))
        wrapped_lines = []
        for line in lines:
            while len(line) > max_chars:
                wrapped_lines.append(line[:max_chars])
                line = line[max_chars:]
            if line: wrapped_lines.append(line)
        return wrapped_lines

    header_width = temp_draw.textbbox((0, 0), header_text, font=header_font)[2]
    footer_width = temp_draw.textbbox((0, 0), footer_text, font=footer_font)[2]

    margin_x, margin_y = 10, 20
    text_offset_x = cover_size[0] + 30  
    initial_row_height = cover_size[1] + 30
    grid_heights = []

    for song in songs:
        title_lines = wrap_text(song["title"], title_font, max_text_width)
        artist_lines = wrap_text(song["artist"], details_font, max_text_width)
        num_lines = len(title_lines) + len(artist_lines) + 1
        grid_height = initial_row_height + (num_lines - 1) * details_font_size + line_spacing_title_artist + line_spacing_artist_id
        grid_heights.append(grid_height)

    canvas_height = margin_y * 2 + header_font_size + 40 + sum(grid_heights[:10]) + 40 + footer_font_size
    canvas_width = max(column_spacing * 2 + margin_x * 2, header_width + 40, footer_width + 40) + 180

    background_color = (31, 31, 46)
    canvas = Image.new("RGB", (canvas_width, canvas_height), background_color)
    draw = ImageDraw.Draw(canvas)

    header_x = (canvas_width - header_width) // 2
    draw.text((header_x, margin_y), header_text, font=header_font, fill="white")

    current_y_offset = margin_y + header_font_size + 40
    for index, song in enumerate(songs):
        row, col = index // 2, index % 2
        x_offset = margin_x + col * column_spacing + (column_spacing - cover_size[0] - text_offset_x) // 2
        y_offset = current_y_offset
        album_cover = Image.open(song["cover_path"]).resize(cover_size)
        canvas.paste(album_cover, (x_offset, y_offset))
        text_x_offset = x_offset + text_offset_x
        text_y_offset = y_offset
        for line in wrap_text(song["title"], title_font, max_text_width):
            draw.text((text_x_offset, text_y_offset), line, font=title_font, fill="white")
            text_y_offset += title_font_size
        text_y_offset += line_spacing_title_artist
        for line in wrap_text(song["artist"], details_font, max_text_width):
            draw.text((text_x_offset, text_y_offset), line, font=details_font, fill="#A2A5C2")
            text_y_offset += details_font_size
        text_y_offset += line_spacing_artist_id
        draw.text((text_x_offset, text_y_offset), f"ID: {song['song_id']}", font=details_font, fill="lightgray")
        if col == 1: current_y_offset += grid_heights[row]
    footer_x = (canvas_width - footer_width) // 2
    draw.text((footer_x, canvas_height - footer_font_size - 20), footer_text, font=footer_font, fill="white")

    output_path = get_output_path("ncm_search_card")
    canvas.save(output_path)
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

def get_raw_lyrics(song_id: int) -> Tuple[Dict[str, str], str]:
    lyrics = {}
    lyrics_raw = apis.track.GetTrackLyrics(song_id)
    song_type = 0
    for x in ["lrc", "tlyric", "romalrc"]:
        lyrics[x] = ""
        if x in lyrics_raw:
            lyrics[x] = lyrics_raw[x]["lyric"] if lyrics_raw[x]["lyric"] else ""
    song_type = "jpn" if lyrics["lrc"] and lyrics["tlyric"] and lyrics["romalrc"] else \
                "eng" if lyrics["lrc"] and lyrics["tlyric"] else \
                "can" if lyrics["lrc"] and lyrics["romalrc"] else "chn"
    song_info = apis.track.GetTrackDetail(song_id)["songs"][0]
    lyrics["song_name"] = song_info["name"]
    lyrics["song_artists"] = " / ".join(song_info["ar"][x]["name"] for x in range(len(song_info["ar"])))
    combined_lyrics: List[Dict[str, str]] = []
    lrc_dict, tlyric_dict, romalrc_dict = [parse_lyrics(lyrics[x]) for x in ["lrc", "tlyric", "romalrc"]]
    timestamps = sorted(set(lrc_dict.keys()).union(tlyric_dict.keys()).union(romalrc_dict.keys()))
    for timestamp in timestamps:
        temp = {}
        lrc_text = lrc_dict.get(timestamp, '')
        if song_type in ["jpn", "eng"]: tlyric_text = tlyric_dict.get(timestamp, '')
        if song_type in ["jpn", "can"]: romalrc_text = romalrc_dict.get(timestamp, '')
        if song_type == "jpn":
            if lrc_text and tlyric_text and romalrc_text: temp = {'lrc': lrc_text, 'tlyric': tlyric_text, 'romalrc': romalrc_text}
        elif song_type == "eng":
            if lrc_text and tlyric_text: temp = {'lrc': lrc_text, 'tlyric': tlyric_text}
        elif song_type == "can":
            if lrc_text and romalrc_text: temp = {'lrc': lrc_text, 'romalrc': romalrc_text}
        else: 
            if lrc_text: temp = {'lrc': lrc_text}  
        if temp: combined_lyrics.append(temp)
    lyrics["combined_lyrics"] = combined_lyrics
    return (lyrics, song_type)

async def draw_lyrics_card(song_id: int) -> MessageSegment:
    lyrics, song_type = get_raw_lyrics(song_id)
    song_info = {"title": lyrics["song_name"], "artists": lyrics["song_artists"]}
    combined_lyrics = lyrics["combined_lyrics"]
    max_line_width = 0
    background_color = '#14163E' 
    font_color_primary = '#FFFFFF'
    font_color_secondary = '#B3B6C4'
    title_font = get_font("noto-sans", size = 50, weight = 700)
    lyrics_font_primary = get_font("noto-sans", size = 38, weight = 400) if song_type == "chn" else get_font("noto-sans", size = 38, weight = 700)
    lyrics_font_secondary = get_font("noto-sans", size = 28, weight = 400)
    copyright_font = get_font("noto-sans", size = 18, weight = 400)
    padding_top = 40
    padding_between_blocks = 20
    padding_between_lines = 10
    padding_after_title = 30

    def get_text_height(font, text): return font.getbbox(text)[3] 
    def get_text_width(font, text): return font.getbbox(text)[2]
    
    copyright_str = get_copyright_str()
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

    output_path = get_output_path("ncm_lyrics_card")
    image.save(output_path)
    return MessageSegment.image("file:///" + output_path) 



    