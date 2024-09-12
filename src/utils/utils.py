import datetime, os

def get_copyright_str() -> str:
    return "\u00A9" + f" Generated by Bi_Gu-bot at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

def get_output_path(name: str, temp: bool = False) -> str:
    if temp: return os.getcwd() + f"/src/data/temp/{name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png" 
    return os.getcwd() + f"/src/data/output/{name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"