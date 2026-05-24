import httpx, datetime
from typing import Dict, List, Tuple, Any, Optional
from nonebot.adapters.onebot.v11.message import MessageSegment
from PIL import Image, ImageDraw
from utils.utils import get_output_path
from utils.fonts import get_font

ROOM_LEVELS: Dict[int, Tuple[str, Tuple[int, int, int]]] = {0: ("般", (120, 120, 120)),
                                                            1: ("上", (0, 128, 0)),
                                                            2: ("特", (30, 90, 180)),
                                                            3: ("鳳", (200, 130, 0))}

DAN_LIST_4: List[Tuple[str, int, int]] = [("新人", 0, 20), ("9級", 0, 20), ("8級", 0, 20), ("7級", 0, 20), ("6級", 0, 40),
                                          ("5級", 0, 60), ("4級", 0, 80), ("3級", 0, 100), ("2級", 0, 100), ("1級", 0, 100),
                                          ("初段", 200, 400), ("二段", 400, 800), ("三段", 600, 1200), ("四段", 800, 1600),
                                          ("五段", 1000, 2000), ("六段", 1200, 2400), ("七段", 1400, 2800), ("八段", 1600, 3200),
                                          ("九段", 1800, 3600), ("十段", 2000, 4000), ("天鳳位", 2000, 0)]
_ROOM_MIN_DAN = {0: 0, 1: 10, 2: 13, 3: 16}

def _pt_delta(rank: int, room: int, length: int, dan_idx: int) -> int:
    return 0 if rank == 3 else (0 if dan_idx < 8 else (-10 if length == 1 else -15) * (dan_idx - 7)) if rank == 4 \
             else ((20, 40, 50, 60) if rank == 1 else (10, 10, 20, 30))[room] * (3 if length == 2 else 2) // 2


async def _fetch_user(username: str) -> Optional[Dict[str, Any]]:
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            data = (await client.get("https://nodocchi.moe/api/listuser.php", params={"name": username})).json()
    except Exception: return None
    return data if isinstance(data, dict) and data.get("list") else None

def _idlife_start(matches: List[Dict[str, Any]]) -> int:
    ordered = sorted((mt.get("starttime", 0) for mt in matches), key=lambda t: t)
    if not ordered: return 0
    cutoff, last_ts = ordered[0], ordered[0]
    for ts in ordered[1:]:
        if ts - last_ts >= 181 * 86400: cutoff = ts
        last_ts = ts
    return cutoff

def _simulate_dan_4(target: str, matches: List[Dict[str, Any]]) -> Optional[Tuple[str, int]]:
    cutoff = _idlife_start(matches)
    sorted_matches = sorted((mt for mt in matches if int(mt.get("playernum", 4)) == 4
                                                  and mt.get("sctype") in ("b", "c")
                                                  and mt.get("starttime", 0) >= cutoff),
                            key=lambda mt: mt.get("starttime", 0))
    if not sorted_matches: return None
    dan_idx = _ROOM_MIN_DAN.get(int(sorted_matches[0].get("playerlevel", 0)), 0); pt = DAN_LIST_4[dan_idx][1]
    for match in sorted_matches:
        try: room, length = int(match.get("playerlevel", 0)), int(match.get("playlength", 2))
        except (TypeError, ValueError): continue
        ranked_players = sorted(((pi, float(match.get(f"player{pi}ptr", 0) or 0)) for pi in range(1, 5)), key=lambda x: -x[1])
        rank = next((r for r, (pi, _) in enumerate(ranked_players, 1) if match.get(f"player{pi}") == target), None)
        if rank is None: continue
        pt += _pt_delta(rank, room, length, dan_idx)
        while True:
            if dan_idx < len(DAN_LIST_4) - 1 and pt >= DAN_LIST_4[dan_idx][2]: dan_idx, pt = dan_idx + 1, DAN_LIST_4[dan_idx + 1][1]; continue
            if dan_idx >= 10 and pt < 0: dan_idx, pt = dan_idx - 1, DAN_LIST_4[dan_idx - 1][1]; continue
            if dan_idx < 10 and pt < 0: pt = 0
            break
    return DAN_LIST_4[dan_idx][0], pt

async def _is_name_ambiguous(name: str, data: Optional[Dict[str, Any]] = None) -> bool:
    if not name or name == "NoName": return True
    if data is None: data = await _fetch_user(name)
    if not data: return False
    return len(data.get("rseq", []) or []) > 1 or any([match.get(f"player{pi}") for pi in range(1, 5)].count(name) > 1 for match in data.get("list", []))

async def _get_player_dan(username: str, playernum: int) -> Optional[Tuple[str, int]]:
    if playernum != 4: return None
    data = await _fetch_user(username)
    return None if not data or await _is_name_ambiguous(username, data) else _simulate_dan_4(username, data.get("list", []))

async def get_dan_change(username: str) -> Optional[Tuple[Tuple[str, int], Tuple[str, int]]]:
    data = await _fetch_user(username)
    if not data or await _is_name_ambiguous(username, data): return None
    all_matches = data.get("list", [])
    cutoff = _idlife_start(all_matches)
    eligible = sorted((mt for mt in all_matches if int(mt.get("playernum", 4)) == 4
                                                and mt.get("sctype") in ("b", "c")
                                                and mt.get("starttime", 0) >= cutoff),
                      key=lambda mt: mt.get("starttime", 0))
    if not eligible: return None
    after = _simulate_dan_4(username, all_matches)
    start_idx = _ROOM_MIN_DAN.get(int(eligible[0].get("playerlevel", 0)), 0)
    before = (DAN_LIST_4[start_idx][0], DAN_LIST_4[start_idx][1]) if len(eligible) == 1 else _simulate_dan_4(username, [mt for mt in all_matches if mt is not eligible[-1]])
    return None if after is None or before is None else (before, after)

async def _get_player_rate(username: str, playernum: int) -> Optional[int]:
    data = await _fetch_user(username)
    if not data: return None
    rate_val = (data.get("rate") or {}).get(str(playernum)) or (data.get("rate") or {}).get(playernum)
    try: return int(rate_val) if rate_val is not None else None
    except Exception: return None

def _match_key(match: Dict[str, Any]) -> str:
    url = match.get("url", "") or ""
    return url.split("log=", 1)[1] if "log=" in url else f"st_{match.get('starttime', 0)}"

def _find_player_index(match: Dict[str, Any], username: str) -> int:
    return next((pi for pi in range(1, 5) if match.get(f"player{pi}") == username), 0)

def _get_mode_str(match: Dict[str, Any]) -> Tuple[str, Tuple[int, int, int]]:
    player_num, room_level, play_length = match.get("playernum", 4), match.get("playerlevel", 0), match.get("playlength", 2)
    room_label, room_color = ROOM_LEVELS.get(room_level, (f"Lv{room_level}", (0, 0, 0)))
    base = f"{'三' if player_num == 3 else '四'}{room_label}{'東' if play_length == 1 else '南'}"
    return base + ("喰" if match.get("kuitanari", 1) else "") + ("赤" if match.get("akaari", 1) else "") + ("速" if match.get("speed", 0) else ""), room_color

async def get_latest_match(username: str) -> Dict[str, Any]:
    data = await _fetch_user(username)
    if not data: return {}
    matches = sorted(data["list"], key=lambda mt: mt.get("starttime", 0), reverse=True)
    if not matches or _find_player_index(matches[0], username) == 0: return {}
    latest = dict(matches[0])
    latest["_key"] = _match_key(latest)
    latest["_meta"] = {"name": data.get("name", username), "rate": data.get("rate", {}), "recent": data.get("recent", 0), "total": len(data["list"])}
    return latest

async def get_user_summary(username: str) -> MessageSegment:
    data = await _fetch_user(username)
    if not data: return MessageSegment.text(f"未找到天凤玩家「{username}」的对局数据")
    matches = sorted(data["list"], key=lambda mt: mt.get("starttime", 0), reverse=True)
    rate = data.get("rate", {})
    lines = [f"天凤玩家「{data.get('name', username)}」", f"总对局数: {len(matches)}", f"段位R: {' / '.join(f'{k}人麻R{v}' for k, v in rate.items()) if rate else 'N/A'}", "———— 近5局 ————"]
    for match in matches[:5]:
        player_idx = _find_player_index(match, username)
        if player_idx == 0: continue
        mode_str, _ = _get_mode_str(match)
        start_str = datetime.datetime.fromtimestamp(match.get("starttime", 0)).strftime("%Y-%m-%d %H:%M")
        ptr = match.get(f"player{player_idx}ptr", "")
        ranked_players = sorted(((pi, float(match.get(f"player{pi}ptr", 0) or 0)) for pi in range(1, int(match.get("playernum", 4)) + 1)), key=lambda x: -x[1])
        rank = next((r for r, (pi, _) in enumerate(ranked_players, 1) if pi == player_idx), None)
        lines.append(f"[{start_str}] {mode_str} 第{rank if rank else '?'}位 {ptr}pt")
    return MessageSegment.text("\n".join(lines))

async def create_match_result_image(match: Dict[str, Any], username: str) -> MessageSegment:
    player_num = match.get("playernum", 4)
    width, height = 1000, 200 + 40 * player_num
    img = Image.new("RGB", (width, height), (240, 240, 240)); draw = ImageDraw.Draw(img)
    font_normal, font_bold, font_title = get_font("noto-sans", 30, 400), get_font("noto-sans", 30, 500), get_font("noto-sans", 36, 400)
    match_key = match.get("_key", _match_key(match))
    start_ts = match.get("starttime", 0); end_ts = start_ts + match.get("during", 0) * 60
    start_str = datetime.datetime.fromtimestamp(start_ts).strftime("%Y-%m-%d %H:%M")
    end_str = datetime.datetime.fromtimestamp(end_ts).strftime("%Y-%m-%d %H:%M")
    mode_str, mode_color = _get_mode_str(match)
    draw.text((50, 30), mode_str, fill=mode_color, font=font_title)
    draw.text((50, 80), f"{start_str} ~ {end_str}", fill=(50, 50, 50), font=font_normal)
    players = []
    for pi in range(1, player_num + 1):
        name = match.get(f"player{pi}", "") or ""; ptr_raw = match.get(f"player{pi}ptr", "0")
        try: ptr_val = float(ptr_raw)
        except Exception: ptr_val = 0.0
        ambiguous = await _is_name_ambiguous(name)
        dan = None if ambiguous else await _get_player_dan(name, player_num)
        rate = None if (dan or ambiguous) else await _get_player_rate(name, player_num)
        players.append((name, ptr_raw, ptr_val, dan, rate, ambiguous))
    players.sort(key=lambda x: x[2], reverse=True)
    for rank, (name, ptr_raw, ptr_val, dan, rate, ambiguous) in enumerate(players, 1):
        font, color = (font_bold, (0, 0, 200)) if name == username else (font_normal, (0, 0, 0))
        tag = "N/A" if ambiguous else f"{dan[0]} {dan[1]}pt" if dan else f"R{rate}" if rate else f"{rank}位"
        draw.text((70, 100 + 40 * rank), f"[{tag}] {name} ({'+' if ptr_val >= 0 else ''}{ptr_raw})", fill=color, font=font)
    draw.rectangle([20, 20, width - 20, height - 20], outline=(200, 200, 200), width=2)
    output_path = get_output_path(f"tenhou_{match_key}"); img.save(output_path)
    return MessageSegment.image("file:///" + output_path)