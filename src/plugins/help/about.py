import sys, psutil, os, cpuinfo, datetime, json, requests
from typing import Optional, Dict, Any, Tuple
from utils import global_plugin_ctrl
from utils.utils import get_asset_path, get_output_path, get_copyright_str, get_IO_path, load_asset_html
from utils.platforms import system_info_string
from utils.chrome import Chrome, file_url
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.message import event_preprocessor
from nonebot import get_driver
from nonebot.adapters.onebot.v11.message import MessageSegment
import matplotlib.pyplot as plt
import html as html_utils

json_path = get_IO_path("bot_status", "json")

nonebot_runtime = datetime.datetime.now()
bot_connect_time = {}
receive_message_count = {}
send_message_count = {}
psutil.cpu_percent(interval = None)

driver = get_driver()

@driver.on_bot_connect
async def on_connect(bot: Bot):
    bot_connect_time[bot.self_id] = datetime.datetime.now()
    if bot.self_id not in receive_message_count: receive_message_count[bot.self_id] = 0
    if bot.self_id not in send_message_count: send_message_count[bot.self_id] = 0

@driver.on_bot_disconnect
async def on_disconnect(bot: Bot):
    session_delta = datetime.datetime.now() - bot_connect_time[bot.self_id]
    with open(json_path, "r") as f: data = json.load(f)
    if bot.self_id not in data: data[bot.self_id] = {"total_run_seconds": 0, "total_received": 0, "total_sent": 0}
    data[bot.self_id]["total_run_seconds"] += session_delta.total_seconds()
    data[bot.self_id]["total_received"] += receive_message_count[bot.self_id]
    data[bot.self_id]["total_sent"] += send_message_count[bot.self_id]
    with open(json_path, "w") as f: json.dump(data, f)
    bot_connect_time.pop(bot.self_id)
    receive_message_count.pop(bot.self_id)
    send_message_count.pop(bot.self_id)

@event_preprocessor
async def check_receive(bot: Bot, event: Event):
    if event.get_type() == "message":
        receive_message_count[bot.self_id] += 1

@Bot.on_called_api
async def check_send(bot: Bot, exception: Optional[Exception], api: str, data: Dict[str, Any], result: Any):
    if api == "send_msg" or "send_group_msg":
        send_message_count[bot.self_id] += 1

def get_brief_bot_status(bot_id: str) -> Tuple[str, str, str]:
    with open(json_path, "r") as f: history_data = json.load(f)
    if bot_id not in history_data: history_data[bot_id] = {"total_run_seconds": 0, "total_received": 0, "total_sent": 0}
    session_run_secs = (datetime.datetime.now() - bot_connect_time[bot_id]).total_seconds() if bot_id in bot_connect_time else 0
    total_run_secs = history_data[bot_id]["total_run_seconds"] + session_run_secs
    total_received = history_data[bot_id]["total_received"] + receive_message_count.get(bot_id, 0)
    total_sent     = history_data[bot_id]["total_sent"] + send_message_count.get(bot_id, 0)
    total_run_td = datetime.timedelta(seconds=total_run_secs)
    session_run_td = datetime.timedelta(seconds=session_run_secs)
    days, seconds = total_run_td.days, total_run_td.seconds
    _days, _seconds = session_run_td.days, session_run_td.seconds
    hours, minutes, secs = seconds // 3600, (seconds % 3600) // 60, seconds % 60  
    _hours, _minutes, _secs = _seconds // 3600, (_seconds % 3600) // 60, _seconds % 60      
    line_total_connect = f"Since Dec 29 2024 running for {days}d {hours}h {minutes}m {secs}s" if days > 0 \
                else f"Since Dec 29 2024 running for {hours}h {minutes}m {secs}s"
    line_session_connect = f"Current session running for {_days}d {_hours}h {_minutes}m {_secs}s" if _days > 0 \
                else f"Current session running for {_hours}h {_minutes}m {_secs}s"
    line_msgs = f"Received: {total_received}  |  Sent: {total_sent}"
    return line_total_connect, line_session_connect, line_msgs

def get_about_image():
    request_url = "https://socialify.git.ci/DaBiGu/Bi_Gu-bot/png?description=1&font=Jost&logo=https://s21.ax1x.com/2024/12/29/pAxNAKS.jpg&name=1&owner=1&pattern=Plus&stargazers=1&theme=Dark"
    output_path = get_output_path("about")
    with open(output_path, "wb") as file: file.write(requests.get(request_url).content)
    return MessageSegment.image(f"file:///{output_path}")

_METRIC_ICONS = {
    "cpu": '<svg class="ring-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><rect x="7" y="7" width="10" height="10" rx="2"/><path d="M9 3v2M15 3v2M9 19v2M15 19v2M3 9h2M3 15h2M19 9h2M19 15h2"/></svg>',
    "ram": '<svg class="ring-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><rect x="2" y="8" width="20" height="9" rx="2"/><path d="M6 17v3M10 17v3M14 17v3M18 17v3"/></svg>',
    "swap": '<svg class="ring-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 8h13l-3.5-3.5"/><path d="M20 16H7l3.5 3.5"/></svg>',
    "disk": '<svg class="ring-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="2.6"/></svg>',
}

async def generate_bot_status_image(bot_id: str, bot_name="Furina Bot") -> MessageSegment:
    template, css = load_asset_html("status_card")
    avatar_path = get_asset_path("images/avatar.jpg")
    avatar_url = file_url(avatar_path) if os.path.exists(avatar_path) else ""
    furina_path = get_asset_path("images/furina_full.png")
    furina_url = file_url(furina_path) if os.path.exists(furina_path) else ""
    system_info_str = system_info_string()
    info_cpu = cpuinfo.get_cpu_info()
    cpu_model_str = info_cpu.get("brand_raw", "Unknown CPU")
    try:
        import nonebot
        nonebot_version = nonebot.__version__
    except ImportError:
        nonebot_version = "NoneBot N/A"
    combined_version_str = f"Python {sys.version.split()[0]} x NoneBot {nonebot_version}"

    cpu_percent = psutil.cpu_percent(interval=None)
    cpu_freq = psutil.cpu_freq()
    if cpu_freq is not None:
        cpu_core_count = psutil.cpu_count(logical=False) or "?"
        cpu_speed_str = (f"{cpu_freq.current / 1000.0:.1f} GHz · {cpu_core_count} cores"
                         if isinstance(cpu_core_count, int) else f"{cpu_freq.current / 1000.0:.1f} GHz")
    else:
        cpu_speed_str = "Unknown Speed"

    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    disk = psutil.disk_usage("/")
    mem_used_gb, mem_total_gb = mem.used / (1024 ** 3), mem.total / (1024 ** 3)
    swap_used_gb, swap_total_gb = swap.used / (1024 ** 3), swap.total / (1024 ** 3)
    disk_used_gb, disk_total_gb = disk.used / (1024 ** 3), disk.total / (1024 ** 3)
    plugins_loaded = len(global_plugin_ctrl.plugin_list)

    def usage_percent(used: float, total: float) -> float:
        return (used / total * 100.0) if total else 0.0

    line_total_connect, line_session_connect, line_msgs = get_brief_bot_status(bot_id)
    status_lines = "\n".join(
        f'            <div class="status-line">{html_utils.escape(text)}</div>'
        for text in (line_total_connect, line_session_connect, line_msgs)
    )

    metrics = [
        ("CPU",  cpu_percent,                          cpu_speed_str,                                 "cpu"),
        ("RAM",  usage_percent(mem.used, mem.total),   f"{mem_used_gb:.2f} / {mem_total_gb:.2f} GB",   "ram"),
        ("SWAP", usage_percent(swap.used, swap.total), f"{swap_used_gb:.2f} / {swap_total_gb:.2f} GB", "swap"),
        ("DISK", usage_percent(disk.used, disk.total), f"{disk_used_gb:.2f} / {disk_total_gb:.2f} GB", "disk"),
    ]
    metric_cards = "\n".join(
        '            <div class="metric">\n'
        f'                <div class="ring" style="--ring-color: var(--{kind}); --pct: {value:.1f};">{_METRIC_ICONS[kind]}</div>\n'
        '                <div class="metric-body">\n'
        '                    <div class="metric-head">\n'
        f'                        <span class="metric-label">{label}</span>\n'
        f'                        <span class="metric-pct">{value:.1f}%</span>\n'
        '                    </div>\n'
        f'                    <div class="metric-detail">{html_utils.escape(detail)}</div>\n'
        '                </div>\n'
        '            </div>'
        for label, value, detail, kind in metrics
    )

    spec_rows = "\n".join(
        f'            <div class="spec-row"><span class="spec-key">{key}</span>'
        f'<span class="spec-val">{html_utils.escape(value)}</span></div>'
        for key, value in (
            ("CPU", cpu_model_str),
            ("System", system_info_str),
            ("Version", combined_version_str),
            ("Plugins", f"{plugins_loaded} loaded"),
        )
    )

    html_content = (
        template
        .replace("{{STYLE_BLOCK}}", f"<style>\n{css}\n</style>")
        .replace("{{AVATAR_URL}}", avatar_url)
        .replace("{{FURINA_URL}}", furina_url)
        .replace("{{BOT_NAME}}", html_utils.escape(bot_name))
        .replace("{{STATUS_LINES}}", status_lines)
        .replace("{{METRIC_CARDS}}", metric_cards)
        .replace("{{SPEC_ROWS}}", spec_rows)
        .replace("{{FOOTER}}", html_utils.escape(get_copyright_str()))
    )

    output_path = get_output_path("status")
    async with Chrome() as chrome:
        await chrome.screenshot_html(html_content, output_path, root_id="card-root")
    return MessageSegment.image(f"file:///{output_path}")

def draw_funccount_bargraph() -> MessageSegment:
    with open(get_IO_path("funccount", "json"), "r") as f: data = json.load(f)
    cumulative_data = {}
    for day, features in data.items():
        for feature, count in features.items():
            cumulative_data[feature] = cumulative_data.get(feature, 0) + count
    sorted_features = sorted(cumulative_data.items(), key=lambda x: x[1], reverse=True)[:20][::-1]
    features_sorted, values_sorted = zip(*sorted_features)
    fig = plt.figure(figsize=(12, 8))
    plt.style.use('default')
    bars = plt.barh(features_sorted, values_sorted, color='black', edgecolor='black')
    for bar in bars: plt.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height() / 2, str(bar.get_width()), ha='left', va='center', fontsize=12, color='black')
    plt.yticks(fontsize=12, color='black')
    plt.xticks(fontsize=12, color='black')
    plt.xlabel("Cumulative Usage", fontsize=14, color='black')
    plt.title("Cumulative Function Usage Over Time", fontsize=16, color='black')
    plt.grid(axis='x', linestyle='--', color='gray', linewidth=0.7, alpha=0.7)
    plt.grid(axis='y', linestyle='--', color='gray', linewidth=0.7, alpha=0.7)

    fig.text(0.2, 0, "\u00A9" + f" Generated by Bi_Gu-bot at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ha='center', fontsize = 12)

    # Displaying the plot
    plt.tight_layout()
    output_path = get_output_path("funccount")
    plt.savefig(output_path, dpi = 300, bbox_inches = "tight")
    return MessageSegment.image("file:///" + output_path)