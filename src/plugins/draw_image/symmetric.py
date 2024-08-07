from PIL import Image
import os
from nonebot.adapters.onebot.v11.message import MessageSegment

def _symmetric(original_image_path: str, direction: str, percent = 50):
    original_image = Image.open(original_image_path)
    width, height = original_image.size
    _width, _height = int(width * percent / 100), int(height * percent / 100)
    result = Image.new("RGB", (2*_width, height)) if direction in ["left", "right"] else Image.new("RGB", (width, 2*_height))
    if direction == "left":
        left = original_image.crop((0, 0, _width, height))
        result.paste(left, (0, 0))
        result.paste(left.transpose(Image.FLIP_LEFT_RIGHT), (_width, 0))
    elif direction == "right":
        right = original_image.crop((_width, 0, width, height))
        result.paste(right.transpose(Image.FLIP_LEFT_RIGHT), (0, 0))
        result.paste(right, (_width, 0))
    elif direction == "up":
        up = original_image.crop((0, 0, width, _height))
        result.paste(up, (0, 0))
        result.paste(up.transpose(Image.FLIP_TOP_BOTTOM), (0, _height))
    elif direction == "down":
        down = original_image.crop((0, _height, width, height))
        result.paste(down.transpose(Image.FLIP_TOP_BOTTOM), (0, 0))
        result.paste(down, (0, _height))
    result.save(os.path.join(os.getcwd(), f"src/data/draw_image/symmetric_{direction}.png"))
    return MessageSegment.image("file:///" + os.path.join(os.getcwd(), f"src/data/draw_image/symmetric_{direction}.png"))