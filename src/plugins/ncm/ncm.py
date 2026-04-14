from pyncm import apis
from nonebot.adapters.onebot.v11.message import MessageSegment
from typing import Dict, List, Any, Tuple
from PIL import Image, ImageDraw
from selenium.webdriver.common.by import By
from utils.chrome import get_chromedriver
from utils.utils import get_asset_path, get_copyright_str, get_output_path
import html, os, tempfile, asyncio, re
from utils.fonts import get_font

ncm_search_card_template_path = get_asset_path("custom_html/ncm_search_card.html")
ncm_search_card_css_path = get_asset_path("custom_html/ncm_search_card.css")


def load_search_card_assets() -> tuple[str, str]:
    with open(ncm_search_card_template_path, "r", encoding = "utf-8") as f: template = f.read()
    with open(ncm_search_card_css_path, "r", encoding = "utf-8") as f: css = f.read()
    return template, css

def ncm_search_song(keyword: str, limit: int = 20) -> Dict[str, Any]:
    search_result = apis.cloudsearch.GetSearchResult(keyword = keyword, stype=1, limit = limit)["result"]["songs"]
    songs = []
    for song in search_result:
        song_info = {}
        song_info["title"] = song["name"]
        song_info["artist"] = " / ".join([song["ar"][x]["name"] for x in range(len(song["ar"]))])
        song_info["song_id"] = song["id"]
        song_info["cover_url"] = song["al"].get("picUrl", "")
        songs.append(song_info)
    return songs


def build_search_card_html(keyword: str, songs: List[Dict[str, Any]]) -> str:
    template, css = load_search_card_assets()
    card_items = []
    for song in songs:
        title = html.escape(str(song.get("title", "")))
        artist = html.escape(str(song.get("artist", "")))
        song_id = int(song.get("song_id", 0) or 0)
        cover_url = html.escape(str(song.get("cover_url", "")))
        card_items.append(f"""
        <div class=\"item\"> 
            <img class=\"cover\" src=\"{cover_url}\" alt=\"cover\" loading=\"eager\" referrerpolicy=\"no-referrer\"/>
            <div class=\"meta\">
                <div class=\"title\">{title}</div>
                <div class=\"artist\">{artist}</div>
                <div class=\"song-id\">ID: {song_id}</div>
            </div>
        </div>
        """)
    footer_text = html.escape(get_copyright_str())
    safe_keyword = html.escape(keyword)
    style_block = f"<style>\n{css}\n</style>"
    return template.replace("{{STYLE_BLOCK}}", style_block).replace("{{KEYWORD}}", safe_keyword).replace("{{CARD_ITEMS}}", ''.join(card_items)).replace("{{FOOTER}}", footer_text)

async def draw_search_card(keyword: str, limit: int = 20) -> MessageSegment:
    songs = ncm_search_song(keyword, limit)[:limit]
    if not songs: return MessageSegment.text(f"未找到关键词 {keyword} 的歌曲")
    html_content = build_search_card_html(keyword, songs)
    with tempfile.NamedTemporaryFile(mode = "w", encoding = "utf-8", suffix = ".html", delete = False) as f:
        f.write(html_content)
        html_path = f.name
    output_path = get_output_path("ncm_search_card")
    chrome = await get_chromedriver()
    try:
        chrome.get("file:///" + html_path.replace("\\", "/"))
        await asyncio.sleep(0.9)
        size = chrome.execute_script("""
            const root = document.getElementById('card-root');
            const rect = root.getBoundingClientRect();
            return {width: Math.ceil(rect.width), height: Math.ceil(rect.height)};
        """)
        chrome.set_window_size(max(1700, int(size["width"]) + 80), max(900, int(size["height"]) + 120))
        await asyncio.sleep(0.3)
        chrome.find_element(By.ID, "card-root").screenshot(output_path)
    finally:
        chrome.quit()
        if os.path.exists(html_path): os.remove(html_path)
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



    