import datetime, os

def get_copyright_str() -> str:
    return "\u00A9" + f" Generated by Bi_Gu-bot at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

def get_output_path(name: str, temp: bool = False) -> str:
    if temp: return os.getcwd() + f"/src/data/temp/{name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png" 
    return os.getcwd() + f"/src/data/output/{name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

def get_data_path(subpath: str = "", temp: bool = False) -> str:
    if temp: return os.getcwd() + f"/src/data/temp/{subpath}"
    return os.getcwd() + f"/src/data/{subpath}"

def get_IO_path(filename: str, file_type: str) -> str:
    return os.getcwd() + f"/src/data/{file_type}s/{filename}.{file_type}"

def get_asset_path(subpath: str) -> str:
    return os.getcwd() + f"/src/assets/{subpath}"

def second_to_hms(seconds):
    h, r = divmod(seconds, 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}小时{int(m)}分钟{int(s)}秒" 