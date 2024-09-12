from PIL import Image, ImageDraw, ImageFont
import datetime, os
from nonebot.adapters.onebot.v11 import MessageSegment
from utils.fonts import get_font
from utils.utils import get_copyright_str

def draw_update_message(message: str) -> MessageSegment:
    background_color = (255, 255, 255) 
    font = get_font("roboto-mono", size = 36)
    _font = get_font("noto-sans", size = 30, weight = 400)
    _draw = ImageDraw.Draw(Image.new("RGB", (1, 1), background_color))
    text_bbox = _draw.textbbox((0, 0), message, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    canvas_width, canvas_height = text_width + 400, text_height + 300
    canvas = Image.new("RGB", (canvas_width, canvas_height), background_color)
    draw = ImageDraw.Draw(canvas)
    draw.text((200, 100), message, font=font, fill=(0, 0, 0))  
    draw.text((40, canvas_height-50), get_copyright_str(), fill=(0, 0, 0, 0), font=_font)

    output_path = os.getcwd() + f"/src/data/update/output/update_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    canvas.save(output_path)
    return MessageSegment.image("file:///" + output_path)