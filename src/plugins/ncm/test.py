from pyncm import apis
import matplotlib.pyplot as plt
import pandas as pd
import requests, os
from plottable import Table, ColDef
from PIL import Image, ImageDraw, ImageFont
from nonebot.adapters.onebot.v11.message import MessageSegment

from sys import path
path.append("D:/Bi_Gu-bot/passwords")
from passwords import get_passwords

def ncm_search_song(keyword: str, limit: int = 10) -> MessageSegment:
    search_result = apis.cloudsearch.GetSearchResult(keyword = keyword, stype=1, limit = limit)["result"]["songs"]
    song_names, song_artists, song_ids = [], [], []
    for song in search_result:
        song_names.append(song["name"])
        _song_artists = [song["ar"][x]["name"] for x in range(len(song["ar"]))]
        _song_artists_str = " / ".join(_song_artists)
        song_artists.append(_song_artists_str)
        song_ids.append(song["id"])
    df = pd.DataFrame({"Song Name": song_names, "Artists": song_artists, "Song ID": song_ids})
    plt.figure(figsize=(15, 5 * limit / 10))
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
    plt.savefig(os.getcwd() + "/src/data/ncm/search_result.png", bbox_inches='tight', dpi=512)
    return MessageSegment.image("file:///" + os.getcwd() + "/src/data/ncm/search_result.png")

def draw_song_covers(song_data, output_path='output_collage.png'):
    # Set canvas properties
    canvas_width = 512
    canvas_height = 2048
    canvas_margin = 20
    square_size = 100
    text_margin = 10
    font_size = 36
    
    # Create a white canvas
    canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
    
    # Initialize drawing context
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype("arial.ttf", font_size)  # You can use a specific font if you have one
    
    current_y = canvas_margin
    
    # Draw each song cover and information
    for song in song_data:
        # Load song cover image
        cover_path = song['cover_path']  # Replace with your actual file paths
        cover = Image.open(cover_path)
        cover.thumbnail((square_size, square_size))
        
        # Paste the cover onto the canvas
        canvas.paste(cover, (canvas_margin, current_y))
        
        # Draw text to the right of the cover
        text = f"{song['title']}\n{song['artist']}"
        text_width, text_height = font.textsize(text, font=font)
        text_position = (
            canvas_margin + square_size + text_margin,
            current_y + (square_size - text_height) // 2
        )
        draw.text(text_position, text, font=font, fill='black')
        
        # Update the Y coordinate for the next cover and text
        current_y += square_size + text_margin
    
    # Save or display the final image
    canvas.save(output_path)
    canvas.show()

# Example usage:
song_data = [
    {'cover_path': 'cover1.jpg', 'title': 'Song 1', 'artist': 'Artist 1'},
    {'cover_path': 'cover2.jpg', 'title': 'Song 2', 'artist': 'Artist 2'},
    # Add more song data as needed
]

def ncm_search_song_pil(keyword: str, limit: int = 10):
    search_result = apis.cloudsearch.GetSearchResult(keyword = keyword, stype=1, limit = limit)["result"]["songs"]
    song_data = []
    song_names, song_artists, song_ids, song_cover_urls = [], [], [], {}
    for song in search_result:
        song_names.append(song["name"])
        _song_artists = [song["ar"][x]["name"] for x in range(len(song["ar"]))]
        _song_artists_str = " / ".join(_song_artists)
        song_artists.append(_song_artists_str)
        song_ids.append(song["id"])
        song_cover_urls[song["name"]] = song["al"]["picUrl"]
    print(song_cover_urls)
    for song_name in song_cover_urls:
        cover_url = song_cover_urls[song_name]
        cover = requests.get(cover_url).content
        with open(f"D://Bi_Gu-bot/Bi_Gu-bot/src/data/ncm/{song_name}.jpg", "wb") as f:
            f.write(cover)
    df = pd.DataFrame({"Song Name": song_names, "Artists": song_artists, "Song ID": song_ids})
    for song in search_result:
        song_data.append({
            'cover_path': f"D://Bi_Gu-bot/Bi_Gu-bot/src/data/ncm/{song['name']}.jpg",
            'title': song["name"],
            'artist': " / ".join([song["ar"][x]["name"] for x in range(len(song["ar"]))])
        })
    draw_song_covers(song_data, output_path='D://Bi_Gu-bot/Bi_Gu-bot/src/data/ncm/search_result.png')

ncm_search_song_pil("USAO")
