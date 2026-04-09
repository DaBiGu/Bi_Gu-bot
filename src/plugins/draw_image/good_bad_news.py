import cv2
import numpy as np
from PIL import ImageDraw, Image
from utils.fonts import get_font
from utils.utils import get_output_path, get_asset_path
from utils.text_layout import pick_font_and_wrap_by_width
from nonebot.adapters.onebot.v11.message import Message, MessageSegment

def multiply_image(img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
    return ((img1/255) * (img2/255) * 255).astype(np.uint8)

def overlay_image(upper: np.ndarray, lower: np.ndarray) -> np.ndarray:
    upper_gray = cv2.cvtColor(upper, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(upper_gray, 254, 255, cv2.THRESH_BINARY_INV)
    mask_inv = cv2.bitwise_not(mask)
    upper_fg = cv2.bitwise_and(upper, upper, mask = mask)
    lower_bg = cv2.bitwise_and(lower, lower, mask = mask_inv)
    return cv2.add(upper_fg, lower_bg)

def get_text_mask(text: str, img: np.ndarray) -> np.ndarray:
    shape = img.shape
    img = np.ones(shape, dtype = np.uint8) * 255
    center_pos = (shape[1] // 2, shape[0] * 9 // 20)
    scales = [96, 64, 48, 32, 24, 16]
    img_pil = Image.fromarray(img)
    draw = ImageDraw.Draw(img_pil)
    font, lines, line_gap, line_height = pick_font_and_wrap_by_width(
        text, draw, get_font, "xi_bei-bao", scales,
        max_width = 3 * img_pil.size[0] // 4,
        max_lines = 12, use_jieba = True,
        line_gap = 0, max_text_height = 550, min_font_size = 16,
    )

    text_h = len(lines) * line_height + (len(lines) - 1) * line_gap
    y = center_pos[1] - text_h // 3
    for line in lines:
        line_w = draw.textlength(line, font = font)
        draw.text((center_pos[0] - line_w // 2, y), line, fill = (35, 48, 220), font = font)
        y += line_height + line_gap

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
    good_news_image = cv2.imread(get_asset_path("images/xi_bao.webp"))
    good_news_image = put_text(good_news_image, text, is_gray = False)
    output_path = get_output_path("good_news")
    cv2.imwrite(output_path, good_news_image)
    return Message([MessageSegment.image("file:///" + output_path)])

async def draw_bad_news(text: str) -> Message:
    bad_news_image = cv2.imread(get_asset_path("images/bei_bao.webp"))
    bad_news_image = put_text(bad_news_image, text, is_gray = True)
    output_path = get_output_path("bad_news")
    cv2.imwrite(output_path, bad_news_image)
    return Message([MessageSegment.image("file:///" + output_path)])