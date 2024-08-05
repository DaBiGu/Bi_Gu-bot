from pyncm import apis
import matplotlib.pyplot as plt
import pandas as pd
import requests, os
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
    plt.savefig(os.getcwd() + "/src/data/ncm/search_result.png", bbox_inches='tight', dpi=512)
    return MessageSegment.image("file:///" + os.getcwd() + "/src/data/ncm/search_result.png")

def ncm_get_song_mp3(song_id: int):
  login = apis.login.LoginViaCellphone(get_passwords["ncm_phone_number"], get_passwords["ncm_password"])
  song_name = apis.track.GetTrackDetail(song_id)["songs"][0]["name"]
  song_url = apis.track.GetTrackAudio(song_id)["data"][0]["url"]
  filename = os.getcwd() + "/src/data/ncm/" + song_name + ".mp3"
  with open(filename, "wb") as f:
    f.write(requests.get(song_url).content)
  return MessageSegment.music

    