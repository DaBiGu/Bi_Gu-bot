from PIL import Image
from nonebot.adapters.onebot.v11.message import MessageSegment
from utils.utils import get_output_path

async def _symmetric(original_image_path: str, direction: str, percent = 50):
    try:
        original_image = Image.open(original_image_path)
    except Exception:
        return "图片已过期, 请重新发送图片后重试"
    width, height = original_image.size
    _width, _height = [int(x * percent / 100) for x in original_image.size]
    result = Image.new("RGB", (2*_width, height)) if direction in ["left", "right"] else Image.new("RGB", (width, 2*_height))
    if direction in ["left", "right"]:
        original_image = original_image.transpose(Image.FLIP_LEFT_RIGHT) if direction == "right" else original_image
        left = original_image.crop((0, 0, _width, height))
        result.paste(left, (0, 0))
        result.paste(left.transpose(Image.FLIP_LEFT_RIGHT), (_width, 0))
    elif direction in ["up", "down"]:
        original_image = original_image.transpose(Image.FLIP_TOP_BOTTOM) if direction == "down" else original_image
        up = original_image.crop((0, 0, width, _height))
        result.paste(up, (0, 0))
        result.paste(up.transpose(Image.FLIP_TOP_BOTTOM), (0, _height))
    output_path = get_output_path("symmetric")
    result.save(output_path)
    return MessageSegment.image("file:///" + output_path)