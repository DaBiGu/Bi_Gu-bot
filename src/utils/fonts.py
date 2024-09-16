import os
from PIL import ImageFont

FONTS = {"noto-sans": os.getcwd() + "/src/assets/fonts/NotoSansCJKsc-VF.otf",
         "yahei-consolas": os.getcwd() + "/src/assets/fonts/YaHei-consolas-hybrid.ttf",
         "xi_bei-bao": os.getcwd() + "/src/assets/fonts/xi_bei_bao.ttf",
         "roboto-mono": os.getcwd() + "/src/assets/fonts/RobotoMono-Regular.ttf",
         "xiaolai": os.getcwd() + "/src/assets/fonts/XiaolaiSC-Regular.ttf"}

def get_font_path(font_name: str) -> str:
    return FONTS[font_name]

def get_font(font_name: str, size: int, weight: int = None) -> ImageFont:
    font = ImageFont.truetype(FONTS[font_name], size)
    if weight: font.set_variation_by_axes([weight])
    return font