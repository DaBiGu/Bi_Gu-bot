from PIL import Image, ImageDraw
from nonebot.adapters.onebot.v11 import MessageSegment
from utils.fonts import get_font
from utils.utils import get_copyright_str, get_output_path, get_asset_path

def draw_help(helper_message: str, current_page: int, total_pages: int) -> MessageSegment:
    image_path = get_asset_path("images/help_background.png")
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
    main_font = get_font("HYWenHei-65W", size = 18)
    copyright_font = get_font("yahei-consolas", size = 18)
 
    width, height = original_image.size
    draw.text((40, 20), helper_message, fill=(0, 0, 0, 255), font=main_font)
    draw.text((40, height-50), get_copyright_str() + f"  |  Page {current_page} of {total_pages}", fill=(0, 0, 0, 255), font=copyright_font)

    output_path = get_output_path("help")
    combined_image.save(output_path)
    return MessageSegment.image('file:///' + output_path)