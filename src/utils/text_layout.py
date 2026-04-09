from typing import List, Callable

import jieba
from PIL import Image, ImageDraw, ImageFont

def regularize_cut(text_cut: List[str], max_token_len: int = 20) -> List[str]:
    ret = []
    for phrase in text_cut:
        while len(phrase) > max_token_len:
            ret.append(phrase[:max_token_len])
            phrase = phrase[max_token_len:]
        ret.append(phrase)
    return ret


def tokenize_text(text: str, use_jieba: bool = True, max_token_len: int = 20) -> List[str]:
    normalized = text.replace("\r", "")
    if not normalized: return []
    text_cut = jieba.lcut(normalized) if use_jieba else list(normalized)
    return regularize_cut(text_cut, max_token_len = max_token_len)


def wrap_tokens_in_box(text_list: List[str], font: ImageFont.ImageFont, image: Image.Image,
                       max_line_width: int, max_total_height: int, force: bool = False) -> str | None:
    def judge_shape(_text: str) -> tuple[bool, bool]:
        bbox = draw.textbbox((0, 0), _text, font = font, align = "center")
        width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        return width > max_line_width, height > max_total_height

    text_list = text_list.copy()
    draw = ImageDraw.Draw(image)
    result = [""]
    while text_list:
        current_text = result[-1] + text_list[0]
        if judge_shape(current_text)[0]:
            result.append(text_list.pop(0))
            if judge_shape("\n".join(result))[1]:
                return "\n".join(result[:-1]) if force else None
        else:
            result[-1] += text_list.pop(0)
    return "\n".join(result)


def wrap_text_by_width(text: str, draw: ImageDraw.ImageDraw, font: ImageFont.ImageFont,
                       max_width: int, max_lines: int = 4, use_jieba: bool = True) -> list[str]:
    text_tokens = tokenize_text(text.strip(), use_jieba = use_jieba, max_token_len = 20)
    if not text_tokens: return ["[空消息]"]
    lines = [""]
    for token in text_tokens:
        candidate = lines[-1] + token
        if draw.textlength(candidate, font = font) <= max_width:
            lines[-1] = candidate
            continue
        if lines[-1]: lines.append("")
        if draw.textlength(token, font = font) <= max_width: lines[-1] = token
        else: # Safety fallback for overlong tokens.
            buf = ""
            for ch in token:
                _candidate = buf + ch
                if draw.textlength(_candidate, font = font) <= max_width: buf = _candidate
                else:
                    lines[-1] = buf if buf else ch
                    lines.append("")
                    buf = "" if buf else ""
                    if not buf and draw.textlength(ch, font = font) <= max_width: buf = ch
            if buf: lines[-1] = buf
    lines = [line if line else " " for line in lines]
    if len(lines) > max_lines:
        clipped = lines[:max_lines]
        while clipped[-1] and draw.textlength(clipped[-1] + "...", font = font) > max_width:
            clipped[-1] = clipped[-1][:-1]
        clipped[-1] = (clipped[-1] + "...") if clipped[-1] else "..."
        return clipped
    return lines

def pick_font_and_wrap_by_width(text: str, draw: ImageDraw.ImageDraw,
                                get_font_func: Callable[..., ImageFont.ImageFont],
                                font_name: str | tuple[str, str], font_sizes: List[int], max_width: int,
                                max_lines: int = 4, use_jieba: bool = True,
                                line_gap: int = 0, max_text_height: int | None = None,
                                min_font_size: int = 16) -> tuple[ImageFont.ImageFont, list[str], int, int]:
    def build_font(size: int) -> ImageFont.ImageFont:
        size = max(min_font_size, size)
        return get_font_func(font_name[0], font_name[1], size) if isinstance(font_name, tuple) else get_font_func(font_name, size)

    for size in font_sizes:
        font = build_font(size)
        lines = wrap_text_by_width(text, draw, font, max_width = max_width, max_lines = max_lines, use_jieba = use_jieba)
        line_height = font.getbbox("测")[3] - font.getbbox("测")[1]
        text_h = len(lines) * line_height + (len(lines) - 1) * line_gap
        if max_text_height is None or text_h <= max_text_height: return font, lines, line_gap, line_height
    font = build_font(font_sizes[-1])
    lines = wrap_text_by_width(text, draw, font, max_width = max_width, max_lines = max_lines, use_jieba = use_jieba)
    line_height = font.getbbox("测")[3] - font.getbbox("测")[1]
    return font, lines, line_gap, line_height