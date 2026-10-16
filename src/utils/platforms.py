import os, platform, sys

def get_platform() -> str:
    if sys.platform == "win32": return "windows"
    if sys.platform == "darwin": return "macos"
    if sys.platform.startswith("linux"): return "linux"
    return "unknown"

def restart_argv(pid = None):
    if get_platform() != "windows": return None
    argv = [os.path.join(os.getcwd(), "run.bat")]
    if pid is not None: argv.append(str(pid))
    return argv

def restart_hint() -> str:
    return "run.bat" if get_platform() == "windows" else "systemd (Restart=always)"

def windows_version_string():
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
            product_name = winreg.QueryValueEx(key, "ProductName")[0]
            release_id = winreg.QueryValueEx(key, "ReleaseId")[0]
            build_number = winreg.QueryValueEx(key, "CurrentBuildNumber")[0]
            ubr = winreg.QueryValueEx(key, "UBR")[0]
        return f"{product_name} {release_id} {build_number}.{ubr}"
    except Exception:
        return None

def linux_version_string():
    try:
        data = {}
        with open("/etc/os-release", encoding = "utf-8") as f:
            for line in f:
                key, sep, value = line.strip().partition("=")
                if sep: data[key.strip()] = value.strip().strip('"').strip("'")
        return f"{data.get('PRETTY_NAME') or data.get('NAME') or 'Linux'} {platform.release()}"
    except Exception:
        return None

def system_info_string() -> str:
    current = get_platform()
    if current == "windows": result = windows_version_string()
    elif current == "linux": result = linux_version_string()
    else: result = None
    if result: return result
    info = platform.uname()
    return f"{info.system} {info.release}"

def python_executable() -> str:
    return sys.executable or "python"
