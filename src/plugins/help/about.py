import sys, psutil, platform, cpuinfo, winreg
from PIL import Image, ImageDraw
from utils import global_plugin_ctrl
from utils.utils import get_asset_path, get_output_path, get_copyright_str
from utils.fonts import get_font
from nonebot.adapters.onebot.v11.message import MessageSegment

def generate_bot_status_image(bot_name="Furina Bot"):
    avatar_path = get_asset_path("images/avatar.jpg")
    icon_path = get_asset_path("images/icon.png")
    def get_windows_detailed_version():
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                product_name = winreg.QueryValueEx(key, "ProductName")[0]
                release_id   = winreg.QueryValueEx(key, "ReleaseId")[0]
                build_number = winreg.QueryValueEx(key, "CurrentBuildNumber")[0]
                ubr          = winreg.QueryValueEx(key, "UBR")[0]
                return f"{product_name} {release_id} {build_number}.{ubr}"
        except:
            sys_info = platform.uname()
            return sys_info.system + ' ' + sys_info.release
    system_info_str = get_windows_detailed_version()
    info_cpu = cpuinfo.get_cpu_info()
    cpu_model_str = info_cpu.get('brand_raw', 'Unknown CPU')
    try:
        import nonebot
        nonebot_version = nonebot.__version__
    except ImportError:
        nonebot_version = "NoneBot N/A"
    python_version = sys.version.split()[0]
    combined_version_str = f"Python {python_version} x NoneBot {nonebot_version}"
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_usage = cpu_percent / 100.0
    cpu_freq = psutil.cpu_freq()
    if cpu_freq is not None:
        current_ghz = cpu_freq.current / 1000.0
        cpu_core_count = psutil.cpu_count(logical=False) or "?"
        cpu_speed_str = f"{current_ghz:.1f}Ghz [{cpu_core_count}core]" if isinstance(cpu_core_count, int) else f"{current_ghz:.1f}Ghz"
    else: cpu_speed_str = "Unknown Speed"
    mem = psutil.virtual_memory()
    mem_used_gb, mem_total_gb = mem.used / (1024**3), mem.total / (1024**3)
    swap = psutil.swap_memory()
    swap_used_gb, swap_total_gb = swap.used / (1024**3), swap.total / (1024**3)
    disk = psutil.disk_usage("/")
    disk_used_gb, disk_total_gb = disk.used / (1024**3), disk.total / (1024**3)
    plugins_loaded = len(global_plugin_ctrl.plugin_list)
    img_width, img_height = 1600, 2000
    base_img = Image.new("RGBA", (img_width, img_height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(base_img)
    font_title = get_font("yahei-consolas", 80)
    font_bold  = get_font("yahei-consolas", 64)
    font_normal = get_font("yahei-consolas", 56)
    font_copyright = get_font("yahei-consolas", 36)
    top_margin = 100
    avatar_size = 240
    avatar_center_margin = 40 
    def create_circular_avatar(path, size):
        avatar_img = Image.open(path).convert("RGBA").resize((size, size))
        mask = Image.new("L", (size, size), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, size, size), fill=255)
        avatar_img.putalpha(mask)
        return avatar_img
    avatar_x = (img_width - avatar_size) // 2
    avatar_y = top_margin
    ring_color = (112, 194, 255)
    ring_width = 10
    center_x = avatar_x + avatar_size // 2
    center_y = avatar_y + avatar_size // 2
    ring_radius = avatar_size // 2 + 15
    draw.ellipse(
        (center_x - ring_radius, center_y - ring_radius, center_x + ring_radius, center_y + ring_radius), outline=ring_color, width=ring_width)
    avatar_img = create_circular_avatar(avatar_path, avatar_size)
    base_img.paste(avatar_img, (avatar_x, avatar_y), avatar_img)
    bbox_bot_name = draw.textbbox((0, 0), bot_name, font=font_title)
    w_name = bbox_bot_name[2] - bbox_bot_name[0]
    h_name = bbox_bot_name[3] - bbox_bot_name[1]
    name_x = (img_width - w_name) // 2
    name_y = avatar_y + avatar_size + avatar_center_margin
    draw.text((name_x, name_y), bot_name, font=font_title, fill=(50, 50, 50))
    current_y = name_y + h_name + 80
    color_cpu  = (112, 194, 255)
    color_mem  = (255, 153, 153)
    color_swap = (255, 182, 113)
    color_disk = (179, 179, 179)
    color_bg_ring = (220, 220, 220)
    bar_height = 240
    radius = 90
    ring_thickness = 9
    icon_size = 150
    left_margin = 240
    right_margin = 900
    usage_data = [
        ("CPU", cpu_usage, cpu_speed_str, color_cpu, f"{cpu_percent:.1f}%"),
        ("RAM", mem_used_gb / mem_total_gb, f"{mem_used_gb:.2f}/{mem_total_gb:.2f} GB",
         color_mem, f"{(mem_used_gb/mem_total_gb)*100:.1f}%"),
        ("SWAP", swap_used_gb / swap_total_gb, f"{swap_used_gb:.2f}/{swap_total_gb:.2f} GB",
         color_swap, f"{(swap_used_gb/swap_total_gb)*100:.1f}%"),
        ("DISK", disk_used_gb / disk_total_gb, f"{disk_used_gb:.2f}/{disk_total_gb:.2f} GB",
         color_disk, f"{(disk_used_gb/disk_total_gb)*100:.1f}%")
    ]
    def draw_ring(draw_obj, center, r, thickness, percent, ring_color, bg_color):
        left_up_point    = (center[0] - r, center[1] - r)
        right_down_point = (center[0] + r, center[1] + r)
        draw_obj.arc([left_up_point, right_down_point], 0, 360, fill=bg_color, width=thickness)
        start_angle = -90
        end_angle   = start_angle + 360 * percent
        draw_obj.arc([left_up_point, right_down_point], start_angle, end_angle, fill=ring_color, width=thickness)
    try:
        icon_img = Image.open(icon_path).convert("RGBA").resize((icon_size, icon_size))
    except:
        icon_img = None
    for label, percent, usage_str, color_bar, percent_str in usage_data:
        ring_center = (left_margin + radius, current_y + bar_height // 2)
        draw_ring(draw, ring_center, radius, ring_thickness, percent, color_bar, color_bg_ring)
        if icon_img is not None:
            icon_x = ring_center[0] - icon_size // 2
            icon_y = ring_center[1] - icon_size // 2
            base_img.paste(icon_img, (icon_x, icon_y), icon_img)
        line1_bbox = draw.textbbox((0, 0), usage_str, font=font_normal)
        line1_height = line1_bbox[3] - line1_bbox[1]
        draw.text((right_margin, current_y + 60), usage_str, font=font_normal, fill=(50, 50, 50))
        second_line_y = current_y + 60 + line1_height + 20
        draw.text((right_margin, second_line_y), f"({percent_str})", font=font_normal, fill=(120, 120, 120))
        label_bbox = draw.textbbox((0, 0), label, font=font_bold)
        label_height = label_bbox[3] - label_bbox[1]
        label_x = left_margin + 2 * radius + 40
        label_y = current_y + (bar_height - label_height) // 2 - 20
        draw.text((label_x, label_y), label, font=font_bold, fill=(50, 50, 50))
        current_y += bar_height
    current_y += 60
    info_texts = [f"CPU: {cpu_model_str}", f"System: {system_info_str}", f"Version: {combined_version_str}", f"Plugins: {plugins_loaded} loaded"]
    line_spacing = 20
    for info in info_texts:
        bbox_info = draw.textbbox((0, 0), info, font=font_normal)
        info_height = bbox_info[3] - bbox_info[1]
        draw.text((left_margin - 100, current_y), info, font=font_normal, fill=(0, 0, 0))
        current_y += info_height + line_spacing
    draw.text((40, img_height - 60), get_copyright_str(), fill=(0, 0, 0, 255), font = font_copyright)
    out_path = get_output_path("about")
    base_img = base_img.convert("RGB")
    base_img.save(out_path)
    return MessageSegment.image(f"file:///{out_path}")