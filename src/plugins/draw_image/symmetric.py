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

def symmetric_up(original_image_path: str):
    original_image = Image.open(original_image_path)
    width, height = original_image.size
    up = original_image.crop((0, 0, width, height // 2))
    flipped_up = up.transpose(Image.FLIP_TOP_BOTTOM)
    symmetric_up = Image.new("RGB", (width, height))
    symmetric_up.paste(up, (0, 0))
    symmetric_up.paste(flipped_up, (0, height // 2))
    symmetric_up.save(os.path.join(os.getcwd(), "src/data/draw_image/symmetric_up.png"))
    return MessageSegment.image("file:///" + os.path.join(os.getcwd(), "src/data/draw_image/symmetric_up.png"))

def symmetric_down(original_image_path: str):
    original_image = Image.open(original_image_path)
    width, height = original_image.size
    down = original_image.crop((0, height // 2, width, height))
    flipped_down = down.transpose(Image.FLIP_TOP_BOTTOM)
    symmetric_down = Image.new("RGB", (width, height))
    symmetric_down.paste(flipped_down, (0, 0))
    symmetric_down.paste(down, (0, height // 2))
    symmetric_down.save(os.path.join(os.getcwd(), "src/data/draw_image/symmetric_down.png"))
    return MessageSegment.image("file:///" + os.path.join(os.getcwd(), "src/data/draw_image/symmetric_down.png"))