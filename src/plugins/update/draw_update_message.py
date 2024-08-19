from PIL import Image, ImageDraw, ImageFont
import datetime, os
from nonebot.adapters.onebot.v11 import MessageSegment

def draw_update_message(message: str) -> MessageSegment:
    background_color = (255, 255, 255) 
    font = ImageFont.truetype(os.getcwd() + "/src/data/update/source/RobotoMono-Regular.ttf", 36)
    _font = ImageFont.truetype(os.getcwd() + "/src/data/update/source/NotoSansCJK-Regular.ttc", 30)
    _draw = ImageDraw.Draw(Image.new("RGB", (1, 1), background_color))
    text_bbox = _draw.textbbox((0, 0), message, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    canvas_width, canvas_height = text_width + 400, text_height + 300
    canvas = Image.new("RGB", (canvas_width, canvas_height), background_color)
    draw = ImageDraw.Draw(canvas)
    draw.text((200, 100), message, font=font, fill=(0, 0, 0))  
    draw.text((40, canvas_height-50), "\u00A9" + f" Generated by Bi_Gu-bot at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fill=(0, 0, 0, 0), font=_font)

    output_path = os.getcwd() + f"/src/data/update/output/update_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    canvas.save(output_path)
    return MessageSegment.image("file:///" + output_path)