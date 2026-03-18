from PIL import Image, ImageSequence
from nonebot.adapters.onebot.v11.message import MessageSegment
from utils.utils import get_output_path

def _build_symmetric_frame(image: Image.Image, direction: str, percent: int) -> Image.Image:
    width, height = image.size
    _width, _height = [int(x * percent / 100) for x in image.size]
    result = Image.new("RGBA", (2 * _width, height)) if direction in ["left", "right"] else Image.new("RGBA", (width, 2 * _height))
    if direction in ["left", "right"]:
        image = image.transpose(Image.FLIP_LEFT_RIGHT) if direction == "right" else image
        left = image.crop((0, 0, _width, height))
        result.paste(left, (0, 0))
        result.paste(left.transpose(Image.FLIP_LEFT_RIGHT), (_width, 0))
    elif direction in ["up", "down"]:
        image = image.transpose(Image.FLIP_TOP_BOTTOM) if direction == "down" else image
        up = image.crop((0, 0, width, _height))
        result.paste(up, (0, 0))
        result.paste(up.transpose(Image.FLIP_TOP_BOTTOM), (0, _height))
    return result

async def _symmetric(original_image_path: str, direction: str, percent = 50):
    try:
        original_image = Image.open(original_image_path)
    except Exception:
        return "图片已过期, 请重新发送图片后重试"

    if getattr(original_image, "is_animated", False) and getattr(original_image, "n_frames", 1) > 1:
        frames, durations, disposals = [], [], []
        default_duration = original_image.info.get("duration", 100)
        default_disposal = original_image.info.get("disposal", 2)
        for frame in ImageSequence.Iterator(original_image):
            symmetric_frame = _build_symmetric_frame(frame.convert("RGBA"), direction, percent)
            frames.append(symmetric_frame)
            durations.append(frame.info.get("duration", default_duration))
            disposals.append(frame.info.get("disposal", default_disposal))

        output_path = get_output_path("symmetric").replace(".png", ".gif")
        frames[0].save(
            output_path,
            save_all = True,
            append_images = frames[1:],
            duration = durations,
            loop = original_image.info.get("loop", 0),
            disposal = disposals,
        )
    else:
        result = _build_symmetric_frame(original_image.convert("RGBA"), direction, percent)
        output_path = get_output_path("symmetric")
        result.save(output_path)
    return MessageSegment.image("file:///" + output_path)