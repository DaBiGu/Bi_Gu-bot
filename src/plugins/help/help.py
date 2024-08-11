from PIL import Image, ImageDraw, ImageFont
import datetime, os
from nonebot.adapters.onebot.v11 import MessageSegment

def draw_help(helper_message: str):
    image_path = os.getcwd() + '/src/data/help/background.png'
    original_image = Image.open(image_path).convert("RGBA")

    opacity = 160
    alpha = original_image.split()[3]
    alpha = Image.eval(alpha, lambda x: int(x * opacity / 255))
    original_image.putalpha(alpha)

    white_layer = Image.new('RGBA', original_image.size, (255, 255, 255, 0))
    white_opacity = 160
    white_alpha = white_layer.split()[3]
    white_alpha = Image.eval(white_alpha, lambda x: white_opacity)
    white_layer.putalpha(white_alpha)

    combined_image = Image.alpha_composite(original_image, white_layer)

    draw = ImageDraw.Draw(combined_image)
    font_size = 18

    font = ImageFont.truetype(os.getcwd() + '/src/data/help/font.ttf', font_size)
 
    width, height = original_image.size
    draw.text((40, 20), helper_message, fill=(0, 0, 0, 255), font=font)
    draw.text((40, height-50), "\u00A9" + f" Generated by Bi_Gu-bot at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  |  Page 1 of 1", fill=(0, 0, 0, 255), font=font)

    combined_image.save(os.getcwd() + "/src/data/help/help.png")
    return MessageSegment.image('file:///' + os.getcwd() + "/src/data/help/help.png")