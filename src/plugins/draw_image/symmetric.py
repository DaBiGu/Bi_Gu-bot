from PIL import Image
import os
from nonebot.adapters.onebot.v11.message import MessageSegment

def symmetric_left(original_image_path: str):
    original_image = Image.open(original_image_path)
    width, height = original_image.size
    left = original_image.crop((0, 0, width // 2, height))
    flipped_left = left.transpose(Image.FLIP_LEFT_RIGHT)
    symmetric_left = Image.new("RGB", (width, height))
    symmetric_left.paste(left, (0, 0))
    symmetric_left.paste(flipped_left, (width // 2, 0))
    symmetric_left.save(os.path.join(os.getcwd(), "src/data/draw_image/symmetric_left.png"))
    return MessageSegment.image("file:///" + os.path.join(os.getcwd(), "src/data/draw_image/symmetric_left.png"))

def symmetric_right(original_image_path: str):
    original_image = Image.open(original_image_path)
    width, height = original_image.size
    right = original_image.crop((width // 2, 0, width, height))
    flipped_right = right.transpose(Image.FLIP_LEFT_RIGHT)
    symmetric_right = Image.new("RGB", (width, height))
    symmetric_right.paste(flipped_right, (0, 0))
    symmetric_right.paste(right, (width // 2, 0))
    symmetric_right.save(os.path.join(os.getcwd(), "src/data/draw_image/symmetric_right.png"))
    return MessageSegment.image("file:///" + os.path.join(os.getcwd(), "src/data/draw_image/symmetric_right.png"))