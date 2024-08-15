from pyncm import apis
import matplotlib.pyplot as plt
import pandas as pd
import requests, os, datetime
from plottable import Table, ColDef
from nonebot.adapters.onebot.v11.message import MessageSegment

from sys import path
path.append("D:/Bi_Gu-bot/passwords")
from passwords import get_passwords

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

def get_ncm_song_card(song_id: int):
    track_detail = apis.track.GetTrackDetail(song_id)
    song_name = track_detail["songs"][0]["name"]
    artists = "/".join([track_detail["songs"][0]["ar"][x]["name"] for x in range(len(track_detail["songs"][0]["ar"]))])
    pic_url = track_detail["songs"][0]["al"]["picUrl"]
    song_url = f"https://music.163.com/#/song?id={song_id}"
    return MessageSegment.music_custom(url = song_url, audio = "audio", title = song_name, content = artists, img_url = pic_url)

    