import os, cv2, jieba
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from typing import List

from nonebot.adapters.onebot.v11.message import Message, MessageSegment

def get_file_path(file_name: str) -> str:
    return os.getcwd() + "/src/data/draw_image/" + file_name

def auto_warp(text_list: List[str], font: ImageFont, image: Image, force: bool = False) -> str | None:
    def judge_shape(_text: str) -> tuple[bool, bool]:
        bbox = draw.textbbox((0, 0), _text, font = font, align = "center")
        [width, height] = [bbox[2] - bbox[0], bbox[3] - bbox[1]]
        return [True if width > 3 * image.size[0] // 4 else False, True if height > 550 else False]
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

def multiply_image(img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
    return ((img1/255) * (img2/255) * 255).astype(np.uint8)

def overlay_image(upper: np.ndarray, lower: np.ndarray) -> np.ndarray:
    upper_gray = cv2.cvtColor(upper, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(upper_gray, 254, 255, cv2.THRESH_BINARY_INV)
    mask_inv = cv2.bitwise_not(mask)
    upper_fg = cv2.bitwise_and(upper, upper, mask = mask)
    lower_bg = cv2.bitwise_and(lower, lower, mask = mask_inv)
    return cv2.add(upper_fg, lower_bg)

def regularize_cut(text_cut: List[str]) -> List[str]:
    ret = []
    for phrase in text_cut:
        while len(phrase) > 20:
            ret.append(phrase[:20])
            phrase = phrase[20:]
        ret.append(phrase)
    return ret

def get_text_mask(text: str, img: np.ndarray) -> np.ndarray:
    shape = img.shape
    img = np.ones(shape, dtype = np.uint8) * 255
    center_pos = (shape[1] // 2, shape[0] * 9 // 20)
    font_path = get_file_path("font.ttf")
    scales = [96, 64, 48, 32, 24, 16]
    auto_scale = 0
    text_cut = regularize_cut(jieba.lcut(text))
    while True:
        font = ImageFont.truetype(font_path, scales[auto_scale])
        img_pil = Image.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        text_wrap = auto_warp(text_cut, font, img_pil)
        if text_wrap is None:
            if auto_scale < len(scales) - 1: auto_scale += 1
            else:
                text_wrap = auto_warp(text_cut, font, img_pil, force = True)
                break
        else: break
    bbox = draw.textbbox(center_pos, text_wrap, font = font, align = "center")
    width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    center_pos = (center_pos[0] - width // 2, center_pos[1] - height // 3)
    draw.text(center_pos, text_wrap, fill = (35, 48, 220), font = font, align = "center")
    img = np.asarray(img_pil)
    img_cny = cv2.Canny(img, 100, 200)
    contour = cv2.findContours(img_cny, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    img_ret = np.ones(shape, dtype = np.uint8) * 255
    cv2.drawContours(img_ret, contour[0], -1, (0, 215, 255), 5)
    img_ret = multiply_image(img, img_ret)
    return img_ret

def put_text(img: np.ndarray, text: str, is_gray: bool) -> np.ndarray:
    text = text[:10000]
    text_mask = get_text_mask(text, img)
    if is_gray:
        text_mask = cv2.cvtColor(text_mask, cv2.COLOR_BGR2GRAY)
        text_mask = cv2.cvtColor(text_mask, cv2.COLOR_GRAY2BGR)
    img = overlay_image(text_mask, img)
    return img

async def draw_good_news(text: str) -> Message:
    good_news_image = cv2.imread(get_file_path("xi_bao.webp"))
    good_news_image = put_text(good_news_image, text, is_gray = False)
    cv2.imwrite(get_file_path("good_news.png"), good_news_image)
    return Message([MessageSegment.image("file:///" + get_file_path("good_news.png"))])

async def draw_bad_news(text: str) -> Message:
    bad_news_image = cv2.imread(get_file_path("bei_bao.webp"))
    bad_news_image = put_text(bad_news_image, text, is_gray = True)
    cv2.imwrite(get_file_path("bad_news.png"), bad_news_image)
    return Message([MessageSegment.image("file:///" + get_file_path("bad_news.png"))])