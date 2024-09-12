import os
from PIL import ImageFont

FONTS = {"noto-sans": os.getcwd() + "/src/utils/fonts/NotoSansCJKsc-VF.otf",
         "yahei-consolas": os.getcwd() + "/src/utils/fonts/YaHei-consolas-hybrid.ttf"}

def get_font(font_name: str, size: int, weight: int = None) -> ImageFont:
    font = ImageFont.truetype(FONTS[font_name], size)
    if weight: font.set_variation_by_axes([weight])
    return font