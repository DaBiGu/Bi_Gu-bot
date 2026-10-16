"""Make OneBot ``file://`` references work when NTQQ runs in a container.

SnowLuma runs the Linux NTQQ inside Docker, mounted with its own volumes
only (``/app/data``, ``/app/.config``, ``/app/.local/share``).  It cannot
see the host filesystem, so a host path such as
``file:///home/ubuntu/Bi_Gu-bot/src/data/temp/x.png`` resolves to ENOENT
inside the container and the send fails with::

    ActionFailed(status='failed', retcode=100, data=None,
                 wording="ENOENT: no such file or directory, stat '...'")

The fix is to read the file on the host and inline it as ``base64://`` so
the container never has to touch the host filesystem.

Windows needs none of this: the native NTQQ shares the filesystem with the
bot, so plain ``file://`` already resolves and we leave it alone.
"""

import base64
import os

from nonebot.adapters.onebot.v11 import MessageSegment

from utils.platforms import get_platform

_INSTALLED_FLAG = "_bigubot_inlines_local_files"


def _to_local_path(file: str) -> str | None:
    """Turn a ``file://`` URI into a local path, or None if it is not one."""
    if not file.startswith("file://"):
        return None
    path = file[len("file://"):]
    # file:///home/x keeps its leading slash, a Windows file://D:/x does not.
    if os.name == "nt" and len(path) > 2 and path[2] == ":":
        path = path[1:]
    return path or None


def _inline(file: str) -> str | None:
    """Return ``base64://...`` for a readable local file, else None.

    Returning None keeps the original value, so an unreadable path still
    fails loudly at the adapter instead of silently sending nothing.
    """
    path = _to_local_path(file)
    if path is None or not os.path.isfile(path):
        return None
    with open(path, "rb") as f: return "base64://" + base64.b64encode(f.read()).decode("ascii")


def install() -> None:
    """Inline local files for every MessageSegment that carries a ``file``.

    No-op on Windows, where ``file://`` already resolves.  Safe to call
    more than once.
    """
    if get_platform() != "linux": return
    if getattr(MessageSegment, _INSTALLED_FLAG, False): return

    for segment_type in ("image", "record"):
        original = getattr(MessageSegment, segment_type).__func__

        def wrapper(cls, file, _original = original, **kwargs):
            if isinstance(file, str):
                inlined = _inline(file)
                if inlined is not None: file = inlined
            return _original(cls, file, **kwargs)

        setattr(MessageSegment, segment_type, classmethod(wrapper))

    setattr(MessageSegment, _INSTALLED_FLAG, True)
