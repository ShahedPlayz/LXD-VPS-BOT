# ║         SGM-ORG-LTD-V — Ultimate VPS Bot v6.1 (FIXED)                    ║
# ║              Environment-Aware • Self-Healing • Production               ║
# ║                      Made with ❤️ • by SGM Company                       ║   
# ╚══════════════════════════════════════════════════════════════════════════╝

# ====================================================== IMPORTS ======================================================= 
import discord
from discord.ext import commands
import asyncio

import json
from datetime import datetime, timedelta
import shlex
import logging
import shutil
import os
from typing import Optional, List, Dict, Any
import sqlite3
import random
import traceback
import aiohttp
import time
import re
import sys
# ==================================================== IMPORTS END ===================================================== 

# ==================================================== EMOJI AUTO-MANAGEMENT SYSTEM =====================================================

import base64

class _Console:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'
    CLEAR_LINE = '\033[2K\r'

    @staticmethod
    def _supports_color():
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

    @classmethod
    def _c(cls, code, text):
        return f"{code}{text}{cls.RESET}" if cls._supports_color() else text

    @classmethod
    def header(cls, text):
        sep = "═" * 55
        msg = f"\n{cls._c(cls.CYAN + cls.BOLD, '╔' + sep + '╗')}\n"
        msg += f"{cls._c(cls.CYAN + cls.BOLD, '║')}  {cls._c(cls.CYAN + cls.BOLD, text)}  {cls._c(cls.CYAN + cls.BOLD, '║')}\n"
        msg += f"{cls._c(cls.CYAN + cls.BOLD, '╚' + sep + '╝')}"
        print(msg, flush=True)

    @classmethod
    def step(cls, text):
        print(f"  {cls._c(cls.BLUE + cls.BOLD, '▸')} {cls._c(cls.BOLD, text)}", flush=True)

    @classmethod
    def ok(cls, text):
        print(f"    {cls._c(cls.GREEN, '✔')} {cls._c(cls.GREEN, text)}", flush=True)

    @classmethod
    def warn(cls, text):
        print(f"    {cls._c(cls.YELLOW, '⚠')} {cls._c(cls.YELLOW, text)}", flush=True)

    @classmethod
    def fail(cls, text):
        print(f"    {cls._c(cls.RED, '✘')} {cls._c(cls.RED, text)}", flush=True)

    @classmethod
    def info(cls, text):
        print(f"    {cls._c(cls.DIM, '·')} {cls._c(cls.DIM, text)}", flush=True)

    @classmethod
    def progress(cls, current, total, text):
        pct = current / total * 100 if total else 0
        bar_len = 25
        filled = int(bar_len * current / total) if total else 0
        bar = cls._c(cls.GREEN, '█' * filled) + cls._c(cls.DIM, '░' * (bar_len - filled))
        print(f"{cls.CLEAR_LINE}    {bar} {cls._c(cls.BOLD, f'{current}/{total}')}  {text}", end='', flush=True)

    @classmethod
    def progress_done(cls):
        print(flush=True)

EMOJI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "emojis")

EMOJI_FILES = {
    "admin": ("admin.png", "png"),
    "almalinux": ("almalinux.png", "png"),
    "arrow_right": ("arrow_right.webp", "webp"),
    "bad_signal": ("bad_signal.png", "png"),
    "bot": ("bot.png", "png"),
    "cpu": ("cpu.webp", "webp"),
    "cross": ("cross.PNG", "PNG"),
    "debian": ("debian.png", "png"),
    "disk": ("disk.webp", "webp"),
    "epxstar": ("epxstar.gif", "gif"),
    "fedora": ("fedora.png", "png"),
    "folder": ("folder.png", "png"),
    "global": ("global.png", "png"),
    "good_signal": ("good_signal.png", "png"),
    "help": ("help.png", "png"),
    "info": ("info.png", "png"),
    "loading": ("loading.gif", "gif"),
    "lock": ("lock.png", "png"),
    "mainadmin": ("mainadmin.png", "png"),
    "mid_signal": ("mid_signal.png", "png"),
    "offline": ("offline.png", "png"),
    "online": ("online.png", "png"),
    "ports": ("ports.png", "png"),
    "ram": ("ram.webp", "webp"),
    "reinstall": ("reinstall.png", "png"),
    "rockylinux": ("rockylinux.webp", "webp"),
    "sshx": ("sshx.png", "png"),
    "start": ("start.png", "png"),
    "stats": ("stats.png", "png"),
    "status": ("status.gif", "gif"),
    "stop": ("stop.gif", "gif"),
    "success": ("success.png", "png"),
    "system": ("system.png", "png"),
    "tmate": ("tmate.png", "png"),
    "ubuntu": ("ubuntu.png", "png"),
    "uptime": ("uptime.png", "png"),
    "user": ("user.png", "png"),
    "vps": ("vps.png", "png"),
    "warning": ("warning.png", "png"),
}

EMOJI_BASE_URL = "https://raw.githubusercontent.com/ShahedPlayz/LXD-VPS-BOT/main/EMOJI-DB"
_APPLICATION_ID = None

def _get_emoji_path(emoji_name):
    entry = EMOJI_FILES.get(emoji_name)
    if not entry:
        return None
    return os.path.join(EMOJI_DIR, entry[0])

def _ensure_emoji_dir():
    os.makedirs(EMOJI_DIR, exist_ok=True)

def _get_missing_local_emojis():
    missing = []
    for name, (filename, _) in EMOJI_FILES.items():
        if not os.path.exists(os.path.join(EMOJI_DIR, filename)):
            missing.append(name)
    return missing

async def _get_application_id():
    global _APPLICATION_ID
    if _APPLICATION_ID:
        return _APPLICATION_ID
    headers = {"Authorization": f"Bot {DISCORD_TOKEN}"}
    async with aiohttp.ClientSession() as session:
        _Console.info("Fetching Application ID from Discord...")
        async with session.get("https://discord.com/api/v10/oauth2/applications/@me", headers=headers) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to get application info: {resp.status}")
            app = await resp.json()
            _APPLICATION_ID = app["id"]
    _Console.ok(f"Application ID: {_APPLICATION_ID}")
    return _APPLICATION_ID

async def _download_single_emoji(name):
    filename, _ = EMOJI_FILES[name]
    url = f"{EMOJI_BASE_URL}/{filename}"
    local_path = os.path.join(EMOJI_DIR, filename)
    _ensure_emoji_dir()
    try:
        proc = await asyncio.create_subprocess_exec(
            "curl", "-L", "-s", "-o", local_path, url,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
        if proc.returncode != 0 or not os.path.exists(local_path) or os.path.getsize(local_path) == 0:
            err_msg = stderr.decode().strip() if stderr else "unknown error"
            _Console.fail(f"curl failed for {filename}: {err_msg}")
            return False
        size_kb = os.path.getsize(local_path) / 1024
        _Console.info(f"{filename} ({size_kb:.1f} KB)")
        return True
    except asyncio.TimeoutError:
        _Console.fail(f"Download timed out for {filename}")
        return False
    except Exception as e:
        _Console.fail(f"Download error for {filename}: {e}")
        return False

async def download_all_emojis():
    missing = _get_missing_local_emojis()
    if not missing:
        return True, []
    _Console.step(f"Downloading {len(missing)} emojis from GitHub...")
    failed = []
    total = len(missing)
    for i, name in enumerate(missing, 1):
        _Console.progress(i, total, f"Downloading {EMOJI_FILES[name][0]}...")
        if not await _download_single_emoji(name):
            failed.append(name)
    _Console.progress_done()
    if failed:
        _Console.warn(f"Failed downloads: {', '.join(failed)}")
    else:
        _Console.ok("All emojis downloaded successfully")
    return len(failed) == 0, failed

async def _get_discord_emojis():
    app_id = await _get_application_id()
    headers = {"Authorization": f"Bot {DISCORD_TOKEN}"}
    async with aiohttp.ClientSession() as session:
        _Console.info("Checking existing emojis on Discord...")
        async with session.get(f"https://discord.com/api/v10/applications/{app_id}/emojis", headers=headers) as resp:
            if resp.status != 200:
                err = await resp.text()
                _Console.fail(f"API error {resp.status}: {err}")
                return {}
            data = await resp.json()
            emojis = {e["name"]: e for e in data.get("items", [])}
            _Console.ok(f"Found {len(emojis)}/{len(EMOJI_FILES)} emojis on Discord")
            return emojis

async def _upload_single_emoji(name):
    filename, filetype = EMOJI_FILES[name]
    local_path = os.path.join(EMOJI_DIR, filename)
    if not os.path.exists(local_path):
        _Console.fail(f"Local file missing for {name}")
        return False

    with open(local_path, "rb") as f:
        file_bytes = f.read()
    size_kb = len(file_bytes) / 1024
    if size_kb > 256:
        _Console.warn(f"{filename} is {size_kb:.1f} KB (limit: 256 KB)")

    mime_map = {"png": "image/png", "gif": "image/gif", "webp": "image/webp", "PNG": "image/png"}
    mime = mime_map.get(filetype, f"image/{filetype}")
    data_uri = f"data:{mime};base64,{base64.b64encode(file_bytes).decode()}"

    payload = {"name": name, "image": data_uri}
    app_id = await _get_application_id()
    headers = {"Authorization": f"Bot {DISCORD_TOKEN}", "Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"https://discord.com/api/v10/applications/{app_id}/emojis",
            headers=headers, json=payload
        ) as resp:
            if resp.status in (200, 201):
                _Console.ok(f"{name} ({filename}, {size_kb:.1f} KB)")
                return True
            else:
                err_text = await resp.text()
                _Console.fail(f"{name}: HTTP {resp.status} - {err_text[:200]}")
                return False

async def upload_missing_emojis(discord_emojis=None):
    if discord_emojis is None:
        discord_emojis = await _get_discord_emojis()
    to_upload = [name for name in EMOJI_FILES if name not in discord_emojis]
    if not to_upload:
        return True, []
    _Console.step(f"Uploading {len(to_upload)} emojis to Discord Developer Portal...")
    failed = []
    total = len(to_upload)
    for i, name in enumerate(to_upload, 1):
        _Console.progress(i, total, f"Uploading {EMOJI_FILES[name][0]} as :{name}:...")
        if await _upload_single_emoji(name):
            await asyncio.sleep(0.5)
        else:
            failed.append(name)
    _Console.progress_done()
    if failed:
        _Console.warn(f"Failed uploads: {', '.join(failed)}")
    else:
        _Console.ok("All emojis uploaded to Discord")
    return len(failed) == 0, failed

async def ensure_all_emojis():
    _Console.header("EMOJI AUTO-MANAGEMENT SYSTEM")
    _Console.step("Verifying emojis on Discord Developer Portal...")

    discord_emojis = await _get_discord_emojis()
    missing_from_discord = [name for name in EMOJI_FILES if name not in discord_emojis]

    if not missing_from_discord:
        _Console.ok(f"All {len(EMOJI_FILES)} emojis are present on Discord")
        logger.info(f"All {len(EMOJI_FILES)} emojis already on Discord")
        return True

    _Console.warn(f"{len(missing_from_discord)} emojis missing from Discord")
    _Console.step("Checking local emoji storage...")
    _ensure_emoji_dir()

    missing_local = _get_missing_local_emojis()
    if missing_local:
        _Console.info(f"{len(missing_local)} emojis not found locally")
        await download_all_emojis()
    else:
        _Console.ok("All emoji files present locally")

    _Console.step("Uploading to Discord...")
    ok, failed = await upload_missing_emojis(discord_emojis)

    _Console.step("Running final verification...")
    discord_emojis = await _get_discord_emojis()
    still_missing = [name for name in EMOJI_FILES if name not in discord_emojis]
    if still_missing:
        _Console.fail(f"Still missing after upload: {', '.join(still_missing)}")
        logger.warning(f"Still missing after upload: {', '.join(still_missing)}")
        return False

    _Console.ok(f"All {len(EMOJI_FILES)} emojis verified on Discord!")
    _Console.header("EMOJI SETUP COMPLETE")
    logger.info(f"All {len(EMOJI_FILES)} emojis verified on Discord!")
    return True

async def ensure_emojis_on_startup():
    try:
        ok = await ensure_all_emojis()
        if not ok:
            _Console.warn("Some emojis may be missing, continuing anyway")
            logger.warning("Some emojis may be missing, continuing anyway")
    except Exception as e:
        _Console.fail(f"Emoji management error: {e}")
        logger.error(f"Emoji management error: {e}")

# ==================================================== EMOJI AUTO-MANAGEMENT SYSTEM END =====================================================

# ==================================================== CUSTOM EMOJIS CONFIG =====================================================
_EMOJI_OBJECTS = []

def _emoji(name, animated=False):
    obj = discord.PartialEmoji(name=name, animated=animated)
    _EMOJI_OBJECTS.append(obj)
    return obj

EMOJI_TMATE = _emoji("tmate")
EMOJI_SSHX = _emoji("sshx")
EMOJI_REINSTALL = _emoji("reinstall")
EMOJI_START = _emoji("start")
EMOJI_STOP = _emoji("stop", animated=True)
EMOJI_STATS = _emoji("stats")
EMOJI_VPS = _emoji("vps")
EMOJI_HELP = _emoji("help")
EMOJI_USER = _emoji("user")
EMOJI_BOT = _emoji("bot")
EMOJI_PORTS = _emoji("ports")
EMOJI_SYSTEM = _emoji("system")
EMOJI_ADMIN = _emoji("admin")
EMOJI_MAIN_ADMIN = _emoji("mainadmin")
EMOJI_STAR = _emoji("epxstar", animated=True)
EMOJI_RAM = _emoji("ram")
EMOJI_CPU = _emoji("cpu")
EMOJI_DISK = _emoji("disk")
EMOJI_ONLINE = _emoji("online")
EMOJI_OFFLINE = _emoji("offline")
EMOJI_UBUNTU = _emoji("ubuntu")
EMOJI_DEBIAN = _emoji("debian")
EMOJI_ROCKYLINUX = _emoji("rockylinux")
EMOJI_FEDORA = _emoji("fedora")
EMOJI_STATUS = _emoji("status", animated=True)
EMOJI_UPTIME = _emoji("uptime")
EMOJI_ALMALINUX = _emoji("almalinux")
EMOJI_ARROW_RIGHT = _emoji("arrow_right")
EMOJI_WARNING = _emoji("warning")
EMOJI_LOADING = _emoji("loading", animated=True)
EMOJI_SUCCESS = _emoji("success")
EMOJI_GOOD_SIGNAL = _emoji("good_signal")
EMOJI_BAD_SIGNAL = _emoji("bad_signal")
EMOJI_MID_SIGNAL = _emoji("mid_signal")
EMOJI_INFO = _emoji("info")
EMOJI_CROSS = _emoji("cross")
EMOJI_GLOBAL = _emoji("global")
EMOJI_FOLDER = _emoji("folder")
EMOJI_LOCK = _emoji("lock")


async def fetch_emoji_ids():
    headers = {"Authorization": f"Bot {DISCORD_TOKEN}"}
    async with aiohttp.ClientSession() as session:
        async with session.get("https://discord.com/api/v10/oauth2/applications/@me", headers=headers) as resp:
            app = await resp.json()
            app_id = app["id"]
        async with session.get(f"https://discord.com/api/v10/applications/{app_id}/emojis", headers=headers) as resp:
            data = await resp.json()
            emoji_data = {e["name"]: e for e in data.get("items", [])}
    for obj in _EMOJI_OBJECTS:
        if obj.name in emoji_data:
            e = emoji_data[obj.name]
            obj.id = int(e["id"])
            obj.animated = e.get("animated", False)
        else:
            logger.warning(f"Emoji '{obj.name}' not found in application emojis")
    logger.info(f"Fetched IDs for {sum(1 for o in _EMOJI_OBJECTS if o.id is not None)}/{len(_EMOJI_OBJECTS)} emojis")

# ==================================================== CUSTOM EMOJIS CONFIG END =====================================================

# ==================================================== DYNAMIC OS EMOJI MANAGER =====================================================
OS_EMOJI_MAP = {
    "ubuntu": EMOJI_UBUNTU,
    "debian": EMOJI_DEBIAN,
    "rockylinux": EMOJI_ROCKYLINUX,
    "almalinux": EMOJI_ALMALINUX,
    "fedora": EMOJI_FEDORA,
}

def get_os_emoji(os_name):
    for key, emoji in OS_EMOJI_MAP.items():
        if key in os_name.lower():
            return emoji
    return "🐧"

# ==================================================== DYNAMIC OS EMOJI MANAGER END =====================================================

# ==================================================== BOT CONFIGURATION =====================================================

DISCORD_TOKEN = 'YOUR_BOT_TOKEN'  # Your bot token here
BOT_NAME = 'YOUR_BOT_NAME'  # Bot name
PREFIX = '.'  # Command prefix
MAIN_ADMIN_IDS = [ #===== MAIN ADMINS ======
                  '0000000000000000000'
                 ]

# ============================== IGNORE THESE =========================================
_orig_prepare_cooldowns = getattr(commands.Command, "_prepare_cooldowns", None)
if _orig_prepare_cooldowns is not None:
    def _sgm_prepare_cooldowns(self, ctx):
        try:
            if str(ctx.author.id) in MAIN_ADMIN_IDS:
                return
        except Exception:
            pass
        return _orig_prepare_cooldowns(self, ctx)
    commands.Command._prepare_cooldowns = _sgm_prepare_cooldowns
# ======================================================================================

DEFAULT_STORAGE_POOL = 'quota'  # Preferred LXC storage pool (ZFS, quota-enforced)
FALLBACK_STORAGE_POOL = 'default'  # Used automatically if the quota pool cannot be created
QUOTA_POOL_NAME = 'quota'  # Name of the auto-created, quota-enforced storage pool
QUOTA_POOL_RESERVE_GB = 2  # GiB of the host disk left free for the OS; the rest goes to the pool
QUOTA_POOL_TARGET_FRACTION = 0.98  # Legacy fallback fraction (used only if the disk size is unknown)
DISK_MONITOR_INTERVAL = 5  # Seconds between node disk checks (1 batched request per node)
DISK_FULL_RESET_PERCENT = 90  # Re-arm the "disk full" DM once usage drops below this percent
YOUR_SERVER_IP = '3.110.79.77'  # Your server IP for port forwarding
AUTO_SUSPENDED_VPS_DELETE_TIME = '7d' # Time after which suspended VPS will be automatically deleted (e.g., '7d' for 7 days, '12h' for 12 hours)
AUTO_SUSPENDED_VPS_DELETE_WARN_TIME = '1h' # Time before deletion to warn users about their suspended VPS being deleted (e.g., '1h' for 1 hour, '30m' for 30 minutes)
FREE_PLANS_MAX_VPS = '3'  # Max VPS allowed for free plans use 0 for unlimited
PAID_PLANS_MAX_VPS = '5'  # Max VPS allowed for paid plans use 0 for unlimited
# Thumbnail URL (icon in top right and footer)
THUMBNAIL_URL = "XXXXXXXXXXXX" # SET HERE THUMBNAIL
LOGGIN_CHANNEL = 0000000000000000000 # Channel ID for logging important actions (suspensions, deletions, etc.)
TRACKING_CHANNEL = 0000000000000000000 # Channel ID for tracking invite/boost activity

# Free VPS Plans based on invites/boosts
FREE_VPS_STATUS = 'No' # 'Yes' if you want to enable, 'No' If you want to disable
# Node used for self-service free VPS claims (claimfree).
# Format: FREE_VPS_NODE = ("<ip:port or https://domain.com>", "<api-key>")
#   - endpoint may be an IP:port, a bare domain, or a full https://domain URL.
#     API paths are appended automatically, e.g. https://domain.com/container-info
#   - Leave as ("", "") to require free VPS to stay disabled.
#   - If FREE_VPS_STATUS is enabled, this MUST be set (a node is required).
FREE_VPS_NODE = ("", "")
FREE_VPS_PLANS = {
    'invites': [
        {'name': ' Free Tier I', 'invites': 10, 'ram': 4, 'cpu': 1, 'disk': 20, 'emoji': '🥉', 'time': '1month'},
        {'name': ' Free Tier II', 'invites': 14, 'ram': 8, 'cpu': 2, 'disk': 50, 'emoji': '🥈', 'time': '1month'},
        {'name': ' Free Tier III', 'invites': 16, 'ram': 12, 'cpu': 2, 'disk': 60, 'emoji': '🥇', 'time': '1month'},
        {'name': ' Free Tier IV', 'invites': 22, 'ram': 16, 'cpu': 2, 'disk': 80, 'emoji': '🏆', 'time': '1month'},
        {'name': ' Free Tier V', 'invites': 32, 'ram': 24, 'cpu': 4, 'disk': 100, 'emoji': '💎', 'time': '1month'},
        {'name': ' Free Tier VI', 'invites': 40, 'ram': 32, 'cpu': 6, 'disk': 150, 'emoji': '👑', 'time': '1month'}
    ],
    'boosts': [
        {'name': ' Boost Tier I', 'boosts': 1, 'ram': 6, 'cpu': 1, 'disk': 30, 'emoji': '🌟', 'time': '1month'},
        {'name': ' Boost Tier II', 'boosts': 2, 'ram': 12, 'cpu': 2, 'disk': 60, 'emoji': '🌟🌟', 'time': '1month'},
        {'name': ' Boost Tier III', 'boosts': 3, 'ram': 18, 'cpu': 3, 'disk': 90, 'emoji': '🌟🌟🌟', 'time': '1month'},
        {'name': ' Boost Tier IV', 'boosts': 4, 'ram': 24, 'cpu': 4, 'disk': 120, 'emoji': '⚡', 'time': '1month'},
        {'name': ' Boost Tier V', 'boosts': 5, 'ram': 32, 'cpu': 5, 'disk': 150, 'emoji': '🔥', 'time': '1month'}
    ]
}
# ==================================================== BOT CONFIGURATION END =====================================================

# ==================================================== OS OPTIONS DEFINITION =====================================================
OS_OPTIONS = [
    {"label": " Ubuntu 20.04 LTS", "value": "ubuntu:20.04", "emoji": EMOJI_UBUNTU, "description": "Focal Fossa - Stable LTS"},
    {"label": " Ubuntu 22.04 LTS", "value": "ubuntu:22.04", "emoji": EMOJI_UBUNTU, "description": "Jammy Jellyfish - Current LTS"},
    {"label": " Ubuntu 24.04 LTS", "value": "ubuntu:24.04", "emoji": EMOJI_UBUNTU, "description": "Noble Numbat - Latest LTS"},
    {"label": " Debian 11", "value": "images:debian/11", "emoji": EMOJI_DEBIAN, "description": "Bullseye - Old Stable"},
    {"label": " Debian 12", "value": "images:debian/12", "emoji": EMOJI_DEBIAN, "description": "Bookworm - Current Stable"},
    {"label": " Debian 13", "value": "images:debian/13", "emoji": EMOJI_DEBIAN, "description": "Trixie - Latest Stable"},
    {"label": " Rocky Linux 8", "value": "images:rockylinux/8", "emoji": EMOJI_ROCKYLINUX, "description": "Enterprise Linux"},
    {"label": " Rocky Linux 9", "value": "images:rockylinux/9", "emoji": EMOJI_ROCKYLINUX, "description": "Enterprise Linux"},
    {"label": " AlmaLinux 9", "value": "images:almalinux/9", "emoji": EMOJI_ALMALINUX, "description": "RHEL Compatible"},
    {"label": " Fedora 44", "value": "images:fedora/44", "emoji": EMOJI_FEDORA, "description": "Latest Fedora"},
]

# ==================================================== OS OPTIONS DEFINITION END =====================================================

# ==================================================== IMAGE AVAILABILITY CHECKING =====================================================
AVAILABLE_OS_OPTIONS = None

async def check_image_available(image_alias: str) -> bool:
    proc = await asyncio.create_subprocess_exec(
        "lxc", "image", "info", image_alias,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    try:
        _, stderr = await asyncio.wait_for(proc.communicate(), timeout=10)
        return proc.returncode == 0
    except asyncio.TimeoutError:
        proc.kill()
        return False

async def get_available_os_options():
    global AVAILABLE_OS_OPTIONS
    if AVAILABLE_OS_OPTIONS is not None:
        return AVAILABLE_OS_OPTIONS
    logger.info("Checking available OS images (parallel)...")
    
    async def check(o):
        ok = await check_image_available(o["value"])
        return (o, ok)
    
    results = await asyncio.gather(*[check(o) for o in OS_OPTIONS])
    available = [o for o, ok in results if ok]
    for o, ok in results:
        status = "✓" if ok else "✗"
        logger.info(f"  {status} {o['value']}")
    
    if not available:
        logger.warning("No OS images available! Falling back to all options.")
        available = list(OS_OPTIONS)
    AVAILABLE_OS_OPTIONS = available
    logger.info(f"Available OS options: {len(available)}/{len(OS_OPTIONS)}")
    return available

def get_os_display_name(os_value):
    for o in OS_OPTIONS:
        if o["value"] == os_value:
            return o["label"]
    return os_value

async def ensure_image_available(image_alias: str) -> str:
    """Ensure the image is available locally. Returns the alias to use for creation."""
    proc = await asyncio.create_subprocess_exec(
        "lxc", "image", "info", image_alias,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    try:
        _, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
    except asyncio.TimeoutError:
        proc.kill()
    
    if proc.returncode == 0:
        return image_alias
    
    if not image_alias.startswith("images:"):
        logger.warning(f"Image {image_alias} not found locally, will download during init")
        return image_alias
    
    alias_name = image_alias.replace("images:", "").replace("/", "-")
    local_alias = f"auto-{alias_name}"
    
    proc2 = await asyncio.create_subprocess_exec(
        "lxc", "image", "info", f"local:{local_alias}",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    try:
        _, _ = await asyncio.wait_for(proc2.communicate(), timeout=10)
    except asyncio.TimeoutError:
        proc2.kill()
    if proc2.returncode == 0:
        return local_alias
    
    logger.info(f"Downloading {image_alias} from images.linuxcontainers.org...")
    
    try:
        proc3 = await asyncio.create_subprocess_exec(
            "curl", "-sSL", "--connect-timeout", "10",
            "https://images.linuxcontainers.org/streams/v1/images.json",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await asyncio.wait_for(proc3.communicate(), timeout=15)
        if proc3.returncode != 0:
            raise Exception("Failed to fetch image index")
        
        index = json.loads(stdout)
        products = index.get("products", {})
        
        search = alias_name.replace("-", "/")
        target_product = None
        for pid, pinfo in products.items():
            aliases = pinfo.get("aliases", "")
            if isinstance(aliases, str) and search in aliases.split(","):
                target_product = pid
                break
        
        if not target_product:
            raise Exception(f"No product found for alias {search}")
        
        pinfo = products[target_product]
        versions = pinfo.get("versions", {})
        if not versions:
            raise Exception("No versions found")
        latest_ver = max(versions.keys())
        items = versions[latest_ver].get("items", {})
        
        base_url = "https://images.linuxcontainers.org"
        meta_path = items.get("incus.tar.xz", {}).get("path", "") or items.get("lxd.tar.xz", {}).get("path", "")
        root_path = items.get("root.squashfs", {}).get("path", "") or items.get("root.tar.xz", {}).get("path", "")
        
        if not meta_path or not root_path:
            raise Exception("Required files not found in image metadata")
        
        import tempfile, os
        tmpdir = tempfile.mkdtemp(prefix="lxc-import-")
        
        meta_url = f"{base_url}/{meta_path}"
        root_url = f"{base_url}/{root_path}"
        
        meta_file = os.path.join(tmpdir, "metadata.tar.xz")
        root_file = os.path.join(tmpdir, "rootfs.squashfs")
        
        for url, outfile in [(meta_url, meta_file), (root_url, root_file)]:
            logger.info(f"  Downloading {url.split('/')[-1]}...")
            proc4 = await asyncio.create_subprocess_exec(
                "curl", "-sSL", "--connect-timeout", "15", "--max-time", "120",
                "-o", outfile, url,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            _, _ = await asyncio.wait_for(proc4.communicate(), timeout=130)
            if proc4.returncode != 0:
                raise Exception(f"Failed to download {url}")
        
        proc5 = await asyncio.create_subprocess_exec(
            "lxc", "image", "import", meta_file, root_file, "--alias", local_alias,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(proc5.communicate(), timeout=60)
        if proc5.returncode != 0:
            raise Exception(f"Failed to import image: {stderr.decode()}")
        
        shutil.rmtree(tmpdir, ignore_errors=True)
        logger.info(f"  Imported as {local_alias}")
        return local_alias
        
    except Exception as e:
        logger.error(f"Failed to auto-import {image_alias}: {e}")
        raise Exception(f"Image {image_alias} is not available and auto-import failed: {e}")

# ==================================================== IMAGE AVAILABILITY CHECKING END =====================================================

# ==================================================== LXC CONTAINER HELPERS =====================================================
async def ensure_container_name_available(container_name: str):
    """If a container with this name exists in LXD but not in DB, delete it."""
    proc = await asyncio.create_subprocess_exec(
        "lxc", "info", container_name,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    _, _ = await proc.communicate()
    if proc.returncode != 0:
        return
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT 1 FROM vps WHERE container_name = ?', (container_name,))
    if cur.fetchone() is None:
        logger.warning(f"Orphaned container {container_name} found in LXD but not DB - deleting and recreating")
        await execute_lxc(f"lxc delete {shlex.quote(container_name)} --force")
    conn.close()

# ==================================================== LXC CONTAINER HELPERS END =====================================================

# ==================================================== LOGGING CONFIGURATION =====================================================

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(f'{BOT_NAME.lower()}_vps_bot')

# Check if lxc command is available
if not shutil.which("lxc"):
    logger.warning("LXC not found locally; running in API/node-only mode.")

# ==================================================== LOGGING CONFIGURATION END =====================================================

# ==================================================== DATABASE SETUP =====================================================

def get_db():
    conn = sqlite3.connect('vps.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    
    # Admins table
    cur.execute('''CREATE TABLE IF NOT EXISTS admins (
        user_id TEXT PRIMARY KEY
    )''')
    
    # VPS table with purge_protected column
    cur.execute('''CREATE TABLE IF NOT EXISTS vps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        container_name TEXT UNIQUE NOT NULL,
        plan_name TEXT DEFAULT 'Custom',
        ram TEXT NOT NULL,
        cpu TEXT NOT NULL,
        storage TEXT NOT NULL,
        config TEXT NOT NULL,
        os_version TEXT DEFAULT 'ubuntu:22.04',
        status TEXT DEFAULT 'stopped',
        suspended INTEGER DEFAULT 0,
        whitelisted INTEGER DEFAULT 0,
        purge_protected INTEGER DEFAULT 0,
        suspended_reason TEXT DEFAULT '',
        created_at TEXT NOT NULL,
        shared_with TEXT DEFAULT '[]',
        suspension_history TEXT DEFAULT '[]'
    )''')
    
    # Ensure columns exist
    cur.execute('PRAGMA table_info(vps)')
    info = cur.fetchall()
    columns = [col[1] for col in info]
    if 'os_version' not in columns:
        cur.execute("ALTER TABLE vps ADD COLUMN os_version TEXT DEFAULT 'ubuntu:22.04'")
    if 'plan_name' not in columns:
        cur.execute("ALTER TABLE vps ADD COLUMN plan_name TEXT DEFAULT 'Custom'")
    if 'suspended_reason' not in columns:
        cur.execute("ALTER TABLE vps ADD COLUMN suspended_reason TEXT DEFAULT ''")
    if 'purge_protected' not in columns:
        cur.execute("ALTER TABLE vps ADD COLUMN purge_protected INTEGER DEFAULT 0")
    if 'expires_at' not in columns:
        cur.execute("ALTER TABLE vps ADD COLUMN expires_at TEXT DEFAULT ''")
    if 'timer_paused_at' not in columns:
        cur.execute("ALTER TABLE vps ADD COLUMN timer_paused_at TEXT DEFAULT ''")
    if 'timer_status' not in columns:
        cur.execute("ALTER TABLE vps ADD COLUMN timer_status TEXT DEFAULT ''")
    if 'auto_delete_warned' not in columns:
        cur.execute("ALTER TABLE vps ADD COLUMN auto_delete_warned INTEGER DEFAULT 0")
    if 'disk_full_notified' not in columns:
        cur.execute("ALTER TABLE vps ADD COLUMN disk_full_notified INTEGER DEFAULT 0")
    
    # User stats for free VPS
    cur.execute('''CREATE TABLE IF NOT EXISTS user_stats (
        user_id TEXT PRIMARY KEY,
        invites INTEGER DEFAULT 0,
        boosts INTEGER DEFAULT 0,
        claimed_vps_count INTEGER DEFAULT 0,
        last_updated TEXT
    )''')
    
    # Settings table
    cur.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )''')
    
    # Port allocations table
    cur.execute('''CREATE TABLE IF NOT EXISTS port_allocations (
        user_id TEXT PRIMARY KEY,
        allocated_ports INTEGER DEFAULT 0
    )''')
    
    # Port forwards table
    cur.execute('''CREATE TABLE IF NOT EXISTS port_forwards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        vps_container TEXT NOT NULL,
        vps_port INTEGER NOT NULL,
        host_port INTEGER NOT NULL,
        created_at TEXT NOT NULL
    )''')
    
    # Suspension logs table
    cur.execute('''CREATE TABLE IF NOT EXISTS suspension_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        container_name TEXT NOT NULL,
        user_id TEXT NOT NULL,
        action TEXT NOT NULL,
        reason TEXT,
        admin_id TEXT,
        created_at TEXT NOT NULL
    )''')
    
    # Purge protection logs table
    cur.execute('''CREATE TABLE IF NOT EXISTS purge_protection_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        container_name TEXT NOT NULL,
        user_id TEXT NOT NULL,
        action TEXT NOT NULL,
        admin_id TEXT,
        created_at TEXT NOT NULL
    )''')
    
    # IPv4 SSH Tunnels for persistent pinggy SSH access
    cur.execute('''CREATE TABLE IF NOT EXISTS ipv4_tunnels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        container_name TEXT UNIQUE NOT NULL,
        created_at TEXT NOT NULL,
        triggered_by TEXT DEFAULT ''
    )''')
    # Migration: ensure triggered_by column exists
    cur.execute('PRAGMA table_info(ipv4_tunnels)')
    tunnel_cols = [col[1] for col in cur.fetchall()]
    if 'triggered_by' not in tunnel_cols:
        cur.execute("ALTER TABLE ipv4_tunnels ADD COLUMN triggered_by TEXT DEFAULT ''")
    
    
    # File Manager Tunnels for persistent filebrowser access
    cur.execute('''CREATE TABLE IF NOT EXISTS filemanager_tunnels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        container_name TEXT UNIQUE NOT NULL,
        created_at TEXT NOT NULL,
        triggered_by TEXT DEFAULT '',
        fm_username TEXT DEFAULT '',
        fm_password TEXT DEFAULT ''
    )''')
    
    # Invite tracking tables
    cur.execute('''CREATE TABLE IF NOT EXISTS invite_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        inviter_id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        max_uses INTEGER DEFAULT 0,
        uses INTEGER DEFAULT 0
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS invite_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT,
        inviter_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        user_name TEXT DEFAULT '',
        action TEXT NOT NULL,
        created_at TEXT NOT NULL
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS boost_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        user_name TEXT DEFAULT '',
        action TEXT NOT NULL,
        created_at TEXT NOT NULL
    )''')
    
    # Remote node registry (multi-node API management)
    cur.execute('''CREATE TABLE IF NOT EXISTS nodes (
        node_id TEXT PRIMARY KEY,
        endpoint TEXT NOT NULL,
        api_key TEXT NOT NULL,
        node_name TEXT DEFAULT '',
        added_by TEXT DEFAULT '',
        online INTEGER DEFAULT 0,
        last_snapshot TEXT DEFAULT '',
        last_seen TEXT DEFAULT '',
        added_at TEXT DEFAULT ''
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS node_vps (
        vps_id INTEGER PRIMARY KEY,
        user_id TEXT NOT NULL,
        node_id TEXT NOT NULL,
        container_name TEXT NOT NULL,
        ram TEXT DEFAULT '',
        cpu TEXT DEFAULT '',
        disk TEXT DEFAULT '',
        os_image TEXT DEFAULT 'ubuntu:22.04',
        status TEXT DEFAULT 'running',
        created_at TEXT DEFAULT '',
        expires_at TEXT DEFAULT ''
    )''')
    # Migration: node_vps feature columns (sharing / protection / timers)
    cur.execute('PRAGMA table_info(node_vps)')
    nv_cols = [c[1] for c in cur.fetchall()]
    for col, decl in (
        ('plan_name', "TEXT DEFAULT 'Custom'"),
        ('shared_with', "TEXT DEFAULT '[]'"),
        ('whitelisted', "INTEGER DEFAULT 0"),
        ('purge_protected', "INTEGER DEFAULT 0"),
        ('suspended_reason', "TEXT DEFAULT ''"),
        ('suspension_history', "TEXT DEFAULT '[]'"),
        ('timer_paused_at', "TEXT DEFAULT ''"),
        ('timer_status', "TEXT DEFAULT ''"),
        ('disk_full_notified', "INTEGER DEFAULT 0"),
        ('bandwidth', "TEXT DEFAULT ''"),
        ('ports_enabled', "INTEGER DEFAULT 1"),
        ('auto_delete_warned', "INTEGER DEFAULT 0"),
    ):
        if col not in nv_cols:
            cur.execute(f'ALTER TABLE node_vps ADD COLUMN {col} {decl}')
    
    # Initialize settings
    settings_init = [
        ('maintenance_mode', 'false'),
        ('maintenance_started_by', ''),
        ('maintenance_started_at', ''),
        ('bot_version', '4.1.0'),
        ('bot_status', 'online'),
        ('bot_activity', 'watching'),
        ('bot_activity_name', f'{BOT_NAME} VPS Manager'),
        ('prefix', PREFIX)
    ]
    for key, value in settings_init:
        cur.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (key, value))
    
    conn.commit()
    conn.close()

def get_setting(key: str, default: Any = None):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT value FROM settings WHERE key = ?', (key,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else default

def set_setting(key: str, value: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

def get_vps_data() -> Dict[str, List[Dict[str, Any]]]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM vps')
    rows = cur.fetchall()
    conn.close()
    data = {}
    for row in rows:
        user_id = row['user_id']
        if user_id not in data:
            data[user_id] = []
        vps = dict(row)
        vps['shared_with'] = json.loads(vps['shared_with']) if vps.get('shared_with') else []
        vps['suspension_history'] = json.loads(vps['suspension_history']) if vps.get('suspension_history') else []
        vps['suspended'] = bool(vps['suspended'])
        vps['whitelisted'] = bool(vps['whitelisted'])
        vps['purge_protected'] = bool(vps.get('purge_protected', 0))
        vps['os_version'] = vps.get('os_version', 'ubuntu:22.04')
        vps['plan_name'] = vps.get('plan_name', 'Custom')
        vps['expires_at'] = vps.get('expires_at', '')
        vps['timer_paused_at'] = vps.get('timer_paused_at', '')
        vps['timer_status'] = vps.get('timer_status', '')
        vps['auto_delete_warned'] = bool(vps.get('auto_delete_warned', 0))
        vps['disk_full_notified'] = bool(vps.get('disk_full_notified', 0))
        data[user_id].append(vps)
    return data

def get_admins() -> List[str]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT user_id FROM admins')
    rows = cur.fetchall()
    conn.close()
    return [row['user_id'] for row in rows if row['user_id'] not in MAIN_ADMIN_IDS]

def save_vps_data():
    conn = get_db()
    try:
        cur = conn.cursor()
        for user_id, vps_list in vps_data.items():
            for vps in vps_list:
                shared_json = json.dumps(vps['shared_with'])
                history_json = json.dumps(vps['suspension_history'])
                suspended_int = 1 if vps['suspended'] else 0
                whitelisted_int = 1 if vps.get('whitelisted', False) else 0
                purge_protected_int = 1 if vps.get('purge_protected', False) else 0
                os_ver = vps.get('os_version', 'ubuntu:22.04')
                plan_name = vps.get('plan_name', 'Custom')
                created_at = vps.get('created_at', datetime.now().isoformat())
                suspended_reason = vps.get('suspended_reason', '')
                expires_at = vps.get('expires_at', '')
                timer_paused_at = vps.get('timer_paused_at', '')
                timer_status = vps.get('timer_status', '')
                auto_delete_warned = 1 if vps.get('auto_delete_warned', False) else 0
                disk_full_notified = 1 if vps.get('disk_full_notified', False) else 0
                
                if 'id' not in vps or vps['id'] is None:
                    cur.execute('''INSERT INTO vps (user_id, container_name, plan_name, ram, cpu, storage, config, os_version, status, suspended, whitelisted, purge_protected, suspended_reason, created_at, shared_with, suspension_history, expires_at, timer_paused_at, timer_status, auto_delete_warned, disk_full_notified)
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                (user_id, vps['container_name'], plan_name, vps['ram'], vps['cpu'], vps['storage'], vps['config'],
                                 os_ver, vps['status'], suspended_int, whitelisted_int, purge_protected_int, suspended_reason,
                                 created_at, shared_json, history_json, expires_at, timer_paused_at, timer_status, auto_delete_warned, disk_full_notified))
                    vps['id'] = cur.lastrowid
                else:
                    cur.execute('''UPDATE vps SET user_id = ?, plan_name = ?, ram = ?, cpu = ?, storage = ?, config = ?, os_version = ?, status = ?, suspended = ?, whitelisted = ?, purge_protected = ?, suspended_reason = ?, shared_with = ?, suspension_history = ?, expires_at = ?, timer_paused_at = ?, timer_status = ?, auto_delete_warned = ?, disk_full_notified = ?
                                   WHERE id = ?''',
                                (user_id, plan_name, vps['ram'], vps['cpu'], vps['storage'], vps['config'],
                                 os_ver, vps['status'], suspended_int, whitelisted_int, purge_protected_int, suspended_reason,
                                 shared_json, history_json, expires_at, timer_paused_at, timer_status, auto_delete_warned, disk_full_notified, vps['id']))
        conn.commit()
    finally:
        conn.close()

def save_admin_data():
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute('DELETE FROM admins')
        for admin_id in admin_data['admins']:
            cur.execute('INSERT INTO admins (user_id) VALUES (?)', (admin_id,))
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()

def log_suspension(container_name: str, user_id: str, action: str, reason: str = "", admin_id: str = ""):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''INSERT INTO suspension_logs (container_name, user_id, action, reason, admin_id, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (container_name, user_id, action, reason, admin_id, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def log_purge_protection(container_name: str, user_id: str, action: str, admin_id: str = ""):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''INSERT INTO purge_protection_logs (container_name, user_id, action, admin_id, created_at)
                   VALUES (?, ?, ?, ?, ?)''',
                (container_name, user_id, action, admin_id, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_suspension_logs(container_name: str = None) -> List[Dict]:
    conn = get_db()
    cur = conn.cursor()
    if container_name:
        cur.execute('SELECT * FROM suspension_logs WHERE container_name = ? ORDER BY created_at DESC', (container_name,))
    else:
        cur.execute('SELECT * FROM suspension_logs ORDER BY created_at DESC LIMIT 50')
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_vps_number(container_name: str) -> Optional[int]:
    parts = container_name.rsplit('-', 1)
    if len(parts) > 1 and parts[-1].isdigit():
        return int(parts[-1])
    return None

def get_vps_by_number(user_id: str, vps_number: int) -> Optional[Dict]:
    vps_list = vps_data.get(user_id, [])
    for vps in vps_list:
        if get_vps_number(vps['container_name']) == vps_number:
            return vps
    return None

def get_vps_index_by_number(user_id: str, vps_number: int) -> int:
    vps_list = vps_data.get(user_id, [])
    for i, vps in enumerate(vps_list):
        if get_vps_number(vps['container_name']) == vps_number:
            return i
    return -1

# User stats functions
def get_user_stats(user_id: str) -> Dict[str, Any]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM user_stats WHERE user_id = ?', (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {'user_id': user_id, 'invites': 0, 'boosts': 0, 'claimed_vps_count': 0, 'last_updated': None}

def update_user_stats(user_id: str, invites: int = 0, boosts: int = 0, claimed_vps_count: int = 0):
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute('''INSERT OR REPLACE INTO user_stats 
                   (user_id, invites, boosts, claimed_vps_count, last_updated) 
                   VALUES (?, COALESCE((SELECT invites FROM user_stats WHERE user_id = ?), 0) + ?, 
                           COALESCE((SELECT boosts FROM user_stats WHERE user_id = ?), 0) + ?,
                           COALESCE((SELECT claimed_vps_count FROM user_stats WHERE user_id = ?), 0) + ?,
                           ?)''',
                (user_id, user_id, invites, user_id, boosts, user_id, claimed_vps_count, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()

# ==================================================== DATABASE SETUP END =====================================================

# ==================================================== INVITE/BOOST TRACKING HELPERS =====================================================

async def cache_invites(guild):
    try:
        invites = await guild.invites()
        _invite_cache[guild.id] = {invite.code: invite for invite in invites}
    except Exception as e:
        logger.error(f"Failed to cache invites for guild {guild.id}: {e}")

def get_invite_logs(user_id: str = None) -> List[Dict]:
    conn = get_db()
    cur = conn.cursor()
    if user_id:
        cur.execute('SELECT * FROM invite_logs WHERE inviter_id = ? OR user_id = ? ORDER BY created_at DESC LIMIT 50', (user_id, user_id))
    else:
        cur.execute('SELECT * FROM invite_logs ORDER BY created_at DESC LIMIT 50')
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_boost_logs(user_id: str = None) -> List[Dict]:
    conn = get_db()
    cur = conn.cursor()
    if user_id:
        cur.execute('SELECT * FROM boost_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT 50', (user_id,))
    else:
        cur.execute('SELECT * FROM boost_logs ORDER BY created_at DESC LIMIT 50')
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# ==================================================== INVITE/BOOST TRACKING HELPERS END =====================================================

# ==================================================== PORT FORWARDING FUNCTIONS =====================================================

def get_user_allocation(user_id: str) -> int:
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT allocated_ports FROM port_allocations WHERE user_id = ?', (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0

def get_user_used_ports(user_id: str) -> int:
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM port_forwards WHERE user_id = ?', (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0]

def allocate_ports(user_id: str, amount: int):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute('INSERT OR REPLACE INTO port_allocations (user_id, allocated_ports) VALUES (?, COALESCE((SELECT allocated_ports FROM port_allocations WHERE user_id = ?), 0) + ?)', (user_id, user_id, amount))
        conn.commit()
    finally:
        conn.close()

def deallocate_ports(user_id: str, amount: int):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute('UPDATE port_allocations SET allocated_ports = MAX(0, allocated_ports - ?) WHERE user_id = ?', (amount, user_id))
        conn.commit()
    finally:
        conn.close()

def get_available_host_port() -> Optional[int]:
    used_ports = set()
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT host_port FROM port_forwards')
    for row in cur.fetchall():
        used_ports.add(row[0])
    conn.close()
    for _ in range(100):
        port = random.randint(20000, 50000)
        if port not in used_ports:
            return port
    return None

async def create_port_forward(user_id: str, container: str, vps_port: int) -> Optional[int]:
    host_port = get_available_host_port()
    if not host_port:
        return None
    try:
        await execute_lxc(f"lxc config device add {shlex.quote(container)} tcp_proxy_{host_port} proxy listen=tcp:0.0.0.0:{host_port} connect=tcp:127.0.0.1:{vps_port}")
        await execute_lxc(f"lxc config device add {shlex.quote(container)} udp_proxy_{host_port} proxy listen=udp:0.0.0.0:{host_port} connect=udp:127.0.0.1:{vps_port}")
        conn = get_db()
        try:
            cur = conn.cursor()
            cur.execute('INSERT INTO port_forwards (user_id, vps_container, vps_port, host_port, created_at) VALUES (?, ?, ?, ?, ?)',
                        (user_id, container, vps_port, host_port, datetime.now().isoformat()))
            conn.commit()
        except:
            raise
        finally:
            conn.close()
        return host_port
    except Exception as e:
        logger.error(f"Failed to create port forward: {e}")
        return None

async def remove_port_forward(forward_id: int, is_admin: bool = False) -> tuple[bool, Optional[str]]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT user_id, vps_container, host_port FROM port_forwards WHERE id = ?', (forward_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False, None
    user_id, container, host_port = row
    try:
        cur.execute('DELETE FROM port_forwards WHERE id = ?', (forward_id,))
        conn.commit()
    except Exception as e:
        conn.close()
        logger.error(f"Failed to remove port forward DB record {forward_id}: {e}")
        return False, None
    try:
        await execute_lxc(f"lxc config device remove {shlex.quote(container)} tcp_proxy_{host_port}")
        await execute_lxc(f"lxc config device remove {shlex.quote(container)} udp_proxy_{host_port}")
    except Exception as e:
        logger.error(f"DB record removed but LXC cleanup failed for forward {forward_id}: {e}")
    conn.close()
    return True, user_id

def get_user_forwards(user_id: str) -> List[Dict]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM port_forwards WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# ==================================================== PORT FORWARDING FUNCTIONS END =====================================================

# ==================================================== IPv4 SSH TUNNEL (Pinggy) =====================================================

active_ipv4_tunnels: Dict[str, asyncio.Task] = {}
_tunnel_connection_info: Dict[str, tuple] = {}
# Node-aware tunnel/connection caches (container_name -> info) for remote nodes
_remote_ipv4_tunnels: Dict[str, tuple] = {}
_remote_filemanager: Dict[str, tuple] = {}

async def get_container_ip(container_name):
    try:
        proc = await asyncio.create_subprocess_exec(
            "lxc", "list", container_name, "--format", "json",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=15)
        data = json.loads(stdout)
        if data and len(data) > 0:
            state = data[0].get('state', {})
            network = state.get('network', {})
            for iface in network.values():
                for addr in iface.get('addresses', []):
                    if addr.get('family') == 'inet' and addr.get('scope') == 'global':
                        return addr['address']
        return None
    except Exception:
        return None

def save_ipv4_tunnel_db(container_name, user_id, triggered_by=''):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT OR REPLACE INTO ipv4_tunnels (user_id, container_name, created_at, triggered_by) VALUES (?, ?, ?, ?)',
                (user_id, container_name, datetime.now().isoformat(), triggered_by))
    conn.commit()
    conn.close()

def remove_ipv4_tunnel_db(container_name):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM ipv4_tunnels WHERE container_name = ?', (container_name,))
    conn.commit()
    conn.close()

def get_all_ipv4_tunnels():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM ipv4_tunnels')
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_fm_tunnel_db(container_name, user_id, triggered_by='', fm_username='', fm_password=''):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT OR REPLACE INTO filemanager_tunnels (user_id, container_name, created_at, triggered_by, fm_username, fm_password) VALUES (?, ?, ?, ?, ?, ?)',
                (user_id, container_name, datetime.now().isoformat(), triggered_by, fm_username, fm_password))
    conn.commit()
    conn.close()

def remove_fm_tunnel_db(container_name):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM filemanager_tunnels WHERE container_name = ?', (container_name,))
    conn.commit()
    conn.close()

def get_all_fm_tunnels():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM filemanager_tunnels')
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

async def check_install_ssh(container_name):
    try:
        r1 = await asyncio.create_subprocess_exec(
            "lxc", "exec", container_name, "--", "which", "sshd",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        o1, _ = await r1.communicate()
        if r1.returncode == 0:
            act = await asyncio.create_subprocess_exec(
                "lxc", "exec", container_name, "--", "systemctl", "is-active", "ssh",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            aout, _ = await act.communicate()
            if aout.decode().strip() == "active":
                return "ok"
            await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- systemctl enable --now ssh", timeout=30)
            return "ok"
        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- apt-get update -y", timeout=180)
        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- apt-get install -y openssh-server", timeout=120)
        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- bash -c \"sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config; sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config\"", timeout=10)
        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- systemctl enable --now ssh", timeout=30)
        return "ok"
    except Exception as e:
        return str(e)

async def run_ipv4_tunnel_loop(container_name, user_id, dm_user_id=None):
    while container_name in active_ipv4_tunnels:
        container_ip = await get_container_ip(container_name)
        if not container_ip:
            await asyncio.sleep(5)
            continue

        proc = None
        try:
            proc = await asyncio.create_subprocess_exec(
                "ssh", "-p", "443", "-R", f"0:{container_ip}:22", "tcp@free.pinggy.io",
                "-o", "ServerAliveInterval=30",
                "-o", "ServerAliveCountMax=3",
                "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null",
                "-o", "LogLevel=ERROR",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )

            sent_dm = False
            try:
                while True:
                    line = await asyncio.wait_for(proc.stdout.readline(), timeout=300)
                    if not line:
                        break
                    text = line.decode(errors='replace').strip()
                    match = re.search(r'tcp://([^\s:]+):(\d+)', text)
                    if match and not sent_dm:
                        host = match.group(1)
                        port = match.group(2)
                        sent_dm = True
                        _tunnel_connection_info[container_name] = (host, port)
                        try:
                            target_id = dm_user_id or user_id
                            user = await bot.fetch_user(int(target_id))
                            dm = discord.Embed(
                                title=f"{EMOJI_GLOBAL} IPv4 SSH Tunnel Active",
                                description=f"Your temporary tunnel for **{container_name}** is ready!",
                                color=0x00ff88
                            )
                            dm.add_field(name=f"{EMOJI_ARROW_RIGHT} SSH Command", value=f"```ssh -p {port} root@{host}```", inline=False)
                            dm.add_field(name=f"{EMOJI_ARROW_RIGHT} Host", value=host, inline=True)
                            dm.add_field(name=f"{EMOJI_ARROW_RIGHT} Port", value=port, inline=True)
                            dm.set_footer(
                                text=f"{BOT_NAME} | Auto-reconnect active | 24/7 Tunnel", 
                                icon_url=THUMBNAIL_URL
                            )
                            await user.send(embed=dm)
                        except Exception:
                            pass
            except asyncio.TimeoutError:
                pass

            if proc:
                await proc.wait()
        except asyncio.CancelledError:
            _tunnel_connection_info.pop(container_name, None)
            raise
        except Exception as e:
            logger.error(f"IPv4 tunnel error for {container_name}: {e}")
        finally:
            if proc and proc.returncode is None:
                proc.kill()
                await proc.wait()

        if container_name not in active_ipv4_tunnels:
            _tunnel_connection_info.pop(container_name, None)
            break
        await asyncio.sleep(3)

async def start_ipv4_tunnel(container_name, user_id, progress_msg=None, triggered_by=None):
    if container_name in active_ipv4_tunnels:
        return False, "Tunnel already running"

    async def edit_progress(text, color=0xffaa00):
        if progress_msg:
            embed = discord.Embed(
                title=f"{EMOJI_GLOBAL} IPv4 SSH Tunnel — {container_name}",
                description=text,
                color=color
            )
            embed.set_footer(text=f"{BOT_NAME} | Setting up tunnel...")
            await progress_msg.edit(embed=embed)

    await edit_progress(f"{EMOJI_LOADING} Checking installation...")
    ssh_result = await check_install_ssh(container_name)
    if ssh_result != "ok":
        await edit_progress(f"{EMOJI_CROSS} **SSH Setup Failed:** {ssh_result}", 0xff3366)
        return False, f"SSH setup failed: {ssh_result}"

    await edit_progress(f"{EMOJI_SUCCESS} **SSH:** Ready\n{EMOJI_LOADING} **Tunnel:** Connecting to pinggy...")
    dm_user_id = str(triggered_by.id) if triggered_by else user_id
    task = asyncio.create_task(run_ipv4_tunnel_loop(container_name, user_id, dm_user_id))
    active_ipv4_tunnels[container_name] = task
    save_ipv4_tunnel_db(container_name, user_id, dm_user_id)

    for _ in range(30):
        if container_name in _tunnel_connection_info:
            host, port = _tunnel_connection_info[container_name]
            await edit_progress(
                f"{EMOJI_SUCCESS} **Tunnel:** Connected!\n"
                f"{EMOJI_GLOBAL} **SSH:** `ssh -p {port} root@{host}`\n"
                f"{EMOJI_INFO} Details sent to your DMs",
                0x00ff88
            )
            return True, (host, port)
        await asyncio.sleep(1)

    await edit_progress(
        f"{EMOJI_ONLINE} **Tunnel:** Started, awaiting pinggy URL\n"
        f"{EMOJI_INFO} You'll receive a DM once connected",
        0x00ccff
    )
    return True, None

async def stop_ipv4_tunnel(container_name):
    task = active_ipv4_tunnels.pop(container_name, None)
    if task:
        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, Exception):
            pass
    _tunnel_connection_info.pop(container_name, None)
    remove_ipv4_tunnel_db(container_name)

async def restore_ipv4_tunnels():
    tunnels = get_all_ipv4_tunnels()
    for t in tunnels:
        container_name = t['container_name']
        user_id = t['user_id']
        dm_user_id = t.get('triggered_by', '') or user_id
        if container_name not in active_ipv4_tunnels:
            task = asyncio.create_task(run_ipv4_tunnel_loop(container_name, user_id, dm_user_id))
            active_ipv4_tunnels[container_name] = task
            logger.info(f"Restored IPv4 tunnel for {container_name}")

async def restore_fm_tunnels():
    tunnels = get_all_fm_tunnels()
    for t in tunnels:
        container_name = t['container_name']
        user_id = t['user_id']
        dm_user_id = t.get('triggered_by', '') or user_id
        username = t.get('fm_username', 'admin')
        password = t.get('fm_password', 'admin')
        if container_name not in active_filemanager:
            _filemanager_credentials[container_name] = {"username": username, "password": password}
            task = asyncio.create_task(run_filemanager_loop(container_name, user_id, username, password, dm_user_id))
            active_filemanager[container_name] = task
            logger.info(f"Restored filemanager tunnel for {container_name}")

# ==================================================== IPv4 SSH TUNNEL (Pinggy) END =====================================================

# ==================================================== FILEMANAGER (File Browser) =====================================================

active_filemanager: Dict[str, asyncio.Task] = {}
_filemanager_connection_info: Dict[str, tuple] = {}
_filemanager_credentials: Dict[str, dict] = {}
FM_CREDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".fm_creds")

def _save_fm_creds(container_name, username, password):
    try:
        os.makedirs(FM_CREDS_DIR, exist_ok=True)
        path = os.path.join(FM_CREDS_DIR, f"{container_name}.json")
        with open(path, "w") as f:
            json.dump({"username": username, "password": password}, f)
    except Exception:
        pass

def _load_fm_creds(container_name):
    try:
        path = os.path.join(FM_CREDS_DIR, f"{container_name}.json")
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
    except Exception:
        pass
    return None

def _delete_fm_creds(container_name):
    try:
        path = os.path.join(FM_CREDS_DIR, f"{container_name}.json")
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

async def check_install_filemanager(container_name, progress_callback=None):
    try:
        async def prog(text, color=0xffaa00):
            if progress_callback:
                await progress_callback(text, color)

        r1 = await asyncio.create_subprocess_exec(
            "lxc", "exec", container_name, "--", "which", "filebrowser",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        o1, _ = await r1.communicate()
        if r1.returncode == 0:
            r2 = await asyncio.create_subprocess_exec(
                "lxc", "exec", container_name, "--", "filebrowser", "version",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            o2, _ = await r2.communicate()
            if r2.returncode == 0:
                return "ok"

        await prog(f"{EMOJI_LOADING} Installing filebrowser...")
        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- apt-get update -y", timeout=180)
        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- apt-get install -y curl", timeout=120)
        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- curl -fsSL https://raw.githubusercontent.com/filebrowser/get/master/get.sh -o /tmp/install_filebrowser.sh", timeout=120)
        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- bash /tmp/install_filebrowser.sh", timeout=60)
        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- rm -f /tmp/install_filebrowser.sh", timeout=10)

        ver = await asyncio.create_subprocess_exec(
            "lxc", "exec", container_name, "--", "filebrowser", "version",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        vout, _ = await ver.communicate()
        if ver.returncode != 0:
            return "Installation failed: filebrowser binary not found after install"

        await prog(f"{EMOJI_SUCCESS} Filebrowser installed\n{EMOJI_LOADING} Initializing config...")

        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- filebrowser config init", timeout=30)
        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- filebrowser config set --address=0.0.0.0 --port=8080 --root=/", timeout=30)

        return "ok"
    except Exception as e:
        return str(e)

async def _run_in_container(container_name, cmd, timeout=120):
    proc = None
    try:
        proc = await asyncio.create_subprocess_exec(
            "lxc", "exec", container_name, "--", *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        out = stdout.decode().strip() if stdout else ""
        err = stderr.decode().strip() if stderr else ""
        if proc.returncode != 0:
            raise Exception(err or out or f"exit code {proc.returncode}")
        return out
    except asyncio.TimeoutError:
        try:
            proc.kill()
            await proc.wait()
        except Exception:
            pass
        raise Exception("timeout")

async def configure_filemanager_user(container_name, username, password):
    try:
        await _run_in_container(container_name, ["filebrowser", "config", "init"])
    except Exception:
        pass
    try:
        await _run_in_container(container_name, ["filebrowser", "config", "set", "--address=0.0.0.0", "--port=8080", "--root=/"])
    except Exception:
        pass
    try:
        await _run_in_container(
            container_name,
            ["filebrowser", "users", "update", username, "--password", password, "--perm.admin"]
        )
    except Exception:
        try:
            await _run_in_container(
                container_name,
                ["filebrowser", "users", "add", username, password, "--perm.admin"]
            )
        except Exception as e:
            return str(e)
    _save_fm_creds(container_name, username, password)
    return True

async def run_filemanager_loop(container_name, user_id, username, password, dm_user_id=None):
    while container_name in active_filemanager:
        container_ip = await get_container_ip(container_name)
        if not container_ip:
            await asyncio.sleep(5)
            continue

        proc = None
        try:
            proc = await asyncio.create_subprocess_exec(
                "ssh", "-p", "443", "-R", f"0:{container_ip}:8080", "tcp@free.pinggy.io",
                "-o", "ServerAliveInterval=30",
                "-o", "ServerAliveCountMax=3",
                "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null",
                "-o", "LogLevel=ERROR",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )

            sent_dm = False
            try:
                while True:
                    line = await asyncio.wait_for(proc.stdout.readline(), timeout=300)
                    if not line:
                        break
                    text = line.decode(errors='replace').strip()
                    match = re.search(r'tcp://([^\s:]+):(\d+)', text)
                    if match and not sent_dm:
                        host = match.group(1)
                        port = match.group(2)
                        sent_dm = True
                        _filemanager_connection_info[container_name] = (host, port)
                        try:
                            target_id = dm_user_id or user_id
                            user = await bot.fetch_user(int(target_id))
                            fm_url = f"http://{host}:{port}"
                            dm = discord.Embed(
                                title=f"{EMOJI_FOLDER} File Manager Active",
                                description=f"Your file manager for **{container_name}** is ready!",
                                color=0x00ff88
                            )
                            dm.add_field(name=f"{EMOJI_ARROW_RIGHT} URL", value=f"{fm_url}", inline=False)
                            dm.add_field(name=f"{EMOJI_ARROW_RIGHT} Username", value=f"```{username}```", inline=True)
                            dm.add_field(name=f"{EMOJI_ARROW_RIGHT} Password", value=f"```{password}```", inline=True)
                            dm.set_footer(
                                text=f"{BOT_NAME} | Auto-reconnect active | 24/7 File Manager",
                                icon_url=THUMBNAIL_URL
                            )
                            await user.send(embed=dm)
                        except Exception:
                            pass
            except asyncio.TimeoutError:
                pass

            if proc:
                await proc.wait()
        except asyncio.CancelledError:
            _filemanager_connection_info.pop(container_name, None)
            _filemanager_credentials.pop(container_name, None)
            raise
        except Exception as e:
            logger.error(f"Filemanager tunnel error for {container_name}: {e}")
        finally:
            if proc and proc.returncode is None:
                proc.kill()
                await proc.wait()

        if container_name not in active_filemanager:
            _filemanager_connection_info.pop(container_name, None)
            _filemanager_credentials.pop(container_name, None)
            break
        await asyncio.sleep(3)

async def start_filemanager(container_name, user_id, username, password, progress_msg=None, triggered_by=None):
    if container_name in active_filemanager:
        return False, "File manager already running"

    async def edit_progress(text, color=0xffaa00):
        if progress_msg:
            embed = discord.Embed(
                title=f"{EMOJI_FOLDER} File Manager — {container_name}",
                description=text,
                color=color
            )
            embed.set_footer(text=f"{BOT_NAME} | Setting up file manager...")
            await progress_msg.edit(embed=embed)

    await edit_progress(f"{EMOJI_LOADING} Checking installation...")
    fm_result = await check_install_filemanager(container_name, edit_progress)
    if fm_result != "ok":
        await edit_progress(f"{EMOJI_CROSS} **Filebrowser Setup Failed:** {fm_result}", 0xff3366)
        return False, f"Filebrowser setup failed: {fm_result}"

    await edit_progress(f"{EMOJI_SUCCESS} Filebrowser installed\n{EMOJI_LOADING} Configuring user...")
    user_result = await configure_filemanager_user(container_name, username, password)
    if user_result is not True:
        await edit_progress(f"{EMOJI_CROSS} **User Config Failed:** {user_result}", 0xff3366)
        return False, f"User configuration failed: {user_result}"

    await edit_progress(
        f"{EMOJI_SUCCESS} **Filebrowser:** Ready\n"
        f"{EMOJI_SUCCESS} **User:** Configured\n"
        f"{EMOJI_LOADING} **Tunnel:** Connecting to pinggy..."
    )

    proc_kill = await asyncio.create_subprocess_exec(
        "lxc", "exec", container_name, "--", "pkill", "-f", "filebrowser",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    await proc_kill.wait()

    start_cmd = await asyncio.create_subprocess_exec(
        "lxc", "exec", container_name, "--", "bash", "-c",
        "nohup filebrowser --address=0.0.0.0 --port=8080 --root=/ > /dev/null 2>&1 &",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    await start_cmd.wait()
    await asyncio.sleep(2)

    dm_user_id = str(triggered_by.id) if triggered_by else user_id
    task = asyncio.create_task(run_filemanager_loop(container_name, user_id, username, password, dm_user_id))
    active_filemanager[container_name] = task
    _filemanager_credentials[container_name] = {"username": username, "password": password}

    for _ in range(30):
        if container_name in _filemanager_connection_info:
            host, port = _filemanager_connection_info[container_name]
            fm_url = f"http://{host}:{port}"
            await edit_progress(
                f"{EMOJI_SUCCESS} **Tunnel:** Connected!\n"
                f"{EMOJI_FOLDER} **URL:** {fm_url}\n"
                f"{EMOJI_USER} **Username:** `{username}`\n"
                f"{EMOJI_LOCK} **Password:** `{password}`\n"
                f"{EMOJI_INFO} Details sent to your DMs",
                0x00ff88
            )
            return True, (host, port, username, password)
        await asyncio.sleep(1)

    await edit_progress(
        f"{EMOJI_ONLINE} **Tunnel:** Started, awaiting pinggy URL\n"
        f"{EMOJI_INFO} You'll receive a DM once connected",
        0x00ccff
    )
    return True, None

async def stop_filemanager(container_name):
    task = active_filemanager.pop(container_name, None)
    if task:
        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, Exception):
            pass
    _filemanager_connection_info.pop(container_name, None)
    _filemanager_credentials.pop(container_name, None)
    remove_fm_tunnel_db(container_name)
    try:
        kill = await asyncio.create_subprocess_exec(
            "lxc", "exec", container_name, "--", "pkill", "-f", "filebrowser",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await kill.wait()
    except Exception:
        pass

async def clear_filemanager(container_name):
    await stop_filemanager(container_name)
    _delete_fm_creds(container_name)
    try:
        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- rm -f /usr/local/bin/filebrowser", timeout=30)
    except Exception:
        pass
    try:
        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- rm -rf ~/.config/filebrowser", timeout=30)
    except Exception:
        pass
    try:
        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- rm -rf /root/.config/filebrowser", timeout=30)
    except Exception:
        pass

# ==================================================== FILEMANAGER (File Browser) END =====================================================

# ==================================================== BOT INITIALIZATION =====================================================

# Initialize database
init_db()

# Load data at startup
vps_data = get_vps_data()
admin_data = {'admins': get_admins()}

# Global settings from DB
MAINTENANCE_MODE = get_setting('maintenance_mode', 'false').lower() == 'true'
MAINTENANCE_STARTED_BY = get_setting('maintenance_started_by', '')
MAINTENANCE_STARTED_AT = get_setting('maintenance_started_at', '')
BOT_STATUS = get_setting('bot_status', 'online')
BOT_ACTIVITY = get_setting('bot_activity', 'watching')
BOT_ACTIVITY_NAME = get_setting('bot_activity_name', f'{BOT_NAME} VPS Manager')
PREFIX = get_setting('prefix', PREFIX)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=lambda *_: PREFIX, intents=intents, help_command=None)

BOT_START_TIME = time.time()

# Rolling history of recent Discord heartbeat round-trips (ms), used to report
# an averaged latency instead of a single noisy sample.
import collections
_WS_LATENCY_HISTORY = collections.deque(maxlen=10)
_GATEWAY_URL = "https://discord.com/api/v10/gateway"

async def sample_ws_latency():
    """Record the current Discord heartbeat latency (ms) if it is valid."""
    try:
        lat = bot.latency
        if lat is not None and lat == lat and lat != float('inf'):  # not NaN/inf
            _WS_LATENCY_HISTORY.append(lat * 1000)
    except Exception:
        pass

async def measure_discord_api_rtt():
    """Measure a real HTTPS round-trip to Discord's API (ms)."""
    start = time.perf_counter()
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=8)) as session:
            async with session.get(_GATEWAY_URL) as resp:
                await resp.read()
        return (time.perf_counter() - start) * 1000
    except Exception:
        return None

async def ws_latency_sampler_loop():
    """Sample the heartbeat latency every 5s so $ping can show a stable average."""
    await bot.wait_until_ready()
    while not bot.is_closed():
        await sample_ws_latency()
        await asyncio.sleep(5)

class RestartBotConfirmView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.message = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the requester can confirm."), ephemeral=True)
            return
        await interaction.response.defer()
        try:
            embed = create_info_embed("Restarting Bot", f"{EMOJI_LOADING} Bot restart initiated...")
            await interaction.edit_original_response(embed=embed, view=None)
            embed = create_success_embed("Bot Restarting", "Bot restart initiated. Bot will be back shortly.")
            await interaction.edit_original_response(embed=embed, view=None)

            async def _do_restart():
                await asyncio.sleep(2)
                try:
                    import sys
                    sys.stdout.flush()
                    sys.stderr.flush()
                    os._exit(0)
                except Exception:
                    pass

            asyncio.create_task(_do_restart())
        except Exception as e:
            await interaction.edit_original_response(embed=create_error_embed("Failed", f"```{str(e)}```"), view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the requester can cancel."), ephemeral=True)
            return
        await interaction.response.defer()
        await interaction.edit_original_response(embed=create_info_embed("Cancelled", "Bot restart cancelled."), view=None)


# ╔══════════════════════════════════════════════════════════════════════════╗



# Dictionary to track active help menus to prevent duplicates
active_help_menus = {}

# Invite cache for tracking who invited whom
_invite_cache: Dict[int, Dict[str, Any]] = {}

# Helper function to truncate text
def truncate_text(text, max_length=1024):
    if not text:
        return text
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

# ==================================================== BOT INITIALIZATION END =====================================================

# ==================================================== EASY EMBED CREATION FUNCTIONS =====================================================

def create_embed(title, description="", color=0x1a1a1a):
    """Create a styled embed with thumbnail and footer icon"""
    embed = discord.Embed(
        title=truncate_text(f"{EMOJI_STAR} {BOT_NAME} - {title}", 256),
        description=truncate_text(description, 4096),
        color=color
    )
    
    # Set thumbnail if URL is provided
    if THUMBNAIL_URL:
        embed.set_thumbnail(url=THUMBNAIL_URL)
    
    # Set footer with timestamp and icon
    embed.set_footer(
        text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        icon_url=THUMBNAIL_URL
    )
    
    return embed

def add_field(embed, name, value, inline=False):
    """Add a styled field to an embed"""
    embed.add_field(
        name=truncate_text(f"{EMOJI_ARROW_RIGHT} {name}", 256),
        value=truncate_text(value, 1024),
        inline=inline
    )
    return embed

def create_success_embed(title, description=""):
    """Create a success embed (green)"""
    return create_embed(title, description, color=0x00ff88)

def create_error_embed(title, description=""):
    """Create an error embed (red)"""
    return create_embed(title, description, color=0xff3366)

def create_info_embed(title, description=""):
    """Create an info embed (blue)"""
    return create_embed(title, description, color=0x00ccff)

def create_warning_embed(title, description=""):
    """Create a warning embed (yellow/orange)"""
    return create_embed(title, description, color=0xffaa00)

def create_loading_embed(description=None):
    """Create a loading embed shown immediately while a command fetches data."""
    if not description:
        description = f"{EMOJI_LOADING} Processing your request, please wait..."
    return create_embed("Please Wait", description, color=0x00ccff)

# ==================================================== GLOBAL LOADING EMBED ====================================================

@bot.before_invoke
async def _sgm_send_loading(ctx):
    """Send an immediate loading embed that morphs into the command's first embed.

    This gives instant feedback on slow commands while guaranteeing a single
    embed per command: the first ``ctx.send(embed=...)`` edits the loading
    message instead of posting a second message.
    """
    ctx._sgm_loading = None
    ctx._sgm_loading_used = False
    try:
        ctx._sgm_loading = await ctx.send(embed=create_loading_embed())
    except Exception:
        ctx._sgm_loading = None

    _orig_send = ctx.send

    async def _patched_send(*args, **kwargs):
        if not ctx._sgm_loading_used and ctx._sgm_loading is not None and 'embed' in kwargs:
            ctx._sgm_loading_used = True
            try:
                await ctx._sgm_loading.edit(embed=kwargs.get('embed'), view=kwargs.get('view'))
                return ctx._sgm_loading
            except Exception:
                pass
        ctx._sgm_loading_used = True
        return await _orig_send(*args, **kwargs)

    ctx.send = _patched_send

@bot.after_invoke
async def _sgm_cleanup_loading(ctx):
    """Remove an unused loading embed, unless the command failed and the error
    handler will reuse it."""
    loading = getattr(ctx, '_sgm_loading', None)
    if loading is None or getattr(ctx, '_sgm_loading_used', False):
        return
    if getattr(ctx, 'command_failed', False):
        return
    try:
        await loading.delete()
    except Exception:
        pass

# ==================================================== GLOBAL LOADING EMBED END ====================================================

async def safe_dm(user_id: str, embed: discord.Embed):
    try:
        uid = int(user_id)
        user = await bot.fetch_user(uid)
        await user.send(embed=embed)
        return True
    except (discord.Forbidden, discord.HTTPException, ValueError, Exception):
        return False

def create_no_vps_embed():
    """Create the No VPS Found embed"""
    embed = discord.Embed(
        title=f"{EMOJI_STAR} {BOT_NAME} - No VPS Found",
        description="You don't have any VPS. Contact an admin to create one.",
        color=0xff3366
    )
    
    quick_actions = f"• `{PREFIX}manage` - Manage VPS\n"
    quick_actions += "• Contact admin for VPS creation"
    
    embed.add_field(
        name=f"{EMOJI_ARROW_RIGHT} Quick Actions",
        value=quick_actions,
        inline=False
    )
    
    # Set thumbnail if URL is provided
    if THUMBNAIL_URL:
        embed.set_thumbnail(url=THUMBNAIL_URL)
    
    # Set footer with timestamp and icon
    embed.set_footer(
        text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        icon_url=THUMBNAIL_URL
    )
    
    return embed

def create_ping_embed(ws_now, ws_avg, ws_min, ws_max, api_rtt, db_latency, samples):
    """Create the latency report embed."""
    embed = discord.Embed(
        title=f"{EMOJI_STATS} System Latency Report",
        color=0x00ccff
    )

    # Discord connection (heartbeat) — averaged for stability
    if ws_avg is not None:
        conn_val = f"`{ws_avg:.1f} ms`"
    else:
        conn_val = "`waiting for heartbeat…`"

    # Live HTTPS round-trip to Discord API
    api_val = f"`{api_rtt:.1f} ms`" if api_rtt is not None else "`unreachable`"
    db_val = f"`{db_latency:.2f} ms`"

    embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Discord Heartbeat", value=conn_val, inline=True)
    embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Discord API", value=api_val, inline=True)
    embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Database", value=db_val, inline=True)

    # Overall status — judge by the averaged heartbeat, fall back to API RTT
    judge = ws_avg if ws_avg is not None else api_rtt
    if judge is None:
        status = f"{EMOJI_MID_SIGNAL} Unable to measure"
    elif judge < 100:
        status = f"{EMOJI_GOOD_SIGNAL} All systems normal"
    elif judge < 200:
        status = f"{EMOJI_MID_SIGNAL} Elevated latency"
    else:
        status = f"{EMOJI_BAD_SIGNAL} High latency"
    embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Status", value=status, inline=False)

    # Set thumbnail if URL is provided
    if THUMBNAIL_URL:
        embed.set_thumbnail(url=THUMBNAIL_URL)

    # Set footer with timestamp and icon
    embed.set_footer(
        text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        icon_url=THUMBNAIL_URL
    )

    return embed

# ==================================================== EASY EMBED CREATION FUNCTIONS END =====================================================

# ==================================================== TRACKING CHANNEL HELPER =====================================================

async def send_tracking(action_emoji, title, description, color=0x1a1a1a, fields=None):
    if not TRACKING_CHANNEL:
        return

    channel = bot.get_channel(TRACKING_CHANNEL)
    if not channel:
        try:
            channel = await bot.fetch_channel(TRACKING_CHANNEL)
        except Exception:
            logger.warning(f"Tracking channel {TRACKING_CHANNEL} not found")
            return

    embed = discord.Embed(
        title=f"{action_emoji} {title}",
        description=description,
        color=color,
        timestamp=datetime.now()
    )

    if THUMBNAIL_URL:
        embed.set_thumbnail(url=THUMBNAIL_URL)

    embed.set_footer(
        text=f"{BOT_NAME} VPS Manager - Tracking Entry",
        icon_url=THUMBNAIL_URL
    )

    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

    try:
        await channel.send(embed=embed)
    except Exception:
        logger.warning(f"Failed to send tracking to channel {TRACKING_CHANNEL}")

# ==================================================== TRACKING CHANNEL HELPER END =====================================================

# ==================================================== LOGGING CHANNEL HELPER =====================================================

async def send_log(action_emoji, title, description, color=0x1a1a1a, fields=None):
    if not LOGGIN_CHANNEL:
        return

    channel = bot.get_channel(LOGGIN_CHANNEL)
    if not channel:
        try:
            channel = await bot.fetch_channel(LOGGIN_CHANNEL)
        except Exception:
            logger.warning(f"Log channel {LOGGIN_CHANNEL} not found")
            return

    embed = discord.Embed(
        title=f"{action_emoji} {title}",
        description=description,
        color=color,
        timestamp=datetime.now()
    )

    if THUMBNAIL_URL:
        embed.set_thumbnail(url=THUMBNAIL_URL)

    embed.set_footer(
        text=f"{BOT_NAME} VPS Manager - Log Entry",
        icon_url=THUMBNAIL_URL
    )

    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

    try:
        await channel.send(embed=embed)
    except Exception:
        logger.warning(f"Failed to send log to channel {LOGGIN_CHANNEL}")

# ==================================================== LOGGING CHANNEL HELPER END =====================================================

# ==================================================== VPS TIMER HELPERS =====================================================

def parse_time_string(time_str):
    if not time_str or not isinstance(time_str, str):
        return None
    time_str = time_str.strip().lower()
    match = re.match(r'^(\d+)\s*(s|sec|m|min|h|hr|hour|d|day|days|month|months|y|yr|year|years)$', time_str)
    if not match:
        return None
    num = int(match.group(1))
    unit = match.group(2)
    if unit in ('s', 'sec'):
        return timedelta(seconds=num)
    elif unit in ('m', 'min'):
        return timedelta(minutes=num)
    elif unit in ('h', 'hr', 'hour'):
        return timedelta(hours=num)
    elif unit in ('d', 'day', 'days'):
        return timedelta(days=num)
    elif unit in ('month', 'months'):
        return timedelta(days=num * 30)
    elif unit in ('y', 'yr', 'year', 'years'):
        return timedelta(days=num * 365)
    return None

def format_timedelta(td):
    if td is None:
        return f"{EMOJI_CROSS} No timer"
    total_seconds = int(td.total_seconds())
    if total_seconds <= 0:
        return f"{EMOJI_CROSS} Expired"
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    return " ".join(parts)

def check_vps_limit(user_id: str, is_paid: bool = False) -> tuple[bool, str]:
    try:
        user_vps_count = len(node_vps_user(user_id))
    except Exception:
        user_vps_count = len(vps_data.get(user_id, []))
    if user_id in MAIN_ADMIN_IDS or user_id in admin_data.get("admins", []):
        return True, ""
    limit_val = int(PAID_PLANS_MAX_VPS) if is_paid else int(FREE_PLANS_MAX_VPS)
    if limit_val == 0:
        return True, ""
    if user_vps_count >= limit_val:
        label = "paid" if is_paid else "free"
        return False, f"You have reached the maximum number of VPS ({limit_val}) for {label} plans."
    return True, ""

# ==================================================== RESOURCE VALUE HELPERS =====================================================
# RAM / CPU / disk may be entered as decimals (e.g. 1.9). LXD needs integer
# sizes (MB) and does not accept fractional CPU cores, so we normalise here.

def _to_num(value):
    """Parse a stored resource value ('1.5GB', '2GiB', 2, 1.9) into a float (GB)."""
    if value is None:
        return 0.0
    s = str(value).strip().lower()
    factor = 1.0
    if s.endswith('gib'):
        s = s[:-3]
    elif s.endswith('gb'):
        s = s[:-2]
    elif s.endswith('mib'):
        s = s[:-3]; factor = 1.0 / 1024.0
    elif s.endswith('mb'):
        s = s[:-2]; factor = 1.0 / 1024.0
    try:
        return float(s.strip()) * factor
    except ValueError:
        return 0.0


def _fmt_num(value):
    """Format a resource number for display: 1.0 -> '1', 1.9 -> '1.9'."""
    try:
        f = float(value)
    except (TypeError, ValueError):
        return str(value)
    if f == int(f):
        return str(int(f))
    return ('%g' % f)


def _mem_mb(ram_gb):
    """Decimal GB -> integer MB for limits.memory."""
    return max(1, int(round(float(ram_gb) * 1024)))


def _disk_mb(disk_gb):
    """Decimal GB -> integer MB for the root device size."""
    return max(1, int(round(float(disk_gb) * 1024)))


def _cpu_limits(cpu_cores):
    """Return (limits.cpu value, limits.cpu.allowance or None).

    Whole cores use plain cpuset pinning. Fractional cores pin ceil() cores
    and add a CFS time allowance (e.g. 1.9 cores -> '2' + '190ms/100ms').
    """
    c = float(cpu_cores)
    if c <= 0:
        c = 1.0
    whole = int(c)
    if float(whole) == c:
        return str(whole), None
    return str(whole + 1), f"{int(round(c * 100))}ms/100ms"


async def apply_resource_limits(container_name, ram_gb=None, cpu_cores=None, disk_gb=None):
    """Apply RAM / CPU / disk limits to a container. Decimals are supported."""
    qn = shlex.quote(container_name)
    if ram_gb is not None:
        await execute_lxc(f"lxc config set {qn} limits.memory {_mem_mb(ram_gb)}MB")
    if disk_gb is not None:
        await execute_lxc(f"lxc config device set {qn} root size={_disk_mb(disk_gb)}MB")
    if cpu_cores is not None:
        cpu_val, allowance = _cpu_limits(cpu_cores)
        await execute_lxc(f"lxc config set {qn} limits.cpu {cpu_val}")
        if allowance is None:
            try:
                await execute_lxc(f"lxc config unset {qn} limits.cpu.allowance")
            except Exception:
                pass
        else:
            await execute_lxc(f"lxc config set {qn} limits.cpu.allowance {allowance}")
# ==================================================== RESOURCE VALUE HELPERS END =====================================================


async def get_available_resources():
    result = {}
    
    try:
        proc = await asyncio.create_subprocess_exec("nproc", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
        total_cpu = int(stdout.decode().strip())
    except:
        total_cpu = os.cpu_count() or 0
    
    allocated_cpu = 0
    for uid, vps_list in vps_data.items():
        for vps in vps_list:
            try:
                allocated_cpu += _to_num(vps['cpu'])
            except:
                pass
    
    result['cpu'] = {
        'total': total_cpu,
        'allocated': allocated_cpu,
        'available': max(0, total_cpu - allocated_cpu)
    }
    
    total_ram_gb = 0
    try:
        proc = await asyncio.create_subprocess_exec("free", "-b", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
        for line in stdout.decode().splitlines():
            if line.startswith("Mem:"):
                parts = line.split()
                total_ram_gb = int(parts[1]) // (1024**3)
                break
    except:
        pass
    
    allocated_ram_gb = 0
    for uid, vps_list in vps_data.items():
        for vps in vps_list:
            try:
                allocated_ram_gb += _to_num(vps['ram'])
            except:
                pass
    
    result['ram'] = {
        'total_gb': total_ram_gb,
        'allocated_gb': allocated_ram_gb,
        'available_gb': max(0, total_ram_gb - allocated_ram_gb)
    }
    
    # Host filesystem usage (baseline + fallback when no quota pool is active)
    host_total_gb = 0
    host_used_gb = 0
    host_free_gb = 0
    try:
        usage = shutil.disk_usage('/')
        host_total_gb = usage.total // (1024**3)
        host_used_gb = usage.used // (1024**3)
        host_free_gb = usage.free // (1024**3)
    except:
        pass

    # Sum of the disk sizes promised to every VPS (from our own DB).
    allocated_disk_gb = 0
    for uid, vps_list in vps_data.items():
        for vps in vps_list:
            try:
                allocated_disk_gb += _to_num(vps['storage'])
            except:
                pass

    # Report the quota pool's capacity — the storage actually handed out to
    # VPSs. Using the pool keeps "Available" honest: it shrinks as VPSs are
    # allocated and can never exceed the enforced capacity.
    if DEFAULT_STORAGE_POOL != FALLBACK_STORAGE_POOL:
        pool_total_gb, pool_used_gb = await get_storage_pool_info_gb(DEFAULT_STORAGE_POOL)
    else:
        pool_total_gb, pool_used_gb = 0, 0

    if pool_total_gb > 0:
        total_disk_gb = pool_total_gb
        used_disk_gb = pool_used_gb
        available_disk_gb = max(0, total_disk_gb - allocated_disk_gb)
    else:
        total_disk_gb = host_total_gb
        used_disk_gb = host_used_gb
        available_disk_gb = max(0, host_free_gb)

    result['disk'] = {
        'total_gb': total_disk_gb,
        'used_gb': used_disk_gb,
        'available_gb': available_disk_gb,
        'pool_total_gb': total_disk_gb,
        'pool_available_gb': available_disk_gb,
        'allocated_gb': allocated_disk_gb,
        'host_total_gb': host_total_gb,
        'host_used_gb': host_used_gb,
        'host_free_gb': host_free_gb
    }

    return result


async def check_resources(ram_gb, cpu_cores, disk_gb, bypass_cpu=False, bypass_ram=False, bypass_disk=False):
    resources = await get_available_resources()
    
    issues = []
    
    if not bypass_cpu and cpu_cores > resources['cpu']['available']:
        issues.append(
            f"{EMOJI_CPU} **CPU:** Requested {_fmt_num(cpu_cores)} cores, only {_fmt_num(resources['cpu']['available'])} available "
            f"(Total: {_fmt_num(resources['cpu']['total'])}, Used: {_fmt_num(resources['cpu']['allocated'])})"
        )
    
    if not bypass_ram and ram_gb > resources['ram']['available_gb']:
        issues.append(
            f"{EMOJI_RAM} **RAM:** Requested {_fmt_num(ram_gb)}GB, only {_fmt_num(resources['ram']['available_gb'])}GB available "
            f"(Total: {_fmt_num(resources['ram']['total_gb'])}GB, Used: {_fmt_num(resources['ram']['allocated_gb'])}GB)"
        )
    
    disk_available_gb = resources['disk'].get('pool_available_gb', resources['disk']['total_gb'] - resources['disk']['allocated_gb'])
    if not bypass_disk and disk_gb > disk_available_gb:
        issues.append(
            f"{EMOJI_DISK} **Disk:** Requested {_fmt_num(disk_gb)}GB, only {_fmt_num(disk_available_gb)}GB available "
            f"(Total: {_fmt_num(resources['disk']['total_gb'])}GB, Allocated: {_fmt_num(resources['disk']['allocated_gb'])}GB)"
        )
    
    if issues:
        msg = "## Resource Check initialized\n\n" + "\n\n".join(issues)
        msg += f"\n\n{EMOJI_INFO} Free up resources or request a smaller VPS."
        return False, msg
    
    return True, ""


def get_vps_timer_info(vps):
    expires_at = vps.get('expires_at', '')
    if not expires_at:
        return None
    timer_status = vps.get('timer_status', '')
    timer_paused_at = vps.get('timer_paused_at', '')
    now = datetime.now()
    if timer_status == 'paused' and timer_paused_at:
        paused = datetime.fromisoformat(timer_paused_at)
        expires_dt = datetime.fromisoformat(expires_at)
        remaining = expires_dt - paused
        return remaining
    expires_dt = datetime.fromisoformat(expires_at)
    remaining = expires_dt - now
    return remaining

def get_vps_timer_line(vps):
    expires_at = vps.get('expires_at', '')
    timer_status = vps.get('timer_status', '')
    if not expires_at:
        return ""
    remaining = get_vps_timer_info(vps)
    if timer_status == 'expired':
        return f"\n{EMOJI_UPTIME} **Timer:** {EMOJI_CROSS} Expired"
    if remaining is None:
        return ""
    if timer_status == 'paused':
        return f"\n{EMOJI_UPTIME} **Timer:** {format_timedelta(remaining)} ({EMOJI_WARNING} Paused)"
    return f"\n{EMOJI_UPTIME} **Timer:** {format_timedelta(remaining)}"

# ==================================================== VPS TIMER HELPERS END =====================================================

# ==================================================== MAINTENANCE MODE CHECK =====================================================

async def maintenance_check(ctx):
    global MAINTENANCE_MODE, MAINTENANCE_STARTED_BY, MAINTENANCE_STARTED_AT
    
    if MAINTENANCE_MODE:
        user_id = str(ctx.author.id)
        if user_id in MAIN_ADMIN_IDS or user_id in admin_data.get("admins", []):
            return True
        
        try:
            started_by_user = await bot.fetch_user(int(MAINTENANCE_STARTED_BY)) if MAINTENANCE_STARTED_BY else None
            started_by_mention = started_by_user.mention if started_by_user else "Unknown"
        except:
            started_by_mention = "Unknown"
        
        try:
            started_at = datetime.fromisoformat(MAINTENANCE_STARTED_AT).strftime('%Y-%m-%d %H:%M:%S') if MAINTENANCE_STARTED_AT else "Unknown"
        except:
            started_at = "Unknown"
        
        embed = create_warning_embed(
            "Maintenance Mode Active",
            "The bot is currently under maintenance. Only administrators can use commands at this time."
        )
        add_field(embed, "Started By", started_by_mention, True)
        add_field(embed, "Status", "Commands disabled for non-admins", True)
        add_field(embed, "Started At", started_at, False)
        
        await ctx.send(embed=embed)
        return False
    return True

# ==================================================== MAINTENANCE MODE CHECK END =====================================================

# ==================================================== ADMIN CHECKS =====================================================

def is_admin():
    async def predicate(ctx):
        if not await maintenance_check(ctx):
            return False
        
        user_id = str(ctx.author.id)
        if user_id in MAIN_ADMIN_IDS or user_id in admin_data.get("admins", []):
            return True
        raise commands.CheckFailure("You need admin permissions to use this command.")
    return commands.check(predicate)

@bot.command(name='restart-bot')
@is_admin()
@commands.cooldown(1, 10, commands.BucketType.user)
async def restart_bot_cmd(ctx):
    """Restart the bot service: restart-bot (Admin)"""
    if not await maintenance_check(ctx):
        return
    embed = create_warning_embed("Confirm Bot Restart", "You are about to restart the bot service. This will disconnect the bot temporarily.")
    view = RestartBotConfirmView(ctx)
    view.message = await ctx.send(embed=embed, view=view)


def is_main_admin():
    async def predicate(ctx):
        if not await maintenance_check(ctx):
            return False
        
        if str(ctx.author.id) in MAIN_ADMIN_IDS:
            return True
        raise commands.CheckFailure("Only the main admin can use this command.")
    return commands.check(predicate)

# ==================================================== ADMIN CHECKS END =====================================================

# ==================================================== LXC COMMAND EXECUTION =====================================================

async def execute_lxc(command, timeout=120):
    try:
        cmd = shlex.split(command)
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise asyncio.TimeoutError(f"Command timed out after {timeout} seconds: {command}")

        stdout_str = stdout.decode().strip() if stdout else ""
        stderr_str = stderr.decode().strip() if stderr else ""

        if proc.returncode != 0:
            error_msg = stderr_str if stderr_str else stdout_str if stdout_str else "Command failed with no output"
            raise Exception(error_msg)

        return stdout_str if stdout_str else True
    except asyncio.TimeoutError:
        raise
    except Exception as e:
        raise

# ==================================================== LXC COMMAND EXECUTION END =====================================================

# ==================================================== LXC CONFIGURATION =====================================================

async def apply_lxc_config(container_name):
    try:
        await execute_lxc(f"lxc config set {shlex.quote(container_name)} security.nesting true")
        await execute_lxc(f"lxc config set {shlex.quote(container_name)} security.privileged true")
        await execute_lxc(f"lxc config set {shlex.quote(container_name)} security.syscalls.intercept.mknod true")
        await execute_lxc(f"lxc config set {shlex.quote(container_name)} security.syscalls.intercept.setxattr true")
        
        try:
            await execute_lxc(f"lxc config device add {shlex.quote(container_name)} fuse unix-char path=/dev/fuse")
        except Exception as e:
            if "already exists" not in str(e).lower():
                raise
        
        await execute_lxc(f"lxc config set {shlex.quote(container_name)} linux.kernel_modules overlay,loop,nf_nat,ip_tables,ip6_tables,netlink_diag,br_netfilter")
        
        raw_lxc_config = """
lxc.apparmor.profile = unconfined
lxc.cgroup.devices.allow = a
lxc.cap.drop =
lxc.mount.auto = proc:rw sys:rw cgroup:rw
"""
        await execute_lxc(f"lxc config set {shlex.quote(container_name)} raw.lxc '{raw_lxc_config}'")
        
        logger.info(f"Applied LXC config to {container_name}")
    except Exception as e:
        logger.error(f"Failed to apply LXC config to {container_name}: {e}")

async def apply_internal_permissions(container_name):
    try:
        await asyncio.sleep(5)
        
        commands = [
            "mkdir -p /etc/sysctl.d/",
            "echo 'net.ipv4.ip_unprivileged_port_start=0' > /etc/sysctl.d/99-custom.conf",
            "echo 'net.ipv4.ping_group_range=0 2147483647' >> /etc/sysctl.d/99-custom.conf",
            "echo 'fs.inotify.max_user_watches=524288' >> /etc/sysctl.d/99-custom.conf",
            "sysctl -p /etc/sysctl.d/99-custom.conf || true",
            # Remove the old rc.local dhclient hack: dhclient rewrites /etc/resolv.conf
            # and breaks DNS after reboot. systemd-networkd already handles DHCP.
            "grep -q 'dhclient eth0' /etc/rc.local 2>/dev/null && sed -i '/dhclient eth0/d' /etc/rc.local || true"
        ]
        
        for cmd in commands:
            try:
                await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- bash -c \"{cmd}\"")
            except Exception:
                continue
        
        logger.info(f"Applied internal permissions to {container_name}")
    except Exception as e:
        logger.error(f"Failed to apply internal permissions to {container_name}: {e}")

async def container_exists(container_name):
    try:
        await execute_lxc(f"lxc info {shlex.quote(container_name)}", timeout=10)
        return True
    except Exception:
        return False

async def _get_lxdbr0_subnet():
    """Return the actual lxdbr0 IPv4 subnet (e.g. '10.141.88.0/24') or None."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "lxc", "network", "get", "lxdbr0", "ipv4.address",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
        addr = out.decode().strip()
        if proc.returncode == 0 and addr and "/" in addr:
            ip_part = addr.split("/")[0]
            prefix = addr.split("/")[1]
            octets = ip_part.split(".")
            if len(octets) == 4:
                return f"{octets[0]}.{octets[1]}.{octets[2]}.0/{prefix}"
    except Exception:
        pass
    try:
        proc = await asyncio.create_subprocess_exec(
            "ip", "-4", "-o", "addr", "show", "dev", "lxdbr0",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
        import re as _re
        m = _re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)/(\d+)", out.decode())
        if m:
            octets = m.group(1).split(".")
            return f"{octets[0]}.{octets[1]}.{octets[2]}.0/{m.group(2)}"
    except Exception:
        pass
    return None

async def _run_host_shell(script, timeout=20):
    """Run a shell script on the host (root), silently ignoring failures."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "bash", "-c", script,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return proc.returncode == 0
    except Exception:
        return False

async def _run_cmd(*args, timeout=30):
    """Run a command on the host, returning (returncode, stdout, stderr)."""
    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return proc.returncode, out.decode(errors="replace").strip(), err.decode(errors="replace").strip()
    except asyncio.TimeoutError:
        try:
            proc.kill()
            await proc.wait()
        except Exception:
            pass
        return 124, "", "timeout"
    except Exception as e:
        return 1, "", str(e)

_UNIT_TO_GIB = {"B": 1 / (1024**3), "KiB": 1 / (1024**2), "MiB": 1 / 1024, "GiB": 1.0, "TiB": 1024.0}

def _size_to_gib(value, unit):
    """Convert an LXD-reported size (value + unit like GiB/GB/MB) to whole GiB."""
    if unit in ("GB", "MB", "KB", "B"):
        # decimal units reported by some drivers -> convert to GiB
        factor = {"B": 1 / (1024**3), "KB": 1 / (1024**2), "MB": 1 / 1024, "GB": 1.0}[unit]
        return int(float(value) * factor)
    return int(float(value) * _UNIT_TO_GIB.get(unit, 1.0))

async def get_storage_pool_info_gb(pool):
    """Return (total_gb, used_gb) for a storage pool, or (0, 0) if unknown."""
    rc, out, _ = await _run_cmd("lxc", "storage", "info", pool, timeout=20)
    if rc != 0:
        return 0, 0
    total_gb = 0
    used_gb = 0
    m = re.search(r"total space:\s*([\d.]+)\s*([KMGT]?i?B)", out)
    if m:
        total_gb = _size_to_gib(m.group(1), m.group(2))
    m = re.search(r"space used:\s*([\d.]+)\s*([KMGT]?i?B)", out)
    if m:
        used_gb = _size_to_gib(m.group(1), m.group(2))
    return total_gb, used_gb

async def get_storage_pool_capacity_gb(pool):
    """Return the hard capacity of a storage pool in whole GiB, or 0 if unknown."""
    total_gb, _ = await get_storage_pool_info_gb(pool)
    return total_gb

def _quota_pool_target_gib():
    """How big the quota pool should be: the whole disk minus a small reserve."""
    try:
        total_bytes = shutil.disk_usage('/').total
        total_gib = int(total_bytes // (1024**3))
        target = total_gib - QUOTA_POOL_RESERVE_GB
        if target <= 0:
            target = int(total_bytes * QUOTA_POOL_TARGET_FRACTION // (1024**3))
        return max(0, target)
    except Exception:
        return 0

async def _get_pool_configured_size_gib(pool):
    """Return the pool's configured 'size' property in GiB (0 if unset/unknown)."""
    rc, out, _ = await _run_cmd("lxc", "storage", "get", pool, "size", timeout=15)
    if rc != 0:
        return 0
    m = re.match(r"\s*([\d.]+)\s*([KMGT]?i?B)?", out)
    if not m:
        return 0
    return _size_to_gib(m.group(1), m.group(2) or "GiB")

async def ensure_storage_pool():
    """Make sure the preferred, quota-enforced storage pool exists and fills the disk.

    Portable across hosts: if the pool already exists we grow it to the target
    size (whole disk minus a small reserve) and use it. Otherwise we create a
    loop-backed ZFS pool sized to that target (ZFS enforces per-container 'size'
    quotas natively). If that fails we fall back to the plain 'dir' pool so the
    bot still runs everywhere.
    """
    global DEFAULT_STORAGE_POOL
    pool = QUOTA_POOL_NAME
    target_gib = _quota_pool_target_gib()

    rc, _, _ = await _run_cmd("lxc", "storage", "show", pool, timeout=20)
    if rc == 0:
        DEFAULT_STORAGE_POOL = pool
        # Grow the pool if the configured size is below the target (disk size).
        try:
            cur_cfg = await _get_pool_configured_size_gib(pool)
        except Exception:
            cur_cfg = 0
        if target_gib and cur_cfg and cur_cfg < target_gib - 1:
            logger.info(f"Growing storage pool '{pool}' from {cur_cfg}GiB to {target_gib}GiB...")
            rc, out, err = await _run_cmd(
                "lxc", "storage", "set", pool, f"size={target_gib}GiB", timeout=180
            )
            if rc == 0:
                logger.info(f"Storage pool '{pool}' grown to {target_gib}GiB")
            else:
                logger.warning(f"Could not grow pool '{pool}': {err or out}")
        else:
            logger.info(f"Storage pool '{pool}' present ({cur_cfg}GiB) — using quota-enforced pool")
        await _make_quota_the_only_pool(pool)
        return DEFAULT_STORAGE_POOL

    try:
        size_gib = target_gib
        logger.info(f"Creating quota-enforced storage pool '{pool}' (zfs, {size_gib}GiB)...")
        rc, out, err = await _run_cmd(
            "lxc", "storage", "create", pool, "zfs", f"size={size_gib}GiB", timeout=300
        )
        if rc == 0:
            DEFAULT_STORAGE_POOL = pool
            logger.info(f"Storage pool '{pool}' created — using quota-enforced pool")
            await _make_quota_the_only_pool(pool)
            return DEFAULT_STORAGE_POOL
        logger.warning(f"Could not create pool '{pool}': {err or out}")
    except Exception as e:
        logger.warning(f"Could not create pool '{pool}': {e}")

    DEFAULT_STORAGE_POOL = FALLBACK_STORAGE_POOL
    logger.warning(f"Falling back to storage pool '{DEFAULT_STORAGE_POOL}' (no hard disk quota)")
    return DEFAULT_STORAGE_POOL

async def _make_quota_the_only_pool(pool):
    """Point the default profile at the quota pool and drop the unused 'default' pool.

    Keeps the same bot.py working on every host with a single enforced pool and
    no silent fallback to an unquota'd 'dir' pool.
    """
    if not pool or pool == FALLBACK_STORAGE_POOL:
        return

    # Repoint the LXD default profile's root device at the enforced pool.
    try:
        rc, out, _ = await _run_cmd(
            "lxc", "profile", "device", "get", "default", "root", "pool", timeout=15
        )
        cur = out.strip() if rc == 0 else ""
        if cur and cur != pool:
            rc2, _, err2 = await _run_cmd(
                "lxc", "profile", "device", "set", "default", "root", "pool", pool, timeout=15
            )
            if rc2 == 0:
                logger.info(f"Default profile root -> '{pool}'")
            else:
                logger.warning(f"Could not repoint default profile to '{pool}': {err2}")
    except Exception as e:
        logger.warning(f"Could not update default profile: {e}")

    # Delete the now-unused 'default' storage pool (best effort).
    try:
        rc, _, _ = await _run_cmd("lxc", "storage", "show", FALLBACK_STORAGE_POOL, timeout=15)
        if rc == 0:
            rc2, out2, err2 = await _run_cmd(
                "lxc", "storage", "delete", FALLBACK_STORAGE_POOL, timeout=120
            )
            if rc2 == 0:
                logger.info(f"Removed unused storage pool '{FALLBACK_STORAGE_POOL}'")
            else:
                logger.warning(f"Could not remove storage pool '{FALLBACK_STORAGE_POOL}': {err2 or out2}")
    except Exception as e:
        logger.warning(f"Could not remove '{FALLBACK_STORAGE_POOL}' pool: {e}")

async def migrate_containers_to_quota_pool():
    """Move any container still on a non-enforced pool onto the quota pool.

    The 'dir' driver ignores the per-container 'size' setting, so limits given to
    users on a dir pool are silently unenforced (df shows the whole host disk).
    This reconciles existing containers so every VPS has a real quota. Safe to
    call at startup; only acts when a real quota pool is available.
    """
    if DEFAULT_STORAGE_POOL == FALLBACK_STORAGE_POOL:
        return  # no enforced pool available, nothing we can do
    target = DEFAULT_STORAGE_POOL

    for user_id, vps_list in list(vps_data.items()):
        for vps in list(vps_list):
            container = vps.get('container_name')
            if not container:
                continue
            try:
                rc, out, _ = await _run_cmd(
                    "lxc", "config", "device", "get", container, "root", "pool", timeout=15
                )
                pool = out.strip() if rc == 0 else ""
            except Exception:
                continue
            if not pool or pool == target:
                continue

            logger.warning(f"Container '{container}' is on non-enforced pool '{pool}' — migrating to '{target}'...")
            try:
                was_running = vps.get('status') == 'running' and not vps.get('suspended', False)
                if was_running:
                    await execute_lxc(f"lxc stop {shlex.quote(container)} --timeout 60", timeout=120)
                await execute_lxc(f"lxc move {shlex.quote(container)} -s {target}", timeout=1800)
                if was_running:
                    await execute_lxc(f"lxc start {shlex.quote(container)}", timeout=120)
                logger.info(f"Migrated '{container}' to quota pool '{target}'")
            except Exception as e:
                logger.error(f"Failed to migrate '{container}' to '{target}': {e}")
    save_vps_data()

async def _host_nat_fix():
    """Ensure forwarding + masquerade for the REAL lxdbr0 subnet (idempotent)."""
    await _run_host_shell("sysctl -w net.ipv4.ip_forward=1 >/dev/null 2>&1 || true")
    subnet = await _get_lxdbr0_subnet()
    if not subnet:
        logger.warning("Could not determine lxdbr0 subnet for NAT fix")
        return
    script = f"""
IPT=$(command -v iptables 2>/dev/null || echo /sbin/iptables)
$IPT -t nat -C POSTROUTING -s {subnet} ! -d {subnet} -j MASQUERADE 2>/dev/null || \
    $IPT -t nat -A POSTROUTING -s {subnet} ! -d {subnet} -j MASQUERADE 2>/dev/null || true
$IPT -C FORWARD -i lxdbr0 -j ACCEPT 2>/dev/null || $IPT -A FORWARD -i lxdbr0 -j ACCEPT 2>/dev/null || true
$IPT -C FORWARD -o lxdbr0 -j ACCEPT 2>/dev/null || $IPT -A FORWARD -o lxdbr0 -j ACCEPT 2>/dev/null || true
"""
    ok = await _run_host_shell(script)
    logger.info(f"Host NAT fix for {subnet}: {'ok' if ok else 'failed'}")

async def ensure_container_tools(container_name):
    """Install curl/wget/ca-certificates inside the container if missing."""
    rc, _, _ = await _container_shell(container_name, "command -v curl", timeout=15)
    if rc == 0:
        return True
    script = (
        "export DEBIAN_FRONTEND=noninteractive; "
        "(apt-get update -qq >/dev/null 2>&1 || true); "
        "(apt-get install -y -qq curl wget ca-certificates >/dev/null 2>&1 || "
        "dnf install -y curl wget ca-certificates >/dev/null 2>&1 || "
        "yum install -y curl wget ca-certificates >/dev/null 2>&1 || true); "
        "command -v curl"
    )
    rc, _, _ = await _container_shell(container_name, script, timeout=300)
    return rc == 0

_INTERNET_PROBE_SCRIPT = r'''
probe_url() {
    if command -v curl >/dev/null 2>&1; then
        curl -fsS --connect-timeout 8 -m 15 -o /dev/null "$1" 2>/dev/null && { echo curl; return 0; }
    fi
    if command -v wget >/dev/null 2>&1; then
        wget -q -T 10 -O /dev/null "$1" 2>/dev/null && { echo wget; return 0; }
    fi
    if command -v python3 >/dev/null 2>&1; then
        python3 -c 'import urllib.request,sys; urllib.request.urlopen(sys.argv[1], timeout=12)' "$1" 2>/dev/null && { echo python3; return 0; }
    fi
    if command -v python >/dev/null 2>&1; then
        python -c 'import urllib2,sys; urllib2.urlopen(sys.argv[1], timeout=12)' "$1" 2>/dev/null && { echo python; return 0; }
    fi
    return 1
}
for url in https://github.com https://google.com https://deb.debian.org; do
    probe_url "$url" && exit 0
done
if (exec 3<>/dev/tcp/1.1.1.1/443) 2>/dev/null; then echo tcp; exit 0; fi
exit 1
'''

async def _container_shell(container_name, script, timeout=30):
    """Run a shell script inside a container without shell-quoting pitfalls.

    Prefers bash but transparently falls back to sh on images where bash is
    missing, so internet/disk checks never give false negatives.
    """
    last = (1, "", "no shell available")
    for shell in ("bash", "sh"):
        try:
            proc = await asyncio.create_subprocess_exec(
                "lxc", "exec", container_name, "--", shell, "-c", script,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            try:
                proc.kill()
                await proc.wait()
            except Exception:
                pass
            return 1, "", "timeout"
        except Exception as e:
            return 1, "", str(e)
        out_str = stdout.decode(errors="replace")
        err_str = stderr.decode(errors="replace")
        last = (proc.returncode, out_str, err_str)
        if proc.returncode != 0 and shell == "bash":
            low = err_str.lower()
            if "not found" in low or "executable file not found" in low or "no such file" in low:
                continue  # bash missing -> retry with sh
        return last
    return last

async def check_container_internet(container_name):
    """True when the container can actually reach the internet.

    Tries curl, wget, python, then a raw TCP connect, so images without curl
    (fresh debian/ubuntu) are no longer reported as 'No Internet'.
    """
    try:
        rc, out, _ = await _container_shell(container_name, _INTERNET_PROBE_SCRIPT, timeout=60)
        if rc == 0:
            logger.info(f"Internet check OK for {container_name} via {out.strip() or 'probe'}")
            return True
        return False
    except Exception as e:
        logger.warning(f"Internet check error for {container_name}: {e}")
        return False

async def _run_internet_fix(container_name):
    try:
        try:
            proc = await asyncio.create_subprocess_exec(
                "lxc", "info", container_name, "--format", "json",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=15)
            info = json.loads(stdout)
            if info.get("status", "").lower() != "running":
                logger.info(f"{container_name} is not running, starting it...")
                await execute_lxc(f"lxc start {shlex.quote(container_name)}", timeout=60)
                await asyncio.sleep(5)
        except Exception:
            logger.warning(f"Could not check/start {container_name}, continuing anyway")

        await ensure_lxdbr0()

        try:
            await execute_lxc("lxc profile device add default eth0 nic nictype=bridged parent=lxdbr0", timeout=30)
        except Exception:
            pass

        has_eth0 = False
        try:
            proc = await asyncio.create_subprocess_exec(
                "lxc", "config", "device", "get", container_name, "eth0", "nictype",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            out, _ = await proc.communicate()
            has_eth0 = proc.returncode == 0
        except Exception:
            pass

        if not has_eth0:
            await execute_lxc(f"lxc config device add {shlex.quote(container_name)} eth0 nic nictype=bridged parent=lxdbr0", timeout=30)
            await asyncio.sleep(2)

        try:
            await execute_lxc("sysctl -w net.ipv4.ip_forward=1", timeout=10)
        except Exception:
            pass

        await _host_nat_fix()

        dns_ok = False
        try:
            await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- resolvectl dns eth0 8.8.8.8 8.8.4.4", timeout=10)
            dns_ok = True
        except Exception:
            pass
        if not dns_ok:
            try:
                await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- bash -c \"rm -f /etc/resolv.conf && echo 'nameserver 8.8.8.8' > /etc/resolv.conf && echo 'nameserver 1.1.1.1' >> /etc/resolv.conf\"", timeout=10)
                dns_ok = True
            except Exception:
                pass
        if not dns_ok:
            try:
                await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- bash -c \"sed -i 's/nameserver.*/nameserver 8.8.8.8/' /etc/resolv.conf 2>/dev/null; grep -q '8.8.8.8' /etc/resolv.conf || echo 'nameserver 8.8.8.8' >> /etc/resolv.conf\"", timeout=10)
            except Exception:
                pass

        await ensure_container_tools(container_name)

        try:
            await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- bash -c \"ip link set eth0 up 2>/dev/null || true\"", timeout=10)
        except Exception:
            pass

        return True
    except Exception:
        return False

async def ensure_container_internet(container_name, msg=None, max_retries=3):
    async def _progress(text, color=0xffaa00):
        if msg:
            embed = discord.Embed(
                title=f"{EMOJI_STAR} Fixing Internet - {container_name}",
                description=text,
                color=color
            )
            if THUMBNAIL_URL:
                embed.set_thumbnail(url=THUMBNAIL_URL)
            embed.set_footer(text=f"{BOT_NAME} | Configuring network...", icon_url=THUMBNAIL_URL)
            try:
                await msg.edit(embed=embed)
            except Exception:
                pass

    for attempt in range(1, max_retries + 1):
        if await check_container_internet(container_name):
            await _progress(f"{EMOJI_ONLINE} Internet is working", 0x00ff88)
            return True

        await _progress(f"{EMOJI_GLOBAL} Internet fix attempt {attempt}/{max_retries}...")
        ok = await _run_internet_fix(container_name)
        if not ok:
            await _progress(f"{EMOJI_WARNING} Fix attempt {attempt} failed, retrying...", 0xffaa00)
            await asyncio.sleep(3)
            continue

        await _progress(f"{EMOJI_LOADING} Testing connectivity (attempt {attempt})...")
        for _ in range(4):
            if await check_container_internet(container_name):
                await _progress(f"{EMOJI_ONLINE} Internet connected", 0x00ff88)
                return True
            await asyncio.sleep(3)

    if await check_container_internet(container_name):
        await _progress(f"{EMOJI_ONLINE} Internet connected", 0x00ff88)
        return True

    await _progress(f"{EMOJI_MID_SIGNAL} Could not verify internet", 0xffaa00)
    return False

async def fix_container_internet(container_name, msg=None):
    return await ensure_container_internet(container_name, msg=msg, max_retries=3)

# ==================================================== LXC CONFIGURATION END =====================================================

# ==================================================== CONTAINER STATS FUNCTIONS =====================================================

async def get_container_status(container_name):
    try:
        proc = await asyncio.create_subprocess_exec(
            "lxc", "info", container_name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        output = stdout.decode()
        for line in output.splitlines():
            if line.startswith("Status: "):
                return line.split(": ", 1)[1].strip().lower()
        return "unknown"
    except Exception:
        return "unknown"

async def get_container_cpu(container_name):
    try:
        proc = await asyncio.create_subprocess_exec(
            "lxc", "exec", container_name, "--", "top", "-bn1",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        output = stdout.decode()
        for line in output.splitlines():
            if '%Cpu(s):' in line:
                parts = line.split()
                us = float(parts[1])
                sy = float(parts[3])
                ni = float(parts[5])
                id_ = float(parts[7])
                wa = float(parts[9])
                hi = float(parts[11])
                si = float(parts[13])
                st = float(parts[15])
                usage = us + sy + ni + wa + hi + si + st
                return f"{usage:.1f}%"
        return "0.0%"
    except Exception:
        return "N/A"

async def get_container_memory(container_name):
    try:
        proc = await asyncio.create_subprocess_exec(
            "lxc", "exec", container_name, "--", "free", "-m",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        lines = stdout.decode().splitlines()
        if len(lines) > 1:
            parts = lines[1].split()
            total = int(parts[1])
            used = int(parts[2])
            usage_pct = (used / total * 100) if total > 0 else 0
            return f"{used}/{total} MB ({usage_pct:.1f}%)"
        return "Unknown"
    except Exception:
        return "N/A"

def _format_bytes(num):
    """Human readable byte size (e.g. 1.5G)."""
    try:
        num = float(num)
    except (TypeError, ValueError):
        return "0B"
    for unit in ("B", "K", "M", "G", "T", "P"):
        if abs(num) < 1024.0:
            return f"{num:.0f}{unit}" if unit == "B" else f"{num:.1f}{unit}"
        num /= 1024.0
    return f"{num:.1f}E"

async def _container_rootfs_path(container_name):
    """Return the on-host rootfs path for a container, or None."""
    try:
        rc, pool, _ = await _run_cmd("lxc", "config", "device", "get", container_name, "root", "pool", timeout=10)
        if rc != 0 or not pool:
            pool = DEFAULT_STORAGE_POOL
        rc, src, _ = await _run_cmd("lxc", "storage", "get", pool, "source", timeout=10)
        if rc == 0 and src:
            return f"{src}/containers/{container_name}/rootfs"
    except Exception:
        pass
    return None

async def get_container_disk_info(container_name):
    """Return (usage_bytes, total_bytes) for a container's root disk.

    Uses the LXD state API which reports the quota-enforced limit and the
    writable usage for any storage driver (zfs, btrfs, lvm, dir). Falls back to
    measuring the rootfs, then to df inside the container.
    """
    # 1) Preferred: LXD state API (accurate + enforced limit, any driver)
    try:
        rc, out, _ = await _run_cmd(
            "lxc", "query", f"/1.0/instances/{container_name}/state", timeout=20)
        if rc == 0 and out:
            data = json.loads(out)
            root = (data.get("disk") or {}).get("root") or {}
            total = int(root.get("total") or 0)
            usage = int(root.get("usage") or 0)
            if usage > 0:
                return usage, total
    except Exception:
        pass

    # 2) Fallback: measure the container rootfs directory on the host
    try:
        path = await _container_rootfs_path(container_name)
        if path:
            rc, out, _ = await _run_cmd("du", "-sb", path, timeout=60)
            if rc == 0 and out:
                usage = int(out.split()[0])
                total = 0
                rc2, out2, _ = await _run_cmd(
                    "lxc", "query", f"/1.0/instances/{container_name}/state", timeout=20)
                if rc2 == 0 and out2:
                    root = (json.loads(out2).get("disk") or {}).get("root") or {}
                    total = int(root.get("total") or 0)
                return usage, total
    except Exception:
        pass

    # 3) Last resort: df inside the container
    try:
        rc, out, _ = await _container_shell(container_name, "df -B1 --output=used,size / | tail -1", timeout=20)
        if rc == 0 and out.strip():
            parts = out.split()
            if len(parts) >= 2:
                return int(parts[0]), int(parts[1])
    except Exception:
        pass
    return 0, 0

async def get_container_disk(container_name):
    usage, total = await get_container_disk_info(container_name)
    if total <= 0:
        return "Unknown"
    pct = (usage / total * 100) if total > 0 else 0
    return f"{_format_bytes(usage)}/{_format_bytes(total)} ({pct:.1f}%)"

async def get_container_uptime(container_name):
    try:
        proc = await asyncio.create_subprocess_exec(
            "lxc", "exec", container_name, "--", "cat", "/proc/uptime",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        parts = stdout.decode().strip().split()
        if not parts:
            return "Unknown"
        uptime_secs = parts[0]
        return format_uptime_str(uptime_secs)
    except Exception:
        return "Unknown"

async def get_container_logs(container_name, lines=50):
    try:
        proc = await asyncio.create_subprocess_exec(
            "lxc", "exec", container_name, "--", "journalctl", "-n", str(lines), "--no-pager",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        return stdout.decode().strip() if stdout else "No logs available"
    except Exception:
        return "Unable to fetch logs"

async def get_uptime():
    try:
        proc = await asyncio.create_subprocess_exec(
            "uptime",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        return stdout.decode().strip() if stdout else "Unknown"
    except Exception:
        return "Unknown"

def format_uptime_str(seconds_str):
    try:
        seconds = int(float(seconds_str.strip()))
        days = seconds // 86400
        seconds %= 86400
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        secs = seconds % 60
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{secs}s")
        return " ".join(parts)
    except Exception:
        return "Unknown"

async def get_container_stats_batch(container_name):
    try:
        proc = await asyncio.create_subprocess_exec(
            "lxc", "exec", container_name, "--", "sh", "-c",
            "cat /proc/uptime && free -m | grep Mem && df -h / | tail -1 && LANG=C top -bn1 -d0.05 2>/dev/null | grep '^%Cpu'",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        raw_stdout = stdout.decode() if stdout else ""
        lines = raw_stdout.strip().splitlines()

        uptime_str = "Unknown"
        mem_str = "N/A"
        disk_str = "N/A"
        cpu_str = "0.0%"

        if lines:
            uptime_secs = lines[0].split()[0] if lines[0].strip() else "0"
            uptime_str = format_uptime_str(uptime_secs)

        if len(lines) > 1:
            mem_parts = lines[1].split()
            if len(mem_parts) >= 3:
                total = int(mem_parts[1])
                used = int(mem_parts[2])
                mem_str = f"{used}/{total} MB ({used/total*100:.1f}%)"

        if len(lines) > 2:
            # df can be misleading on some drivers (shows base image + quota);
            # use the accurate LXD-reported usage/limit instead.
            disk_str = await get_container_disk(container_name)

        # Prefer host cgroup CPU via lxc info (more accurate)
        host_cpu = await get_container_cpu(container_name)
        if host_cpu:
            cpu_str = host_cpu
        elif len(lines) > 3:
            cpu_line = lines[3].replace(',', ' ')
            if '%Cpu' in cpu_line:
                cpu_parts = cpu_line.split()
                if len(cpu_parts) >= 16:
                    us = float(cpu_parts[1])
                    sy = float(cpu_parts[3])
                    ni = float(cpu_parts[5])
                    wa = float(cpu_parts[9])
                    hi = float(cpu_parts[11])
                    si = float(cpu_parts[13])
                    st = float(cpu_parts[15])
                    cpu_str = f"{us + sy + ni + wa + hi + si + st:.1f}%"

        return cpu_str, mem_str, disk_str, uptime_str
    except Exception:
        return "N/A", "N/A", "N/A", "Unknown"

# ==================================================== CONTAINER STATS FUNCTIONS END =====================================================

# ==================================================== BOT EVENTS =====================================================

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    
    await _apply_bot_presence()
    
    # Cache invites for all guilds to prevent race condition on member join
    for guild in bot.guilds:
        await cache_invites(guild)

    # Start remote-node status refresher (multi-node management)
    if not getattr(bot, '_node_refresh_task', None):
        bot._node_refresh_task = bot.loop.create_task(node_refresh_loop())

    # Start heartbeat latency sampler (for accurate $ping reporting)
    if not getattr(bot, '_ws_latency_task', None):
        bot._ws_latency_task = bot.loop.create_task(ws_latency_sampler_loop())

    # Start disk-full monitor for node VPS
    if not getattr(bot, '_node_disk_task', None):
        bot._node_disk_task = bot.loop.create_task(node_disk_monitor_loop())

    # Auto-suspend expired node VPS + auto-delete after grace period (like bot.py)
    if not getattr(bot, '_node_expiry_task', None):
        bot._node_expiry_task = bot.loop.create_task(check_expired_node_vps())
    if not getattr(bot, '_node_autodelete_task', None):
        bot._node_autodelete_task = bot.loop.create_task(auto_delete_node_vps())

    logger.info(f"{BOT_NAME} Bot is ready!")

@bot.event
async def on_resumed():
    # Re-apply the saved presence after a gateway resume, otherwise the bot can
    # silently fall back to "online" and forget the selected mode/activity.
    await _apply_bot_presence()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=create_error_embed("Missing Argument", f"Please check command usage with `{PREFIX}help`."))
    elif isinstance(error, commands.BadArgument):
        await ctx.send(embed=create_error_embed("Invalid Argument", "Please check your input and try again."))
    elif isinstance(error, commands.CheckFailure):
        error_msg = str(error) if str(error) else "You need admin permissions for this command."
        await ctx.send(embed=create_error_embed("Access Denied", error_msg))
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(embed=create_warning_embed("Command on Cooldown", f"Please wait {error.retry_after:.2f} seconds before using this command again."))
    else:
        logger.error(f"Command error: {error}")
        await ctx.send(embed=create_error_embed("System Error", "An unexpected error occurred."))

# ==================================================== BOT EVENTS END =====================================================

# ==================================================== INVITE/BOOST TRACKING EVENTS =====================================================

@bot.event
async def on_invite_create(invite):
    if not invite.guild:
        return
    conn = get_db()
    try:
        cur = conn.cursor()
        inviter_id = str(invite.inviter.id) if invite.inviter else 'unknown'
        cur.execute('INSERT INTO invite_codes (code, inviter_id, created_at, max_uses, uses) VALUES (?, ?, ?, ?, ?)',
                    (invite.code, inviter_id, datetime.now().isoformat(), invite.max_uses, invite.uses))
        conn.commit()
    finally:
        conn.close()
    if invite.guild.id in _invite_cache:
        _invite_cache[invite.guild.id][invite.code] = invite

@bot.event
async def on_invite_delete(invite):
    if invite.guild and invite.guild.id in _invite_cache:
        _invite_cache[invite.guild.id].pop(invite.code, None)

@bot.event
async def on_member_join(member):
    guild = member.guild
    if not guild:
        return
    try:
        invites_after = await guild.invites()
        invites_after_dict = {inv.code: inv for inv in invites_after}
        cached = _invite_cache.get(guild.id, {})
        inviter_id = None
        used_code = None

        deltas = []
        for code, after_inv in invites_after_dict.items():
            before_inv = cached.get(code)
            if before_inv:
                d = after_inv.uses - before_inv.uses
                if d > 0:
                    deltas.append((d, code, after_inv))
        if deltas:
            deltas.sort(key=lambda x: x[0])
            best = next(((c, i) for d, c, i in deltas if d == 1), None)
            if not best:
                best = (deltas[0][1], deltas[0][2])
            used_code = best[0]
            inviter_id = str(best[1].inviter.id) if best[1].inviter else None

        if not inviter_id or inviter_id == 'vanity':
            for code, after_inv in invites_after_dict.items():
                if code not in cached and after_inv.uses > 0:
                    inviter_id = str(after_inv.inviter.id) if after_inv.inviter else None
                    used_code = code
                    break

        if not inviter_id:
            try:
                vanity = await guild.vanity_invite()
                if vanity:
                    inviter_id = 'vanity'
                    used_code = vanity.code
            except:
                pass

        if not inviter_id:
            try:
                async for entry in guild.audit_logs(action=discord.AuditLogAction.invite_create, limit=5):
                    if entry.user and not entry.user.bot:
                        entry_time = entry.created_at.replace(tzinfo=None) if entry.created_at.tzinfo else entry.created_at
                        if (datetime.utcnow() - entry_time).total_seconds() < 15:
                            inviter_id = str(entry.user.id)
                            used_code = "audit"
                            break
            except:
                pass

        _invite_cache[guild.id] = invites_after_dict

        conn = get_db()
        conn_closed = False
        try:
            cur = conn.cursor()
            if inviter_id and inviter_id != 'vanity':
                cur.execute('''INSERT INTO invite_logs (code, inviter_id, user_id, user_name, action, created_at)
                               VALUES (?, ?, ?, ?, ?, ?)''',
                            (used_code, inviter_id, str(member.id), member.name, 'joined', datetime.now().isoformat()))
                conn.commit()
                conn.close()
                conn_closed = True
                update_user_stats(inviter_id, invites=1)
                await send_log(EMOJI_USER, "Member Joined via Invite",
                    f"{EMOJI_USER} **User:** {member.mention} (`{member.id}`)\n"
                    f"{EMOJI_ARROW_RIGHT} **Invited by:** <@{inviter_id}>\n"
                    f"{EMOJI_ARROW_RIGHT} **Invite Code:** `{used_code}`\n"
                    f"{EMOJI_ARROW_RIGHT} **Account Created:** {member.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
                    color=0x00ff88)
                await send_tracking(EMOJI_USER, "Invite Used",
                    f"{EMOJI_USER} **User:** {member.mention} (`{member.id}`)\n"
                    f"{EMOJI_ARROW_RIGHT} **Invited by:** <@{inviter_id}>\n"
                    f"{EMOJI_ARROW_RIGHT} **Invite Code:** `{used_code}`",
                    color=0x00ff88)
            else:
                cur.execute('''INSERT INTO invite_logs (code, inviter_id, user_id, user_name, action, created_at)
                               VALUES (?, ?, ?, ?, ?, ?)''',
                            (used_code or 'unknown', 'unknown', str(member.id), member.name, 'joined', datetime.now().isoformat()))
                conn.commit()
                conn.close()
                conn_closed = True
        finally:
            if not conn_closed:
                conn.close()
    except Exception as e:
        logger.error(f"Error tracking member join: {e}")

@bot.event
async def on_member_remove(member):
    guild = member.guild
    if not guild:
        return
    conn = get_db()
    conn_closed = False
    try:
        cur = conn.cursor()
        cur.execute('SELECT inviter_id, code FROM invite_logs WHERE user_id = ? AND action = ? ORDER BY created_at DESC LIMIT 1',
                    (str(member.id), 'joined'))
        row = cur.fetchone()
        if row:
            inviter_id = row[0]
            code = row[1]
            cur.execute('''INSERT INTO invite_logs (code, inviter_id, user_id, user_name, action, created_at)
                           VALUES (?, ?, ?, ?, ?, ?)''',
                        (code, inviter_id, str(member.id), member.name, 'left', datetime.now().isoformat()))
            conn.commit()
            conn.close()
            conn_closed = True
            update_user_stats(inviter_id, invites=-1)
            await send_log(EMOJI_USER, "Member Left",
                f"{EMOJI_USER} **User:** {member.name} (`{member.id}`)\n"
                f"{EMOJI_ARROW_RIGHT} **Was invited by:** <@{inviter_id}>\n"
                f"{EMOJI_ARROW_RIGHT} **Invite Code:** `{code}`",
                color=0xff3366)
            await send_tracking(EMOJI_USER, "Member Left",
                f"{EMOJI_USER} **User:** {member.name} (`{member.id}`)\n"
                f"{EMOJI_ARROW_RIGHT} **Was invited by:** <@{inviter_id}>\n"
                f"{EMOJI_ARROW_RIGHT} **Invite Code:** `{code}`",
                color=0xff3366)
        else:
            conn.close()
            conn_closed = True
    except Exception as e:
        logger.error(f"Error tracking member remove: {e}")
        if not conn_closed:
            try:
                conn.close()
            except:
                pass

_recent_boost_events = {}

@bot.event
async def on_member_update(before, after):
    if before.premium_since != after.premium_since:
        user_id = str(after.id)
        now = time.time()
        last_seen = _recent_boost_events.get(user_id, 0)
        if now - last_seen < 60:
            return
        _recent_boost_events[user_id] = now

        conn = get_db()
        conn_closed = False
        try:
            cur = conn.cursor()
            if after.premium_since and not before.premium_since:
                cur.execute('''INSERT INTO boost_logs (user_id, user_name, action, created_at)
                               VALUES (?, ?, ?, ?)''',
                            (user_id, after.name, 'boosted', datetime.now().isoformat()))
                conn.commit()
                conn.close()
                conn_closed = True
                update_user_stats(user_id, boosts=1)
                await send_log(EMOJI_STAR, "Server Boosted!",
                    f"{EMOJI_USER} **User:** {after.mention} (`{user_id}`)\n"
                    f"{EMOJI_ARROW_RIGHT} **Action:** Started boosting!",
                    color=0xff73fa)
                await send_tracking(EMOJI_STAR, "Server Boosted!",
                    f"{EMOJI_USER} **User:** {after.mention} (`{user_id}`)\n"
                    f"{EMOJI_ARROW_RIGHT} **Action:** Started boosting!",
                    color=0xff73fa)
            elif before.premium_since and not after.premium_since:
                cur.execute('''INSERT INTO boost_logs (user_id, user_name, action, created_at)
                               VALUES (?, ?, ?, ?)''',
                            (user_id, after.name, 'unboosted', datetime.now().isoformat()))
                conn.commit()
                conn.close()
                conn_closed = True
                stats = get_user_stats(user_id)
                current_boosts = stats.get('boosts', 0)
                if current_boosts > 0:
                    update_user_stats(user_id, boosts=-1)
                await send_log(EMOJI_CROSS, "Boost Removed",
                    f"{EMOJI_USER} **User:** {after.mention} (`{user_id}`)\n"
                    f"{EMOJI_ARROW_RIGHT} **Action:** Stopped boosting!",
                    color=0xff3366)
                await send_tracking(EMOJI_CROSS, "Boost Removed",
                    f"{EMOJI_USER} **User:** {after.mention} (`{user_id}`)\n"
                    f"{EMOJI_ARROW_RIGHT} **Action:** Stopped boosting!",
                    color=0xff3366)
            else:
                conn.close()
                conn_closed = True
        except Exception as e:
            logger.error(f"Error tracking member update: {e}")
            if not conn_closed:
                try:
                    conn.close()
                except:
                    pass

# ==================================================== INVITE/BOOST TRACKING EVENTS END =====================================================

# ==================================================== USER COMMANDS =====================================================

@bot.command(name='ping')
@commands.cooldown(1, 3, commands.BucketType.user)
async def ping(ctx, node_id: str = None):
    """Check bot latency, or a node's latency: ping [node-name]"""
    if not await maintenance_check(ctx):
        return

    if node_id:
        n = node_resolve(node_id)
        if not n:
            await ctx.send(embed=create_error_embed("Not Found", f"No node with name `{node_id}`."))
            return
        node_id = n['node_id']
        node_label = node_display_name(n)
        start = time.perf_counter()
        try:
            info = await node_client(n).info()
        except NodeError as e:
            node_set_status(node_id, False)
            await ctx.send(embed=create_error_embed("Node Offline", f"`{node_label}`\n```{e}```"))
            return
        node_set_status(node_id, True, info)
        latency = (time.perf_counter() - start) * 1000
        embed = create_success_embed("Pong!", f"{EMOJI_GOOD_SIGNAL} `{node_label}` responded in `{latency:.0f} ms`")
        add_field(embed, f"{EMOJI_VPS} Containers", f"`{info.get('containers', {}).get('running', '?')}` running", True)
        add_field(embed, f"{EMOJI_UPTIME} Uptime", f"`{info.get('uptime', 'unknown')}`", True)
        await ctx.send(embed=embed)
        return

    # Current heartbeat sample (record it too, in case the sampler hasn't yet)
    await sample_ws_latency()
    ws_now = bot.latency * 1000 if bot.latency and bot.latency == bot.latency else None
    if _WS_LATENCY_HISTORY:
        ws_avg = sum(_WS_LATENCY_HISTORY) / len(_WS_LATENCY_HISTORY)
        ws_min = min(_WS_LATENCY_HISTORY)
        ws_max = max(_WS_LATENCY_HISTORY)
    else:
        ws_avg = ws_min = ws_max = None

    # Live Discord API round-trip + database latency (run in parallel)
    db_start = time.perf_counter()
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT 1')
    cur.fetchone()
    conn.close()
    db_latency = (time.perf_counter() - db_start) * 1000

    api_rtt = await measure_discord_api_rtt()

    embed = create_ping_embed(
        ws_now if ws_now is not None else 0.0,
        ws_avg, ws_min, ws_max,
        api_rtt, db_latency, len(_WS_LATENCY_HISTORY)
    )
    await ctx.send(embed=embed)

@bot.command(name='uptime')
@commands.cooldown(1, 5, commands.BucketType.user)
async def uptime(ctx, node_id: str = None):
    """Show uptime: uptime <node-name> | uptime bot"""
    if not await maintenance_check(ctx):
        return

    if not node_id:
        await ctx.send(embed=create_error_embed("Missing Argument",
            f"Usage: `{PREFIX}uptime <node-name>` or `{PREFIX}uptime bot` — see `{PREFIX}node-list`"))
        return

    if node_id.lower() in ('bot', 'self'):
        secs = int(time.time() - BOT_START_TIME)
        up_str = format_uptime_str(str(secs))
        embed = create_info_embed(f"{EMOJI_UPTIME} Bot Uptime", f"`{up_str}`")
        add_field(embed, "PID", f"`{os.getpid()}`", True)
        add_field(embed, "Node", f"`{BOT_NAME}`", True)
        await ctx.send(embed=embed)
        return

    n = node_resolve(node_id)
    if not n:
        await ctx.send(embed=create_error_embed("Not Found", f"No node with name `{node_id}`."))
        return
    node_id = n['node_id']
    node_label = node_display_name(n)
    try:
        info = await asyncio.wait_for(node_client(n).info(), timeout=5)
        node_set_status(node_id, True, info)
    except asyncio.TimeoutError:
        node_set_status(node_id, False)
        await ctx.send(embed=create_error_embed("Node Offline", f"`{node_label}` API is unreachable or offline."))
        return
    except NodeError as e:
        node_set_status(node_id, False)
        await ctx.send(embed=create_error_embed("Node Offline", f"`{node_label}`\n```{e}```"))
        return
    embed = create_info_embed(f"Node {node_label} Uptime", f"{EMOJI_UPTIME} `{info.get('uptime', 'unknown')}`")
    add_field(embed, "Hostname", f"`{info.get('hostname', '?')}`", True)
    add_field(embed, f"{EMOJI_VPS} Containers",
              f"`{info.get('containers', {}).get('running', '?')}` running", True)
    await ctx.send(embed=embed)

@bot.command(name='plans')
@commands.cooldown(1, 5, commands.BucketType.user)
async def show_plans(ctx):
    """View free VPS plans with emojis"""
    if not await maintenance_check(ctx):
        return
    
    embed = discord.Embed(
        title=f"{EMOJI_STAR} {BOT_NAME} - Free VPS Plans",
        description="───────────────\nEarn FREE VPS plans by invites or server boosts",
        color=0xffaa00
    )
    
    # Invite-based plans with emojis
    invite_text = ""
    for i, plan in enumerate(FREE_VPS_PLANS['invites'], 1):
        plan_time = parse_time_string(plan.get('time', ''))
        time_str = format_timedelta(plan_time) if plan_time else "None"
        invite_text += f"**{plan['emoji']} {plan['name']}**\n"
        invite_text += f"  • RAM: {plan['ram']} GB\n"
        invite_text += f"  • CPU: {plan['cpu']} Cores\n"
        invite_text += f"  • Storage: {plan['disk']} GB\n"
        invite_text += f"  • Requires: {plan['invites']} Invites\n"
        invite_text += f"  {EMOJI_UPTIME} Duration: {time_str}\n\n"
    
    embed.add_field(name="📨 Invite Rewards", value=invite_text, inline=True)
    
    # Boost-based plans with emojis
    boost_text = ""
    for i, plan in enumerate(FREE_VPS_PLANS['boosts'], 1):
        plan_time = parse_time_string(plan.get('time', ''))
        time_str = format_timedelta(plan_time) if plan_time else "None"
        boost_text += f"**{plan['emoji']} {plan['name']}**\n"
        boost_text += f"  • RAM: {plan['ram']} GB\n"
        boost_text += f"  • CPU: {plan['cpu']} Cores\n"
        boost_text += f"  • Storage: {plan['disk']} GB\n"
        boost_text += f"  • Requires: {plan['boosts']} Boost{'s' if plan['boosts'] > 1 else ''}\n"
        boost_text += f"  {EMOJI_UPTIME} Duration: {time_str}\n\n"
    
    embed.add_field(name="🚀 Boost Rewards", value=boost_text, inline=True)
    
    embed.add_field(name="───────────────", 
                   value=f"📌 **How to Claim:**\n"
                         f"• `{PREFIX}claimfree inv <1-6>` - Claim invite VPS\n"
                         f"• `{PREFIX}claimfree boost <1-5>` - Claim boost VPS\n"
                         f"• Check your stats with `{PREFIX}stats`", 
                   inline=False)
    
    # Set thumbnail if URL is provided
    if THUMBNAIL_URL:
        embed.set_thumbnail(url=THUMBNAIL_URL)
    
    # Set footer with timestamp and icon
    embed.set_footer(
        text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        icon_url=THUMBNAIL_URL
    )
    
    await ctx.send(embed=embed)

@bot.command(name='freeplans')
@commands.cooldown(1, 5, commands.BucketType.user)
async def free_plans(ctx):
    """Free Plans List"""
    if not await maintenance_check(ctx):
        return
    await show_plans(ctx)

@bot.command(name='stats')
@commands.cooldown(1, 5, commands.BucketType.user)
async def user_stats(ctx, vps_id: int = None):
    """View your invite/boost stats, or a VPS's stats: stats [vps-id]"""
    if not await maintenance_check(ctx):
        return

    if vps_id is not None:
        await _remote_vps_op(ctx, 'stats', vps_id)
        return

    user_id = str(ctx.author.id)
    stats = get_user_stats(user_id)
    
    embed = create_info_embed(f"📊 {ctx.author.name}'s Stats", f"Your current statistics")
    
    add_field(embed, "📨 Invites", str(stats.get('invites', 0)), True)
    add_field(embed, "🚀 Boosts", str(stats.get('boosts', 0)), True)
    add_field(embed, "🖥️ VPS Owned", str(len(node_vps_user(ctx.author.id))), True)
    add_field(embed, "🎁 Claimed VPS", str(stats.get('claimed_vps_count', 0)), True)
    
    await ctx.send(embed=embed)

@bot.command(name='claimfree')
@commands.cooldown(1, 30, commands.BucketType.user)
async def claim_free_vps(ctx, reward_type: str = None, plan_number: int = None):
    """Claim a free VPS based on invites or boosts
    Usage: 
    .claimfree inv <1-6> - Claim invite-based VPS
    .claimfree boost <1-5> - Claim boost-based VPS
    """
    if FREE_VPS_STATUS.lower() not in ('yes', 'true', '1'):
        await ctx.send(embed=create_error_embed("Free VPS Disabled",
            "Free VPS claiming is currently disabled."))
        return
    
    if not await maintenance_check(ctx):
        return

    if not free_vps_node():
        await ctx.send(embed=create_error_embed("Free VPS Node Not Configured",
            "Free VPS is enabled but `FREE_VPS_NODE` is not set in the bot config.\n"
            "Set the node endpoint + api-key, or disable free VPS."))
        return

    if not reward_type or not plan_number:
        embed = create_error_embed("Invalid Usage", 
            f"**Usage:**\n"
            f"• `{PREFIX}claimfree inv <1-6>` - Claim invite VPS\n"
            f"• `{PREFIX}claimfree boost <1-5>` - Claim boost VPS\n\n"
            f"Use `{PREFIX}plans` to see available plans.")
        await ctx.send(embed=embed)
        return
    
    user_id = str(ctx.author.id)
    stats = get_user_stats(user_id)
    
    # Check if user already has a VPS
    if node_vps_user(user_id):
        embed = create_error_embed("VPS Already Exists", 
            "You already have a VPS. Each user can only claim one free VPS.\n"
            "Contact an admin if you need additional VPS.")
        await ctx.send(embed=embed)
        return
    
    # Determine reward type
    reward_type = reward_type.lower()
    plan_category = None
    
    if reward_type in ['inv', 'invite', 'invites']:
        plan_category = 'invites'
        max_plans = len(FREE_VPS_PLANS['invites'])
        plan_type_name = "invite"
    elif reward_type in ['boost', 'boosts']:
        plan_category = 'boosts'
        max_plans = len(FREE_VPS_PLANS['boosts'])
        plan_type_name = "boost"
    else:
        embed = create_error_embed("Invalid Reward Type", 
            "Reward type must be: `inv` (invites) or `boost` (boosts)")
        await ctx.send(embed=embed)
        return
    
    # Check plan number
    if plan_number < 1 or plan_number > max_plans:
        embed = create_error_embed("Invalid Plan Number", 
            f"Plan number must be between 1 and {max_plans} for {plan_type_name} plans.\n"
            f"Use `{PREFIX}plans` to see available plans.")
        await ctx.send(embed=embed)
        return
    
    # Get the selected plan
    selected_plan = FREE_VPS_PLANS[plan_category][plan_number - 1]
    
    # Check if user meets requirements
    required = selected_plan.get(plan_category)
    current = stats.get(plan_category, 0)
    
    if current < required:
        embed = create_error_embed("Insufficient Requirements", 
            f"You need **{required} {plan_type_name}{'s' if required > 1 else ''}** to claim **{selected_plan['name']}**.\n"
            f"You currently have: **{current} {plan_type_name}{'s' if current > 1 else ''}**\n\n"
            f"**How to earn more {plan_type_name}s:**\n"
            f"• Invites: Invite users to the server\n"
            f"• Boosts: Boost the server with Nitro")
        await ctx.send(embed=embed)
        return
    
    # Verify the free-VPS node is reachable and has capacity before showing OS selection
    msg = await ctx.send(embed=create_info_embed("Checking Resources", f"{EMOJI_LOADING} Verifying node capacity..."))
    free_conf = free_vps_node()
    try:
        _fc = node_client(free_conf)
        _res = await _fc.check_resources()
        can_create = (selected_plan['cpu'] <= _res.get('cpu', {}).get('available', 0)
                      and selected_plan['ram'] <= _res.get('ram', {}).get('available_gb', 0)
                      and selected_plan['disk'] <= _res.get('disk', {}).get('available_gb', 0))
        error_msg = f"{EMOJI_WARNING} The free-VPS node is low on capacity. Please try again later."
    except NodeError as e:
        can_create = False
        error_msg = f"Free-VPS node unavailable: {e}"
    if not can_create:
        await msg.edit(embed=create_error_embed("Insufficient Resources", error_msg))
        return
    
    # Create OS selection view
    embed = create_info_embed("VPS Creation", 
        f"Claiming **{selected_plan['name']}** for {ctx.author.mention}\n"
        f"**RAM:** {selected_plan['ram']}GB\n"
        f"**CPU:** {selected_plan['cpu']} Cores\n"
        f"**Disk:** {selected_plan['disk']}GB\n"
        f"**Cost:** {required} {plan_type_name}{'s' if required > 1 else ''}\n\n"
        f"Select an OS below.")
    
    view = ClaimOSSelectView(selected_plan, plan_category, required, ctx)
    await msg.edit(embed=embed, view=view)

class ClaimOSSelectView(discord.ui.View):
    def __init__(self, plan, plan_category, required, ctx):
        super().__init__(timeout=300)
        self.plan = plan
        self.plan_category = plan_category
        self.required = required
        self.ctx = ctx
        self.selected_os = None
        
        options = []
        for o in OS_OPTIONS:
            emoji = o.get('emoji', '🐧')
            options.append(discord.SelectOption(label=o["label"], value=o["value"], emoji=emoji, description=o.get("description", "")))
        
        self.select = discord.ui.Select(
            placeholder="Select an OS for the VPS",
            options=options
        )
        self.select.callback = self.select_os
        self.add_item(self.select)
        cancel_btn = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger, row=1, emoji=EMOJI_CROSS)
        async def cancel_btn_cb(interaction: discord.Interaction):
            if str(interaction.user.id) != str(self.ctx.author.id):
                await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can cancel."), ephemeral=True)
                return
            await interaction.response.edit_message(embed=create_info_embed("Cancelled", "VPS creation cancelled."), view=None)
        cancel_btn.callback = cancel_btn_cb
        self.add_item(cancel_btn)
    
    async def select_os(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.ctx.author.id):
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can select."), ephemeral=True)
            return
        
        self.selected_os = self.select.values[0]
        await interaction.response.defer()
        
        confirm_view = discord.ui.View()
        confirm_button = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.success, emoji=EMOJI_SUCCESS)
        cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger, emoji=EMOJI_CROSS)
        
        async def confirm_callback(confirm_interaction):
            await self.create_vps(confirm_interaction)
        
        async def cancel_callback(cancel_interaction):
            if str(cancel_interaction.user.id) != str(self.ctx.author.id):
                await cancel_interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can cancel."), ephemeral=True)
                return
            await cancel_interaction.response.edit_message(embed=create_info_embed("Cancelled", "VPS creation cancelled."), view=None)
        
        confirm_button.callback = confirm_callback
        cancel_button.callback = cancel_callback
        
        confirm_view.add_item(confirm_button)
        confirm_view.add_item(cancel_button)
        
        embed = create_info_embed("Confirm VPS Creation", 
            f"**User:** {self.ctx.author.mention}\n"
            f"**Plan:** {self.plan['name']}\n"
            f"**OS:** {get_os_emoji(self.selected_os)} {self.selected_os}\n"
            f"**RAM:** {self.plan['ram']}GB\n"
            f"**CPU:** {self.plan['cpu']} Cores\n"
            f"**Disk:** {self.plan['disk']}GB\n"
            f"**Cost:** {self.required} {self.plan_category[:-1]}{'s' if self.required > 1 else ''}\n\n"
            f"Please confirm to proceed.")
        
        await interaction.edit_original_response(embed=embed, view=confirm_view)
    
    async def create_vps(self, interaction: discord.Interaction):
        await interaction.response.defer()

        user_id = str(self.ctx.author.id)
        allowed, limit_msg = check_vps_limit(user_id, is_paid=False)
        if not allowed:
            await interaction.edit_original_response(
                embed=create_error_embed("VPS Limit Reached", limit_msg), view=None)
            return

        if FREE_VPS_STATUS.lower() not in ('yes', 'true', '1'):
            await interaction.edit_original_response(
                embed=create_error_embed("Free VPS Disabled", "Free VPS claiming is currently disabled."), view=None)
            return

        free_conf = free_vps_node()
        if not free_conf:
            await interaction.edit_original_response(
                embed=create_error_embed("Free VPS Node Not Configured",
                    "Set `FREE_VPS_NODE` in the bot config (endpoint + api-key) or disable free VPS.\n"
                    "Example: `FREE_VPS_NODE = (\"https://domain.com\", \"api-key\")`"), view=None)
            return

        client = node_client(free_conf)
        try:
            h = await client.health()
        except NodeError as e:
            await interaction.edit_original_response(
                embed=create_error_embed("Free VPS Node Offline", f"`{free_conf['endpoint']}`\n```{e}```"), view=None)
            return

        node_id = h.get('node_id') or 'free-node'
        if not node_get(node_id):
            node_upsert(node_id, free_conf['endpoint'], free_conf['api_key'],
                        h.get('node_name', 'Free VPS Node'), 'free-config')

        try:
            res = await client.check_resources()
        except NodeError as e:
            await interaction.edit_original_response(
                embed=create_error_embed("Free VPS Node Offline", f"```{e}```"), view=None)
            return
        avail_cpu = res.get('cpu', {}).get('available', 0)
        avail_ram = res.get('ram', {}).get('available_gb', 0)
        avail_disk = res.get('disk', {}).get('available_gb', 0)
        if self.plan['cpu'] > avail_cpu or self.plan['ram'] > avail_ram or self.plan['disk'] > avail_disk:
            await interaction.edit_original_response(
                embed=create_error_embed("Insufficient Resources",
                    f"{EMOJI_WARNING} The free-VPS node is low on capacity. Please try again later."), view=None)
            return

        vps_id = _new_remote_vps_id()
        container_name = f"vps-{user_id}-{vps_id}"

        creating_embed = create_info_embed("Creating VPS", f"{EMOJI_LOADING} Deploying {get_os_display_name(self.selected_os)} VPS for {self.ctx.author.mention}...")
        await interaction.edit_original_response(embed=creating_embed, view=None)
        try:
            await client.create(container_name, self.selected_os, self.plan['ram'], self.plan['cpu'], self.plan['disk'])
        except NodeError as e:
            await interaction.edit_original_response(embed=create_error_embed("Creation Failed", f"```{e}```"), view=None)
            return

        plan_time = parse_time_string(self.plan.get('time', ''))
        expires_at = (datetime.utcnow() + plan_time) if plan_time else (datetime.utcnow() + timedelta(days=30))
        node_vps_add(vps_id, user_id, node_id, container_name,
                     self.plan['ram'], self.plan['cpu'], self.plan['disk'], self.selected_os, expires_at)
        node_vps_update(vps_id, plan_name=self.plan['name'])

        update_amount = -self.required
        if self.plan_category == 'invites':
            update_user_stats(user_id, invites=update_amount)
        else:
            update_user_stats(user_id, boosts=update_amount)
        update_user_stats(user_id, claimed_vps_count=1)

        config_str = f"{self.plan['ram']}GB RAM / {self.plan['cpu']} CPU / {self.plan['disk']}GB Disk"
        timer_display = f"{EMOJI_UPTIME} {format_timedelta(plan_time)}" if plan_time else ""

        success_embed = create_success_embed("VPS Created Successfully")
        add_field(success_embed, "Owner", self.ctx.author.mention, True)
        add_field(success_embed, "Plan", self.plan['name'], True)
        add_field(success_embed, f"{EMOJI_VPS} VPS ID", f"`{vps_id}`", True)
        add_field(success_embed, "Container", f"`{container_name}`", True)
        add_field(success_embed, f"{EMOJI_GLOBAL} Node", f"`{node_name_of(node_id)}`", True)
        add_field(success_embed, "Resources", f"**RAM:** {self.plan['ram']}GB\n**CPU:** {self.plan['cpu']} Cores\n**Storage:** {self.plan['disk']}GB", False)
        add_field(success_embed, "OS", f"{get_os_emoji(self.selected_os)} {get_os_display_name(self.selected_os)}", True)
        add_field(success_embed, f"{EMOJI_UPTIME} Expires", f"<t:{int(expires_at.timestamp())}:F>", True)
        await interaction.followup.send(embed=success_embed)

        try:
            await send_log(EMOJI_VPS, "Free VPS Claimed",
                f"{EMOJI_USER} **User:** {self.ctx.author.mention} (`{user_id}`)\n"
                f"{EMOJI_VPS} **Plan:** {self.plan['name']}\n"
                f"{EMOJI_RAM} **RAM:** {self.plan['ram']}GB | {EMOJI_CPU} **CPU:** {self.plan['cpu']} | {EMOJI_DISK} **Disk:** {self.plan['disk']}GB\n"
                f"**Container:** `{container_name}`\n"
                f"{get_os_emoji(self.selected_os)} **OS:** {self.selected_os}\n"
                f"{EMOJI_UPTIME} **Duration:** {timer_display}\n"
                f"{EMOJI_INFO} **Type:** {self.plan_category.title()} ({self.required} required)",
                color=0x00ff88)
        except Exception:
            pass

        try:
            dm_embed = create_success_embed("VPS Created!", "Your VPS has been successfully created!")
            vps_details = f"**Plan:** {self.plan['name']}\n"
            vps_details += f"**VPS ID:** `{vps_id}`\n"
            vps_details += f"**Container Name:** `{container_name}`\n"
            vps_details += f"**Configuration:** {config_str}\n"
            vps_details += f"**Status:** Running\n"
            vps_details += f"**OS:** {get_os_emoji(self.selected_os)} {get_os_display_name(self.selected_os)}\n"
            vps_details += f"**Node:** `{node_name_of(node_id)}`\n"
            vps_details += f"**Created:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
            add_field(dm_embed, "VPS Details", vps_details, False)
            add_field(dm_embed, "Management",
                     f"• Use `{PREFIX}manage` to start/stop your VPS\n"
                     f"• Use `{PREFIX}manage` for terminal access\n"
                     f"• Use `{PREFIX}ports` for port forwarding",
                     False)
            await self.ctx.author.send(embed=dm_embed)
        except Exception:
            pass


# ==================================================== USER COMMANDS END =====================================================

# ==================================================== MODERN REINSTALL BUTTON WITH OS SELECTION =====================================================

class ReinstallOSView(discord.ui.View):
    """Modern OS selection view for reinstall with descriptions and emojis"""
    def __init__(self, ctx, container_name, owner_id, actual_idx, vps_data_entry, parent_view):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.container_name = container_name
        self.owner_id = owner_id
        self.actual_idx = actual_idx
        self.vps_data_entry = vps_data_entry
        self.parent_view = parent_view
        self.message = None
        
        # Get current OS for display
        self.current_os = vps_data_entry.get('os_version', 'ubuntu:22.04')
        
        # Create OS selection dropdown with modern styling
        options = []
        for o in OS_OPTIONS:
            emoji = o.get('emoji', '🐧')
            description = o.get('description', '')
            options.append(discord.SelectOption(
                label=o["label"], 
                value=o["value"], 
                emoji=emoji,
                description=description
            ))
        
        self.select = discord.ui.Select(
            placeholder="🎯 Select a new operating system",
            options=options,
            min_values=1,
            max_values=1
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)
        
        # Add cancel button
        cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary, row=1, emoji=EMOJI_CROSS)
        cancel_button.callback = self.cancel_callback
        self.add_item(cancel_button)
    
    async def select_callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.ctx.author.id):
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can select."), ephemeral=True)
            return
        
        selected_os = self.select.values[0]
        os_display = get_os_display_name(selected_os)
        
        # Create confirmation embed
        embed = discord.Embed(
            title=f"{EMOJI_WARNING} Confirm Reinstall",
            description=f"Are you sure you want to reinstall **{self.container_name}**?",
            color=0xffaa00
        )
        
        # Set thumbnail if URL is provided
        if THUMBNAIL_URL:
            embed.set_thumbnail(url=THUMBNAIL_URL)
        
        # Set footer with timestamp and icon
        embed.set_footer(
            text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            icon_url=THUMBNAIL_URL
        )
        
        details = f"**Container:** `{self.container_name}`\n"
        details += f"**New OS:** {get_os_emoji(selected_os)} {os_display}\n"
        details += f"**Current OS:** {self.current_os}\n\n"
        details += f"{EMOJI_WARNING} **WARNING:** This will erase ALL data on this VPS!\n"
        details += "This action cannot be undone."
        
        embed.add_field(name=f"{EMOJI_INFO} Reinstall Details", value=details, inline=False)
        
        # Create confirmation buttons
        view = discord.ui.View()
        confirm_button = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.danger, emoji=EMOJI_SUCCESS)
        cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary, emoji=EMOJI_CROSS)
        
        async def confirm_callback(confirm_interaction):
            await self.perform_reinstall(confirm_interaction, selected_os)
        
        async def cancel_callback(cancel_interaction):
            await cancel_interaction.response.edit_message(
                embed=create_info_embed("Cancelled", "Reinstall operation cancelled."),
                view=None
            )
        
        confirm_button.callback = confirm_callback
        cancel_button.callback = cancel_callback
        
        view.add_item(confirm_button)
        view.add_item(cancel_button)
        
        await interaction.response.edit_message(embed=embed, view=view)
    
    async def perform_reinstall(self, interaction: discord.Interaction, selected_os):
        await interaction.response.defer()
        
        # Update message to show progress
        progress_embed = create_info_embed(
            "Reinstalling VPS", 
            f"Please wait while we reinstall **{self.container_name}** with **{selected_os}**...\n\n"
            f"{EMOJI_LOADING} **Step 1/4:** Stopping container..."
        )
        await interaction.edit_original_response(embed=progress_embed, view=None)
        
        try:
            # Get resource values from VPS
            ram_gb = _to_num(self.vps_data_entry['ram'])
            cpu = _to_num(self.vps_data_entry['cpu'])
            storage_gb = _to_num(self.vps_data_entry['storage'])
            ram_mb = _mem_mb(ram_gb)
            
            # Step 1: Stop and delete the container
            progress_embed.description = f"{EMOJI_LOADING} **Step 2/4:** Removing old container..."
            await interaction.edit_original_response(embed=progress_embed)
            
            try:
                await execute_lxc(f"lxc stop {shlex.quote(self.container_name)} --force", timeout=60)
            except:
                pass  # Container might not be running
            
            try:
                await execute_lxc(f"lxc delete {shlex.quote(self.container_name)} --force", timeout=60)
            except Exception as delete_err:
                if "Instance not found" in str(delete_err) or "not found" in str(delete_err).lower():
                    pass
                else:
                    raise
            
            # Step 2: Create new container with selected OS
            progress_embed.description = f"{EMOJI_LOADING} **Step 3/4:** Creating new container with {get_os_emoji(selected_os)} {selected_os}..."
            await interaction.edit_original_response(embed=progress_embed)
            
            resolved_os = await ensure_image_available(selected_os)
            await execute_lxc(f"lxc init {resolved_os} {shlex.quote(self.container_name)} -s {DEFAULT_STORAGE_POOL}", timeout=600)
            await apply_resource_limits(self.container_name, ram_gb=ram_gb, cpu_cores=cpu, disk_gb=storage_gb)
            await apply_lxc_config(self.container_name)
            
            # Step 3: Start and configure
            progress_embed.description = f"{EMOJI_LOADING} **Step 4/4:** Starting and configuring VPS..."
            await interaction.edit_original_response(embed=progress_embed)
            
            await execute_lxc(f"lxc start {shlex.quote(self.container_name)}")
            await apply_internal_permissions(self.container_name)
            
            # Update VPS data
            target_vps = vps_data[self.owner_id][self.actual_idx]
            target_vps["os_version"] = selected_os
            target_vps["status"] = "running"
            target_vps["suspended"] = False
            target_vps["created_at"] = datetime.now().isoformat()
            config_str = f"{_fmt_num(ram_gb)}GB RAM / {_fmt_num(cpu)} CPU / {_fmt_num(storage_gb)}GB Disk"
            target_vps["config"] = config_str
            save_vps_data()
            
            # Success embed
            success_embed = discord.Embed(
                title=f"{EMOJI_SUCCESS} Reinstall Complete",
                description=f"VPS **{self.container_name}** has been successfully reinstalled!",
                color=0x00ff88
            )
            
            # Set thumbnail if URL is provided
            if THUMBNAIL_URL:
                success_embed.set_thumbnail(url=THUMBNAIL_URL)
            
            # Set footer with timestamp and icon
            success_embed.set_footer(
                text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                icon_url=THUMBNAIL_URL
            )
            
            # Find OS display name
            os_display = get_os_display_name(selected_os)
            
            details = f"**Container:** `{self.container_name}`\n"
            details += f"**New OS:** {get_os_emoji(selected_os)} {os_display}\n"
            details += f"**Resources:** {_fmt_num(ram_gb)}GB RAM / {_fmt_num(cpu)} CPU / {_fmt_num(storage_gb)}GB Disk"
            
            success_embed.add_field(name=f"{EMOJI_INFO} New Configuration", value=details, inline=False)
            success_embed.add_field(name="✨ Features", 
                                  value="• Nesting, Privileged, FUSE\n• Docker-ready with kernel modules\n• Unprivileged ports from 0", 
                                  inline=False)
            
            await interaction.edit_original_response(embed=success_embed)
            
            # Refresh the parent view
            if self.parent_view and self.parent_view.selected_index is not None:
                new_embed = await self.parent_view.create_vps_embed(self.parent_view.selected_index)
                await self.parent_view.message.edit(embed=new_embed, view=self.parent_view)
            
        except Exception as e:
            error_embed = create_error_embed("Reinstall Failed", str(e))
            await interaction.edit_original_response(embed=error_embed)
    
    async def cancel_callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.ctx.author.id):
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can cancel."), ephemeral=True)
            return
        
        await interaction.response.edit_message(
            embed=create_info_embed("Cancelled", "Reinstall operation cancelled."),
            view=None
        )
        
        # Refresh the parent view
        if self.parent_view and self.parent_view.selected_index is not None:
            new_embed = await self.parent_view.create_vps_embed(self.parent_view.selected_index)
            await self.parent_view.message.edit(embed=new_embed, view=self.parent_view)

# ==================================================== MODERN REINSTALL BUTTON WITH OS SELECTION END =====================================================

# ==================================================== IPv4 SSH TUNNEL VIEW =====================================================

class IPv4SSHView(discord.ui.View):
    def __init__(self, container_name, owner_id, interaction_user, node=None):
        super().__init__(timeout=300)
        self.container_name = container_name
        self.owner_id = owner_id
        self.interaction_user = interaction_user
        self.node = node
        self.message = None

    def _status_embed(self, desc, color=0xffaa00):
        info = _remote_ipv4_tunnels.get(self.container_name)
        embed = discord.Embed(
            title=f"{EMOJI_GLOBAL} IPv4 SSH Tunnel — `{self.container_name}`",
            description=desc,
            color=color
        )
        if info:
            host, port = info
            if host and port:
                embed.add_field(name=f"{EMOJI_ARROW_RIGHT} SSH Command", value=f"```ssh -p {port} root@{host}```", inline=False)
            status_emoji = f"{EMOJI_ONLINE} **Running**"
        else:
            status_emoji = f"{EMOJI_OFFLINE} **Not running**"
        embed.add_field(name=f"{EMOJI_STATUS} Status", value=status_emoji, inline=False)
        embed.set_footer(text=f"{BOT_NAME} | Auto-restart on disconnect | 24/7")
        return embed

    @discord.ui.button(label="Start", style=discord.ButtonStyle.success, emoji=EMOJI_START)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.interaction_user.id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can control this."), ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        progress_msg = await interaction.followup.send(embed=self._status_embed(f"{EMOJI_LOADING} Initializing..."), ephemeral=True, wait=True)
        try:
            res = await node_client(self.node).ipv4_tunnel(self.container_name, "start")
        except NodeError as e:
            await interaction.edit_original_response(embed=self._status_embed(f"{EMOJI_CROSS} {e}", 0xff3366), view=self)
            return
        host, port = res.get("host"), res.get("port")
        if not host:
            await interaction.edit_original_response(
                embed=self._status_embed(f"{EMOJI_ONLINE} Tunnel starting — no URL yet, press Start again shortly.", 0x00ccff), view=self)
            return
        _remote_ipv4_tunnels[self.container_name] = (host, port)
        await interaction.edit_original_response(embed=self._status_embed(f"{EMOJI_SUCCESS} Tunnel active", 0x00ff88), view=self)
        try:
            dm = discord.Embed(
                title=f"{EMOJI_GLOBAL} IPv4 SSH Tunnel Active",
                description=f"Your temporary tunnel for **{self.container_name}** is ready!",
                color=0x00ff88)
            dm.add_field(name=f"{EMOJI_ARROW_RIGHT} SSH Command", value=f"```ssh -p {port} root@{host}```", inline=False)
            dm.add_field(name=f"{EMOJI_ARROW_RIGHT} Host", value=host, inline=True)
            dm.add_field(name=f"{EMOJI_ARROW_RIGHT} Port", value=str(port), inline=True)
            dm.set_footer(text=f"{BOT_NAME} | Auto-reconnect active | 24/7 Tunnel", icon_url=THUMBNAIL_URL)
            await interaction.user.send(embed=dm)
        except Exception:
            pass

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, emoji=EMOJI_CROSS)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.interaction_user.id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can control this."), ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        try:
            await node_client(self.node).ipv4_tunnel(self.container_name, "stop")
        except NodeError:
            pass
        _remote_ipv4_tunnels.pop(self.container_name, None)
        await interaction.edit_original_response(embed=self._status_embed(f"{EMOJI_SUCCESS} Tunnel stopped", 0xff3366), view=self)

# ==================================================== IPv4 SSH TUNNEL VIEW END =====================================================

# ==================================================== FILE MANAGER VIEW =====================================================

class FileManagerModal(discord.ui.Modal, title="📁 File Manager Credentials"):
    fm_username = discord.ui.TextInput(
        label="Username",
        placeholder="Enter admin username for file manager...",
        style=discord.TextStyle.short,
        min_length=1,
        max_length=50
    )
    fm_password = discord.ui.TextInput(
        label="Password (min 12 characters)",
        placeholder="Enter a strong password (12+ chars)...",
        style=discord.TextStyle.short,
        min_length=12,
        max_length=128
    )

    def __init__(self, container_name, owner_id, interaction_user, parent_view, node=None):
        super().__init__()
        self.container_name = container_name
        self.owner_id = owner_id
        self.interaction_user = interaction_user
        self.parent_view = parent_view
        self.node = node

    async def on_submit(self, interaction: discord.Interaction):
        username = self.fm_username.value.strip()
        password = self.fm_password.value.strip()

        if len(password) < 12:
            err_embed = discord.Embed(
                title=f"{EMOJI_CROSS} Password Too Short",
                description="Password must be at least **12 characters** long.\nPlease use Config-init again.",
                color=0xff3366
            )
            err_embed.set_footer(text=f"{BOT_NAME} | File Manager")
            try:
                await interaction.response.send_message(embed=err_embed, ephemeral=True)
            except Exception:
                pass
            return

        confirm_embed = discord.Embed(
            title=f"{EMOJI_FOLDER} Confirm Credentials",
            description=f"Are these values correct for `{self.container_name}`?",
            color=0xffaa00
        )
        confirm_embed.add_field(name=f"{EMOJI_USER} Username", value=f"```{username}```", inline=True)
        confirm_embed.add_field(name=f"{EMOJI_LOCK} Password", value=f"```{'*' * len(password)}```", inline=True)
        confirm_embed.set_footer(text=f"{BOT_NAME} | File Manager Setup")

        class ConfirmView(discord.ui.View):
            def __init__(self, parent):
                super().__init__(timeout=120)
                self.parent = parent

            @discord.ui.button(label="Yes", style=discord.ButtonStyle.success, emoji=EMOJI_SUCCESS)
            async def yes_btn(self, inter: discord.Interaction, btn: discord.ui.Button):
                if inter.user.id != self.parent.interaction_user.id:
                    await inter.response.send_message("Not your menu!", ephemeral=True)
                    return
                await self.parent._do_config_init(inter, username, password)

            @discord.ui.button(label="No", style=discord.ButtonStyle.danger, emoji=EMOJI_CROSS)
            async def no_btn(self, inter: discord.Interaction, btn: discord.ui.Button):
                if inter.user.id != self.parent.interaction_user.id:
                    await inter.response.send_message("Not your menu!", ephemeral=True)
                    return
                cancelled = discord.Embed(
                    title=f"{EMOJI_CROSS} Config-init Cancelled",
                    description="File manager credentials setup cancelled.",
                    color=0xff3366
                )
                cancelled.set_footer(text=f"{BOT_NAME} | File Manager")
                for child in self.children:
                    child.disabled = True
                await inter.response.edit_message(embed=cancelled, view=self)

        try:
            await interaction.response.send_message(embed=confirm_embed, view=ConfirmView(self), ephemeral=True)
        except Exception:
            pass

    async def _do_config_init(self, interaction, username, password):
        for child in interaction.message.components:
            for c in child.children:
                c.disabled = True
        await interaction.response.edit_message(
            embed=discord.Embed(
                title=f"{EMOJI_FOLDER} File Manager — `{self.container_name}`",
                description=f"{EMOJI_LOADING} Setting up...",
                color=0xffaa00
            ).set_footer(text=f"{BOT_NAME} | File Manager"),
            view=None
        )

        async def edit_progress(text, color=0xffaa00):
            try:
                await interaction.edit_original_response(
                    embed=discord.Embed(
                        title=f"{EMOJI_FOLDER} File Manager — `{self.container_name}`",
                        description=text,
                        color=color
                    ).set_footer(text=f"{BOT_NAME} | File Manager")
                )
            except Exception:
                pass

        await edit_progress(f"{EMOJI_LOADING} Installing filebrowser + configuring user...")
        try:
            res = await node_client(self.node).file_manager(
                self.container_name, "start", username, password)
        except NodeError as e:
            await edit_progress(f"{EMOJI_CROSS} **Filebrowser Setup Failed:** {e}", 0xff3366)
            return

        _save_fm_creds(self.container_name, username, password)
        _filemanager_credentials[self.container_name] = {"username": username, "password": password}

        host, port = res.get("host"), res.get("port")
        if not host:
            await edit_progress(
                f"{EMOJI_ONLINE} Filebrowser installed + user configured\n"
                f"{EMOJI_LOADING} Tunnel starting — press **Start** again shortly for the URL.",
                0x00ccff
            )
            return

        _remote_filemanager[self.container_name] = (host, port, username)
        fm_url = f"http://{host}:{port}"
        await edit_progress(
            f"{EMOJI_SUCCESS} **Tunnel:** Connected!\n"
            f"{EMOJI_FOLDER} **URL:** {fm_url}\n"
            f"{EMOJI_USER} **Username:** `{username}`\n"
            f"{EMOJI_LOCK} **Password:** `{'*' * len(password)}`\n"
            f"{EMOJI_INFO} Details sent to your DMs",
            0x00ff88
        )
        try:
            dm = discord.Embed(
                title=f"{EMOJI_FOLDER} File Manager Ready",
                description=f"Your file manager for **{self.container_name}** is live!",
                color=0x00ff88
            )
            dm.add_field(name=f"{EMOJI_FOLDER} URL", value=fm_url, inline=False)
            dm.add_field(name=f"{EMOJI_USER} Username", value=f"`{username}`", inline=True)
            dm.add_field(name=f"{EMOJI_LOCK} Password", value=f"`{password}`", inline=True)
            dm.set_footer(text=f"{BOT_NAME} | File Manager | Auto-reconnect 24/7", icon_url=THUMBNAIL_URL)
            await self.interaction_user.send(embed=dm)
        except Exception:
            pass


class FileManagerView(discord.ui.View):
    def __init__(self, container_name, owner_id, interaction_user, node=None):
        super().__init__(timeout=300)
        self.container_name = container_name
        self.owner_id = owner_id
        self.interaction_user = interaction_user
        self.node = node

    def _status_embed(self, desc, color=0xffaa00):
        info = _remote_filemanager.get(self.container_name)
        embed = discord.Embed(
            title=f"{EMOJI_FOLDER} File Manager — `{self.container_name}`",
            description=desc,
            color=color
        )
        if info:
            host, port, username = info
            creds = _filemanager_credentials.get(self.container_name, None)
            embed.add_field(name=f"{EMOJI_ARROW_RIGHT} URL", value=f"http://{host}:{port}", inline=False)
            if creds:
                embed.add_field(name=f"{EMOJI_USER} Username", value=f"`{creds['username']}`", inline=True)
                embed.add_field(name=f"{EMOJI_LOCK} Password", value=f"`{'*' * len(creds['password'])}`", inline=True)
            embed.add_field(name=f"{EMOJI_STATUS} Status", value=f"{EMOJI_ONLINE} **Running**", inline=False)
        else:
            embed.add_field(name=f"{EMOJI_STATUS} Status", value=f"{EMOJI_OFFLINE} **Not running**", inline=False)
        embed.set_footer(text=f"{BOT_NAME} | Auto-restart on disconnect | File Manager")
        return embed

    @discord.ui.button(label="Config-init", style=discord.ButtonStyle.primary, emoji=EMOJI_FOLDER)
    async def config_init_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.interaction_user.id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can control this."), ephemeral=True)
            return
        modal = FileManagerModal(self.container_name, self.owner_id, self.interaction_user, self, node=self.node)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Start", style=discord.ButtonStyle.success, emoji=EMOJI_START)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.interaction_user.id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can control this."), ephemeral=True)
            return
        if self.container_name in _remote_filemanager:
            await interaction.response.send_message(embed=create_warning_embed("Already Running", "File manager is already active."), ephemeral=True)
            return

        creds = _load_fm_creds(self.container_name) or _filemanager_credentials.get(self.container_name)
        if not creds:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"{EMOJI_CROSS} Not Configured",
                    description="File manager is not configured yet. Use **Config-init** first to install and configure it.",
                    color=0xff3366
                ).set_footer(text=f"{BOT_NAME} | File Manager"),
                ephemeral=True
            )
            return
        username = creds["username"]
        password = creds["password"]

        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(
            embed=discord.Embed(
                title=f"{EMOJI_FOLDER} File Manager — `{self.container_name}`",
                description=f"{EMOJI_LOADING} Starting...",
                color=0xffaa00
            ).set_footer(text=f"{BOT_NAME} | File Manager"),
            view=None
        )

        async def edit_progress(text, color=0xffaa00):
            try:
                await interaction.edit_original_response(
                    embed=discord.Embed(
                        title=f"{EMOJI_FOLDER} File Manager — `{self.container_name}`",
                        description=text,
                        color=color
                    ).set_footer(text=f"{BOT_NAME} | File Manager")
                )
            except Exception:
                pass

        await edit_progress(f"{EMOJI_LOADING} Starting filebrowser + tunnel...")
        try:
            res = await node_client(self.node).file_manager(
                self.container_name, "start", username, password)
        except NodeError as e:
            await edit_progress(f"{EMOJI_CROSS} **Failed:** {e}", 0xff3366)
            return

        host, port = res.get("host"), res.get("port")
        if not host:
            await edit_progress(
                f"{EMOJI_ONLINE} Tunnel starting — no URL yet, press **Start** again shortly.",
                0x00ccff
            )
            return

        _remote_filemanager[self.container_name] = (host, port, username)
        _filemanager_credentials[self.container_name] = {"username": username, "password": password}
        fm_url = f"http://{host}:{port}"
        await edit_progress(
            f"{EMOJI_SUCCESS} **Tunnel:** Connected!\n"
            f"{EMOJI_FOLDER} **URL:** {fm_url}\n"
            f"{EMOJI_USER} **Username:** `{username}`\n"
            f"{EMOJI_LOCK} **Password:** `{'*' * len(password)}`\n"
            f"{EMOJI_INFO} Details sent to your DMs",
            0x00ff88
        )
        try:
            dm = discord.Embed(
                title=f"{EMOJI_FOLDER} File Manager Ready",
                description=f"Your file manager for **{self.container_name}** is live!",
                color=0x00ff88
            )
            dm.add_field(name=f"{EMOJI_FOLDER} URL", value=fm_url, inline=False)
            dm.add_field(name=f"{EMOJI_USER} Username", value=f"`{username}`", inline=True)
            dm.add_field(name=f"{EMOJI_LOCK} Password", value=f"`{password}`", inline=True)
            dm.set_footer(text=f"{BOT_NAME} | File Manager | Auto-reconnect 24/7", icon_url=THUMBNAIL_URL)
            await self.interaction_user.send(embed=dm)
        except Exception:
            pass

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, emoji=EMOJI_CROSS)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.interaction_user.id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can control this."), ephemeral=True)
            return
        await interaction.response.defer()
        try:
            await node_client(self.node).file_manager(self.container_name, "stop")
        except NodeError:
            pass
        _remote_filemanager.pop(self.container_name, None)
        await interaction.edit_original_response(
            embed=self._status_embed(f"{EMOJI_SUCCESS} File manager stopped", 0xff3366), view=self
        )

    @discord.ui.button(label="Clear", style=discord.ButtonStyle.secondary, emoji=EMOJI_FOLDER)
    async def clear_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.interaction_user.id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can control this."), ephemeral=True)
            return

        warning_embed = discord.Embed(
            title=f"{EMOJI_WARNING} Clear File Manager",
            description=f"Are you sure you want to **completely remove** file manager from `{self.container_name}`?\n\n"
                        f"This will:\n"
                        f"• Stop file manager process\n"
                        f"• Delete the filebrowser binary\n"
                        f"• Delete all filebrowser config files\n"
                        f"• Remove all data associated with file manager\n\n"
                        f"**This cannot be undone!**",
            color=0xff0000
        )
        warning_embed.set_footer(text=f"{BOT_NAME} | File Manager")

        class ClearConfirmView(discord.ui.View):
            def __init__(self, parent):
                super().__init__(timeout=60)
                self.parent = parent

            @discord.ui.button(label="Yes", style=discord.ButtonStyle.danger, emoji=EMOJI_SUCCESS)
            async def yes_btn(self, inter: discord.Interaction, btn: discord.ui.Button):
                if inter.user.id != self.parent.interaction_user.id:
                    await inter.response.send_message("Not your menu!", ephemeral=True)
                    return
                for child in self.children:
                    child.disabled = True
                await inter.response.edit_message(
                    embed=discord.Embed(
                        title=f"{EMOJI_FOLDER} Clearing File Manager",
                        description=f"{EMOJI_LOADING} Removing everything...",
                        color=0xffaa00
                    ).set_footer(text=f"{BOT_NAME} | File Manager"),
                    view=self
                )
                try:
                    client = node_client(self.parent.node)
                    try:
                        await client.file_manager(self.parent.container_name, "stop")
                    except NodeError:
                        pass
                    await client.exec(
                        self.parent.container_name,
                        "pkill -x filebrowser; rm -f /usr/local/bin/filebrowser "
                        "/usr/bin/filebrowser; rm -rf /root/.config/filebrowser "
                        "~/.config/filebrowser /etc/filebrowser"
                    )
                    _remote_filemanager.pop(self.parent.container_name, None)
                    _delete_fm_creds(self.parent.container_name)
                    done = discord.Embed(
                        title=f"{EMOJI_SUCCESS} File Manager Cleared",
                        description=f"File manager has been completely removed from `{self.parent.container_name}`.",
                        color=0x00ff88
                    )
                    done.set_footer(text=f"{BOT_NAME} | File Manager")
                    await inter.edit_original_response(embed=done)
                except Exception as e:
                    err = discord.Embed(
                        title=f"{EMOJI_CROSS} Clear Failed",
                        description=str(e),
                        color=0xff3366
                    )
                    err.set_footer(text=f"{BOT_NAME} | File Manager")
                    await inter.edit_original_response(embed=err)

            @discord.ui.button(label=" No", style=discord.ButtonStyle.secondary, emoji=EMOJI_CROSS)
            async def no_btn(self, inter: discord.Interaction, btn: discord.ui.Button):
                if inter.user.id != self.parent.interaction_user.id:
                    await inter.response.send_message("Not your menu!", ephemeral=True)
                    return
                cancelled = discord.Embed(
                    title=f"{EMOJI_CROSS} Clear Cancelled",
                    description="File manager clear cancelled.",
                    color=0xff3366
                )
                cancelled.set_footer(text=f"{BOT_NAME} | File Manager")
                for child in self.children:
                    child.disabled = True
                await inter.response.edit_message(embed=cancelled, view=self)

        await interaction.response.send_message(embed=warning_embed, view=ClearConfirmView(self), ephemeral=True)

# ==================================================== FILE MANAGER VIEW END =====================================================

# ==================================================== VPS MANAGEMENT COMMANDS =====================================================

class ManageView(discord.ui.View):
    def __init__(self, user_id, vps_list, is_shared=False, owner_id=None, is_admin=False, actual_index: Optional[int] = None, ctx=None):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.vps_list = vps_list[:]
        self.selected_index = 0 if vps_list else None
        self.is_shared = is_shared
        self.owner_id = owner_id or user_id
        self.is_admin = is_admin
        self.actual_index = actual_index
        self.indices = list(range(len(vps_list)))
        self.message = None  # Will be set when message is sent
        self.ctx = ctx
        
        if self.is_shared and self.actual_index is None:
            raise ValueError("actual_index required for shared views")
        
        if len(vps_list) > 1:
            options = [
                discord.SelectOption(
                    label=f"VPS {i+1} ({v.get('plan_name', 'Custom')})",
                    description=f"Status: {v.get('status', 'unknown')}",
                    value=str(i)
                ) for i, v in enumerate(vps_list)
            ]
            self.select = discord.ui.Select(placeholder="Select a VPS to manage", options=options)
            self.select.callback = self.select_vps
            self.add_item(self.select)
        else:
            self.add_action_buttons()
    
    async def create_vps_embed(self, index):
        vps = self.vps_list[index]
        status = vps.get('status', 'unknown')
        suspended = vps.get('suspended', False)
        whitelisted = vps.get('whitelisted', False)
        purge_protected = vps.get('purge_protected', False)
        status_color = 0x00ff88 if status == 'running' and not suspended else 0xffaa00 if suspended else 0xff3366
        container_name = vps['container_name']
        
        lxc_status = await get_container_status(container_name)
        cpu_usage = await get_container_cpu(container_name)
        memory_usage = await get_container_memory(container_name)
        disk_usage = await get_container_disk(container_name)
        uptime = await get_container_uptime(container_name)
        
        status_text = f"{lxc_status.upper()}"
        if suspended:
            status_text += " (SUSPENDED)"
        if whitelisted:
            status_text += " (WHITELISTED)"
        
        purge_text = f"{EMOJI_ONLINE} Enabled" if purge_protected else f"{EMOJI_OFFLINE} Disabled"
        
        owner_text = ""
        if self.is_admin and self.owner_id != self.user_id:
            try:
                owner_user = await bot.fetch_user(int(self.owner_id))
                owner_text = f"\n**Owner:** {owner_user.mention}"
            except:
                owner_text = f"\n**Owner ID:** {self.owner_id}"
        
        embed = discord.Embed(
            title=f"{EMOJI_VPS} VPS Management",
            description=f"Managing VPS #{get_vps_number(container_name) or (index + 1)}: `{container_name}`{owner_text}",
            color=status_color
        )
        
        # Set thumbnail if URL is provided
        if THUMBNAIL_URL:
            embed.set_thumbnail(url=THUMBNAIL_URL)
        
        # Set footer with timestamp and icon
        embed.set_footer(
            text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            icon_url=THUMBNAIL_URL
        )
        
        # Find OS display name
        os_display = vps.get('os_version', 'ubuntu:22.04')
        os_display = get_os_display_name(os_display)
        
        resource_info = f"**Plan:** {vps.get('plan_name', 'Custom')}\n"
        resource_info += f"{EMOJI_STATUS} **Status:** {status_text}\n"
        resource_info += f"{EMOJI_RAM} **RAM:** {vps['ram']}\n"
        resource_info += f"{EMOJI_CPU} **CPU:** {vps['cpu']} Cores\n"
        resource_info += f"{EMOJI_DISK} **Storage:** {vps['storage']}\n"
        resource_info += f"{get_os_emoji(vps.get('os_version', 'ubuntu:22.04'))} **OS:** {os_display}\n"
        resource_info += f"{EMOJI_UPTIME} **Uptime:** {uptime}\n"
        resource_info += get_vps_timer_line(vps)
        resource_info += f"\n**Purge Protection:** {purge_text} "
        
        embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Resources", value=resource_info, inline=False)
        
        if suspended:
            embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Suspended", value="This VPS is suspended. Contact an admin to unsuspend.", inline=False)
        if whitelisted:
            embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Whitelisted", value="This VPS is exempt from auto-suspension.", inline=False)
        if purge_protected:
            embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Purge Protected", value="This VPS is protected from `{PREFIX}purge-vm-all` command.", inline=False)
        
        live_stats = f"**CPU Usage:** {cpu_usage}\n**Memory:** {memory_usage}\n**Disk:** {disk_usage}"
        embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Live Usage", value=live_stats, inline=False)
        embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Controls", value="Use the buttons below to manage your VPS", inline=False)
        
        return embed
    
    def add_action_buttons(self):
        # Modern button styling with emojis
        if not self.is_shared and not self.is_admin:
            reinstall_button = discord.ui.Button(label="Reinstall", style=discord.ButtonStyle.danger, emoji=EMOJI_REINSTALL)
            reinstall_button.callback = lambda inter: self.action_callback(inter, 'reinstall')
            self.add_item(reinstall_button)
        
        start_button = discord.ui.Button(label="Start", style=discord.ButtonStyle.success, emoji=EMOJI_START)
        start_button.callback = lambda inter: self.action_callback(inter, 'start')
        
        stop_button = discord.ui.Button(label="Stop", style=discord.ButtonStyle.secondary, emoji=EMOJI_STOP)
        stop_button.callback = lambda inter: self.action_callback(inter, 'stop')
        
        ssh_button = discord.ui.Button(label="SSHX", style=discord.ButtonStyle.primary, emoji=EMOJI_SSHX)
        ssh_button.callback = lambda inter: self.action_callback(inter, 'ssh')

        tmate_button = discord.ui.Button(label="Tmate", style=discord.ButtonStyle.success, emoji=EMOJI_TMATE)
        tmate_button.callback = lambda inter: self.action_callback(inter, 'tmate')

        ipv4_button = discord.ui.Button(label="IPv4-SSH", style=discord.ButtonStyle.secondary, emoji=EMOJI_GLOBAL)
        ipv4_button.callback = lambda inter: self.action_callback(inter, 'ipv4_ssh')

        filemanager_button = discord.ui.Button(label="File-Manager", style=discord.ButtonStyle.secondary, emoji=EMOJI_FOLDER)
        filemanager_button.callback = lambda inter: self.action_callback(inter, 'filemanager')

        stats_button = discord.ui.Button(label="Stats", style=discord.ButtonStyle.secondary, emoji=EMOJI_STATS)
        stats_button.callback = lambda inter: self.action_callback(inter, 'stats')

        self.add_item(start_button)
        self.add_item(stop_button)
        self.add_item(ssh_button)
        self.add_item(tmate_button)
        self.add_item(ipv4_button)
        self.add_item(filemanager_button)
        self.add_item(stats_button)
    
    async def select_vps(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.user_id and not self.is_admin:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "This is not your VPS!"), ephemeral=True)
            return
        
        await interaction.response.defer()
        self.selected_index = int(self.select.values[0])
        new_embed = await self.create_vps_embed(self.selected_index)
        self.clear_items()
        self.add_action_buttons()
        await interaction.edit_original_response(embed=new_embed, view=self)
        self.message = await interaction.original_response()
    
    async def action_callback(self, interaction: discord.Interaction, action: str):
        if str(interaction.user.id) != self.user_id and not self.is_admin:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "This is not your VPS!"), ephemeral=True)
            return
        
        if self.selected_index is None and len(self.vps_list) == 1:
            self.selected_index = 0
        
        if self.selected_index is None:
            await interaction.response.send_message(embed=create_error_embed("No VPS Selected", "Please select a VPS first."), ephemeral=True)
            return
        
        actual_idx = self.actual_index if self.is_shared else self.indices[self.selected_index]
        target_vps = vps_data[self.owner_id][actual_idx]
        suspended = target_vps.get('suspended', False)
        
        if suspended and not self.is_admin and action not in ['stats']:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "This VPS is suspended. Contact an admin to unsuspend."), ephemeral=True)
            return
        
        container_name = target_vps["container_name"]
        
        if action == 'stats':
            if target_vps.get('status') != 'running':
                await interaction.response.send_message(embed=create_warning_embed(f"{EMOJI_WARNING} VPS Not Running", f"`{container_name}` is not running. Start it first."), ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)

            progress_msg = await interaction.followup.send(
                embed=create_info_embed(f"{EMOJI_STATS} Live Statistics", f"{EMOJI_LOADING} Starting live stats..."),
                ephemeral=True, wait=True
            )

            start = time.time()
            try:
                while (time.time() - start) < 3600:
                    iter_start = time.time()
                    cpu_usage, memory_usage, disk_usage, uptime_str = await get_container_stats_batch(container_name)
                    lxc_status = await get_container_status(container_name)

                    embed = create_info_embed(f"{EMOJI_STATS} Live Statistics", f"Real-time stats for `{container_name}`")
                    add_field(embed, f"{EMOJI_STATUS} Status", f"`{lxc_status.upper()}`", True)
                    add_field(embed, f"{EMOJI_CPU} CPU", cpu_usage, True)
                    add_field(embed, f"{EMOJI_RAM} Memory", memory_usage, True)
                    add_field(embed, f"{EMOJI_DISK} Disk", disk_usage, True)
                    add_field(embed, f"{EMOJI_UPTIME} Uptime", uptime_str, True)

                    timer_line = get_vps_timer_line(target_vps)
                    if timer_line:
                        add_field(embed, f"{EMOJI_UPTIME} Auto-Suspend Timer", timer_line.replace("\n", ""), True)

                    await progress_msg.edit(embed=embed)

                    elapsed = time.time() - iter_start
                    await asyncio.sleep(max(0, 1 - elapsed))
            except Exception:
                pass
            return
        
        # Handle reinstall action with modern OS selection
        if action == 'reinstall':
            if self.is_shared or self.is_admin:
                await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the VPS owner can reinstall!"), ephemeral=True)
                return
            
            if suspended:
                await interaction.response.send_message(embed=create_error_embed("Cannot Reinstall", "Unsuspend the VPS first."), ephemeral=True)
                return
            
            # Create modern OS selection view
            os_view = ReinstallOSView(
                ctx=self.ctx if hasattr(self, 'ctx') else interaction,
                container_name=container_name,
                owner_id=self.owner_id,
                actual_idx=actual_idx,
                vps_data_entry=target_vps,
                parent_view=self
            )
            
            # Get current OS display name
            current_os_display = target_vps.get('os_version', 'ubuntu:22.04')
            current_os_display = get_os_display_name(current_os_display)
            
            embed = discord.Embed(
                title=f"{EMOJI_REINSTALL} Reinstall VPS",
                description=f"Choose a new operating system for **{container_name}**",
                color=0xffaa00
            )
            
            # Set thumbnail if URL is provided
            if THUMBNAIL_URL:
                embed.set_thumbnail(url=THUMBNAIL_URL)
            
            # Set footer with timestamp and icon
            embed.set_footer(
                text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                icon_url=THUMBNAIL_URL
            )
            
            embed.add_field(name=f"{EMOJI_INFO} Current Configuration", 
                          value=f"**Container:** `{container_name}`\n**Current OS:** {current_os_display}", 
                          inline=False)
            embed.add_field(name=f"{EMOJI_WARNING} Warning", 
                          value="This will erase ALL data on this VPS. Make sure to backup important files first.", 
                          inline=False)
            
            await interaction.response.send_message(embed=embed, view=os_view, ephemeral=True)
            return
        
        if action == 'ipv4_ssh':
            if target_vps.get('status') != 'running':
                await interaction.response.send_message(embed=create_warning_embed(f"{EMOJI_WARNING} VPS Not Running", f"`{container_name}` is not running. Start it first."), ephemeral=True)
                return
            view = IPv4SSHView(container_name, self.owner_id, interaction.user)
            desc = f"{EMOJI_INFO} Press **Start** to begin the persistent IPv4 SSH tunnel" if container_name not in active_ipv4_tunnels else f"{EMOJI_ONLINE} Tunnel is active"
            await interaction.response.send_message(embed=view._status_embed(desc), view=view, ephemeral=True)
            return

        if action == 'filemanager':
            if target_vps.get('status') != 'running':
                await interaction.response.send_message(embed=create_warning_embed(f"{EMOJI_WARNING} VPS Not Running", f"`{container_name}` is not running. Start it first."), ephemeral=True)
                return
            view = FileManagerView(container_name, self.owner_id, interaction.user)
            desc = f"{EMOJI_INFO} Press **Start** to set up File Manager" if container_name not in active_filemanager else f"{EMOJI_ONLINE} File Manager is active"
            await interaction.response.send_message(embed=view._status_embed(desc), view=view, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        if action == 'start':
            progress_msg = await interaction.followup.send(
                embed=create_info_embed(f"{EMOJI_START} Starting VPS", f"{EMOJI_LOADING} Starting `{container_name}`, please wait..."),
                ephemeral=True, wait=True
            )
            try:
                await execute_lxc(f"lxc start {shlex.quote(container_name)}")
                target_vps["status"] = "running"
                target_vps["suspended"] = False
                save_vps_data()
                await apply_internal_permissions(container_name)
                await progress_msg.edit(embed=create_success_embed(f"{EMOJI_SUCCESS} VPS Started", f"VPS `{container_name}` is now running!"))
            except Exception as e:
                err_str = str(e)
                if "not found" in err_str.lower():
                    err_str = f"VPS `{container_name}` no longer exists on the host."
                await progress_msg.edit(embed=create_error_embed(f"{EMOJI_WARNING} Start Failed", err_str))
        
        elif action == 'stop':
            progress_msg = await interaction.followup.send(
                embed=create_info_embed(f"{EMOJI_STOP} Stopping VPS", f"{EMOJI_LOADING} Stopping `{container_name}`, please wait..."),
                ephemeral=True, wait=True
            )
            try:
                await execute_lxc(f"lxc stop {shlex.quote(container_name)}", timeout=120)
                target_vps["status"] = "stopped"
                save_vps_data()
                await progress_msg.edit(embed=create_success_embed(f"{EMOJI_SUCCESS} VPS Stopped", f"VPS `{container_name}` has been stopped!"))
            except Exception as e:
                err_str = str(e)
                if "not found" in err_str.lower():
                    err_str = f"VPS `{container_name}` no longer exists on the host."
                await progress_msg.edit(embed=create_error_embed(f"{EMOJI_WARNING} Stop Failed", err_str))
        
        elif action == 'ssh':
            if target_vps.get('status') != 'running':
                await interaction.followup.send(embed=create_warning_embed(f"{EMOJI_WARNING} VPS Not Running", f"`{container_name}` is not running. Start it first."), ephemeral=True)
                return
            if suspended:
                await interaction.followup.send(embed=create_error_embed(f"{EMOJI_WARNING} SSHX Access", "Cannot access suspended VPS."), ephemeral=True)
                return
            if not await container_exists(container_name):
                await interaction.followup.send(embed=create_error_embed(f"{EMOJI_CROSS} VPS Not Found", f"VPS `{container_name}` no longer exists on the host."), ephemeral=True)
                return

            progress_msg = await interaction.followup.send(
                embed=create_info_embed(f"{EMOJI_SSHX} SSHX Access", "Starting SSHX session..."),
                ephemeral=True, wait=True
            )

            if not await check_container_internet(container_name):
                await progress_msg.edit(embed=create_info_embed(f"{EMOJI_SSHX} SSHX Access",
                    f"{EMOJI_LOADING} No internet detected — auto-fixing..."))
                await ensure_container_internet(container_name, max_retries=2)
                if not await check_container_internet(container_name):
                    await progress_msg.edit(embed=create_error_embed(f"{EMOJI_WARNING} No Internet",
                        f"Container has no internet. Contact an administrator."))
                    return

            try:
                check_proc = await asyncio.create_subprocess_exec(
                    "lxc", "exec", container_name, "--", "which", "sshx",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await check_proc.communicate()

                if check_proc.returncode != 0:
                    await progress_msg.edit(embed=create_info_embed(f"{EMOJI_SSHX} Installing SSHX",
                        f"{EMOJI_LOADING} Step 1/5: Testing internet connectivity..."))

                    if not await check_container_internet(container_name):
                        await progress_msg.edit(embed=create_info_embed(f"{EMOJI_SSHX} Installing SSHX",
                            f"{EMOJI_LOADING} Step 1/5: No internet detected — auto-fixing..."))
                        await ensure_container_internet(container_name, max_retries=2)
                        if not await check_container_internet(container_name):
                            await progress_msg.edit(embed=create_error_embed(f"{EMOJI_WARNING} No Internet",
                                f"Container has no internet access even after auto-fix.\nContact an administrator."))
                            return

                    await progress_msg.edit(embed=create_info_embed(f"{EMOJI_SSHX} Installing SSHX",
                        f"{EMOJI_LOADING} Step 2/5: Updating packages and installing curl..."))
                    try:
                        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- apt-get update -y", timeout=180)
                    except Exception as e:
                        logger.error(f"apt-get update failed: {e}")
                        raise
                    try:
                        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- apt-get install -y curl", timeout=120)
                    except Exception as e:
                        logger.error(f"curl install failed: {e}")
                        raise

                    await progress_msg.edit(embed=create_info_embed(f"{EMOJI_SSHX} Installing SSHX",
                        f"{EMOJI_LOADING} Step 3/5: Downloading sshx installer..."))
                    try:
                        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- curl -L --connect-timeout 30 --max-time 300 https://sshx.io/get -o /tmp/sshx_install.sh", timeout=310)
                    except Exception:
                        await ensure_container_internet(container_name, max_retries=2)
                        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- curl -L --connect-timeout 30 --max-time 300 https://sshx.io/get -o /tmp/sshx_install.sh", timeout=310)
                    actual_out = await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- wc -c /tmp/sshx_install.sh", timeout=10)
                    logger.info(f"Downloaded sshx install script: {actual_out}")

                    await progress_msg.edit(embed=create_info_embed(f"{EMOJI_SSHX} Installing SSHX",
                        f"{EMOJI_LOADING} Step 4/5: Running sshx installer..."))
                    await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- sh /tmp/sshx_install.sh", timeout=120)
                    await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- rm -f /tmp/sshx_install.sh", timeout=10)

                await progress_msg.edit(embed=create_info_embed(f"{EMOJI_SSHX} Starting SSHX",
                    f"{EMOJI_LOADING} Launching session..."))
                await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- bash -c \"pkill -9 sshx 2>/dev/null; rm -f /tmp/sshx_output.txt\"", timeout=10)
                await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- bash -c \"nohup sshx > /tmp/sshx_output.txt 2>&1 &\"", timeout=10)
                await asyncio.sleep(5)

                out_proc = await asyncio.create_subprocess_exec(
                    "lxc", "exec", container_name, "--", "cat", "/tmp/sshx_output.txt",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await out_proc.communicate()
                output = stdout.decode().strip() if stdout else ""

                ansi_escape = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')
                clean_output = ansi_escape.sub('', output)
                match = re.search(r'https?://sshx\.io/\S+', clean_output)
                sshx_url = match.group(0) if match else None

                if sshx_url:
                    try:
                        sshx_embed = create_info_embed(f"{EMOJI_SSHX} SSHX Access", f"SSHX session for VPS `{container_name}`:")
                        add_field(sshx_embed, f"{EMOJI_SSHX} URL", f"```{sshx_url}```", False)
                        add_field(sshx_embed, f"{EMOJI_SYSTEM} Security", "This link is temporary. Do not share it.", False)

                        await interaction.user.send(embed=sshx_embed)
                        await progress_msg.edit(embed=create_success_embed(f"{EMOJI_SUCCESS} SSHX Ready", "Check your DMs for the SSHX link!"))
                    except discord.Forbidden:
                        await progress_msg.edit(embed=create_error_embed(f"{EMOJI_WARNING} DM Failed", "Enable DMs to receive SSHX link!"))
                else:
                    logger.warning(f"SSHX output contained no URL: {output[:500]}")
                    await progress_msg.edit(embed=create_success_embed(f"{EMOJI_SUCCESS} SSHX Started", f"Run `{PREFIX}exec {container_name} cat /tmp/sshx_output.txt` to see the URL."))

            except Exception as e:
                logger.error(f"SSHX error for {container_name}: {e}", exc_info=True)
                err_str = str(e)
                if "not found" in err_str.lower():
                    err_str = f"VPS `{container_name}` no longer exists on the host."
                await progress_msg.edit(embed=create_error_embed(f"{EMOJI_WARNING} SSHX Error", err_str))

        elif action == 'tmate':
            if target_vps.get('status') != 'running':
                await interaction.followup.send(embed=create_warning_embed(f"{EMOJI_WARNING} VPS Not Running", f"`{container_name}` is not running. Start it first."), ephemeral=True)
                return
            if suspended:
                await interaction.followup.send(embed=create_error_embed(f"{EMOJI_WARNING} Tmate Access", "Cannot access suspended VPS."), ephemeral=True)
                return
            if not await container_exists(container_name):
                await interaction.followup.send(embed=create_error_embed(f"{EMOJI_CROSS} VPS Not Found", f"VPS `{container_name}` no longer exists on the host."), ephemeral=True)
                return

            progress_msg = await interaction.followup.send(
                embed=create_info_embed(f"{EMOJI_TMATE} Tmate Access", "Starting Tmate session..."),
                ephemeral=True, wait=True
            )

            if not await check_container_internet(container_name):
                await progress_msg.edit(embed=create_info_embed(f"{EMOJI_TMATE} Tmate Access",
                    f"{EMOJI_LOADING} No internet detected — auto-fixing..."))
                await ensure_container_internet(container_name, max_retries=2)
                if not await check_container_internet(container_name):
                    await progress_msg.edit(embed=create_error_embed(f"{EMOJI_WARNING} No Internet",
                        f"Container has no internet. Contact an administrator."))
                    return

            try:
                await progress_msg.edit(embed=create_info_embed(f"{EMOJI_TMATE} Setting up Tmate",
                    f"{EMOJI_LOADING} Checking installation..."))

                check_proc = await asyncio.create_subprocess_exec(
                    "lxc", "exec", container_name, "--", "which", "tmate",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await check_proc.communicate()

                if check_proc.returncode != 0:
                    await progress_msg.edit(embed=create_info_embed(f"{EMOJI_TMATE} Installing Tmate",
                        f"{EMOJI_LOADING} Installing tmate (this may take a minute)..."))
                    try:
                        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- apt-get update -y", timeout=180)
                        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- apt-get install -y tmate", timeout=120)
                    except Exception:
                        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- apt-get install -y wget tar openssh-client", timeout=120)
                        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- wget -q --timeout=30 https://github.com/tmate-io/tmate/releases/download/2.4.0/tmate-2.4.0-static-linux-amd64.tar.gz -O /tmp/tmate.tar.gz", timeout=120)
                        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- tar xzf /tmp/tmate.tar.gz -C /tmp/", timeout=30)
                        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- cp /tmp/tmate-2.4.0-static-linux-amd64/tmate /usr/local/bin/tmate", timeout=30)
                        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- chmod +x /usr/local/bin/tmate", timeout=30)

                await progress_msg.edit(embed=create_info_embed(f"{EMOJI_TMATE} Starting Tmate",
                    f"{EMOJI_LOADING} Generating SSH keys..."))
                await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- bash -c \"mkdir -p /root/.ssh && [ -f /root/.ssh/id_rsa ] || ssh-keygen -t rsa -f /root/.ssh/id_rsa -N '' -q\"", timeout=30)

                session_name = f"{BOT_NAME.lower()}-tmate-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- bash -c \"pkill -9 tmate 2>/dev/null; rm -f /tmp/{session_name}.sock\"", timeout=10)

                await progress_msg.edit(embed=create_info_embed(f"{EMOJI_TMATE} Starting Tmate",
                    f"{EMOJI_LOADING} Launching tmate session..."))
                await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- tmate -S /tmp/{session_name}.sock new-session -d", timeout=15)
                await asyncio.sleep(3)

                await progress_msg.edit(embed=create_info_embed(f"{EMOJI_TMATE} Starting Tmate",
                    f"{EMOJI_LOADING} Waiting for connection..."))

                ssh_url = None
                last_error = ""
                for attempt in range(15):
                    await asyncio.sleep(2)
                    ssh_proc = await asyncio.create_subprocess_exec(
                        "lxc", "exec", container_name, "--", "tmate", "-S", f"/tmp/{session_name}.sock", "display", "-p", "#{tmate_ssh}",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await ssh_proc.communicate()
                    if stdout:
                        url = stdout.decode().strip()
                        if url and not url.startswith("waiting") and "tmate" in url.lower():
                            ssh_url = url
                            break
                    if stderr:
                        last_error = stderr.decode().strip()

                if ssh_url:
                    try:
                        tmate_embed = create_info_embed(f"{EMOJI_TMATE} Tmate SSH Access", f"SSH connection for VPS `{container_name}`:")
                        add_field(tmate_embed, f"{EMOJI_TMATE} Command", f"```{ssh_url}```", False)
                        add_field(tmate_embed, f"{EMOJI_SYSTEM} Security", "This link is temporary. Do not share it.", False)

                        await interaction.user.send(embed=tmate_embed)
                        await progress_msg.edit(embed=create_success_embed(f"{EMOJI_SUCCESS} Tmate Ready", "Check your DMs for the SSH command!"))
                    except discord.Forbidden:
                        await progress_msg.edit(embed=create_error_embed(f"{EMOJI_WARNING} DM Failed", "Enable DMs to receive the SSH link!"))
                else:
                    if not last_error:
                        last_error = "Tmate session did not connect (timed out). Check internet connectivity in the container."
                    logger.error(f"Tmate failed for {container_name}: {last_error}")
                    await progress_msg.edit(embed=create_error_embed(f"{EMOJI_WARNING} Tmate Error", last_error))

            except Exception as e:
                logger.error(f"Tmate error for {container_name}: {e}", exc_info=True)
                err_str = str(e)
                if "not found" in err_str.lower():
                    err_str = f"VPS `{container_name}` no longer exists on the host."
                await progress_msg.edit(embed=create_error_embed(f"{EMOJI_WARNING} Tmate Error", err_str))

        if self.selected_index is not None and self.message:
            new_embed = await self.create_vps_embed(self.selected_index)
            await self.message.edit(embed=new_embed, view=self)


# ==================================================== VPS MANAGEMENT COMMANDS END =====================================================

# ==================================================== SHARE COMMANDS =====================================================

@bot.command(name='share-user')
@commands.cooldown(1, 3, commands.BucketType.user)
async def share_user(ctx, shared_user: discord.Member, vps_id: int):
    """Share VPS access with another user: share-user @user <vps-id>"""
    if not await maintenance_check(ctx):
        return

    user_id = str(ctx.author.id)
    shared_user_id = str(shared_user.id)

    vps = node_vps_get(vps_id)
    if not vps or str(vps['user_id']) != user_id:
        await ctx.send(embed=create_error_embed("Invalid VPS", "Invalid VPS id or you don't own this VPS."))
        return

    shared = node_vps_shared_list(vps)
    if shared_user_id in shared:
        await ctx.send(embed=create_error_embed("Already Shared", f"{shared_user.mention} already has access to this VPS!"))
        return

    shared.append(shared_user_id)
    node_vps_update(vps_id, shared_with=json.dumps(shared))

    embed = create_success_embed("VPS Shared", f"VPS `{vps_id}` (`{vps['container_name']}`) shared with {shared_user.mention}!")
    await ctx.send(embed=embed)

@bot.command(name='share-ruser')
@commands.cooldown(1, 3, commands.BucketType.user)
async def revoke_share(ctx, shared_user: discord.Member, vps_id: int):
    """Revoke VPS access from another user: share-ruser @user <vps-id>"""
    if not await maintenance_check(ctx):
        return

    user_id = str(ctx.author.id)
    shared_user_id = str(shared_user.id)

    vps = node_vps_get(vps_id)
    if not vps or str(vps['user_id']) != user_id:
        await ctx.send(embed=create_error_embed("Invalid VPS", "Invalid VPS id or you don't own this VPS."))
        return

    shared = node_vps_shared_list(vps)
    if shared_user_id not in shared:
        await ctx.send(embed=create_error_embed("Not Shared", f"{shared_user.mention} doesn't have access to this VPS!"))
        return

    shared.remove(shared_user_id)
    node_vps_update(vps_id, shared_with=json.dumps(shared))

    embed = create_success_embed("Access Revoked", f"Access to VPS `{vps_id}` revoked from {shared_user.mention}!")
    await ctx.send(embed=embed)

# NOTE: manage-shared is implemented as a node-aware command in the
# multi-node management section (see manage_shared_remote).

# ==================================================== SHARE COMMANDS END =====================================================

# ==================================================== ADMIN INFO COMMANDS =====================================================








# ==================================================== ADMIN INFO COMMANDS END =====================================================

# ==================================================== BOT SYSTEM COMMANDS =====================================================

@bot.command(name='addinv')
@is_admin()
@commands.cooldown(1, 2, commands.BucketType.user)
async def add_invites(ctx, user: discord.Member, amount: int):
    """Add invites to user"""
    if amount <= 0:
        await ctx.send(embed=create_error_embed("Invalid Amount", "Amount must be positive."))
        return
    
    update_user_stats(str(user.id), invites=amount)
    stats = get_user_stats(str(user.id))
    
    embed = create_success_embed("Invites Added", f"Added **{amount}** invites to {user.mention}")
    add_field(embed, "Current Stats", 
              f"**Total Invites:** {stats['invites']}\n**Boosts:** {stats['boosts']}", 
              False)
    await ctx.send(embed=embed)

@bot.command(name='removeinv')
@is_admin()
@commands.cooldown(1, 2, commands.BucketType.user)
async def remove_invites(ctx, user: discord.Member, amount: int):
    """Remove invites from user"""
    if amount <= 0:
        await ctx.send(embed=create_error_embed("Invalid Amount", "Amount must be positive."))
        return
    
    stats = get_user_stats(str(user.id))
    if stats['invites'] < amount:
        amount = stats['invites']
    
    update_user_stats(str(user.id), invites=-amount)
    new_stats = get_user_stats(str(user.id))
    
    embed = create_success_embed("Invites Removed", f"Removed **{amount}** invites from {user.mention}")
    add_field(embed, "Current Stats", 
              f"**Total Invites:** {new_stats['invites']}\n**Boosts:** {new_stats['boosts']}", 
              False)
    await ctx.send(embed=embed)

@bot.command(name='addboost')
@is_admin()
@commands.cooldown(1, 2, commands.BucketType.user)
async def add_boosts(ctx, user: discord.Member, amount: int):
    """Add boosts to user"""
    if amount <= 0:
        await ctx.send(embed=create_error_embed("Invalid Amount", "Amount must be positive."))
        return
    
    update_user_stats(str(user.id), boosts=amount)
    stats = get_user_stats(str(user.id))
    
    embed = create_success_embed("Boosts Added", f"Added **{amount}** boosts to {user.mention}")
    add_field(embed, "Current Stats", 
              f"**Invites:** {stats['invites']}\n**Total Boosts:** {stats['boosts']}", 
              False)
    await ctx.send(embed=embed)

@bot.command(name='removeboost')
@is_admin()
@commands.cooldown(1, 2, commands.BucketType.user)
async def remove_boosts(ctx, user: discord.Member, amount: int):
    """Remove boosts from user"""
    if amount <= 0:
        await ctx.send(embed=create_error_embed("Invalid Amount", "Amount must be positive."))
        return
    
    stats = get_user_stats(str(user.id))
    if stats['boosts'] < amount:
        amount = stats['boosts']
    
    update_user_stats(str(user.id), boosts=-amount)
    new_stats = get_user_stats(str(user.id))
    
    embed = create_success_embed("Boosts Removed", f"Removed **{amount}** boosts from {user.mention}")
    add_field(embed, "Current Stats", 
              f"**Invites:** {new_stats['invites']}\n**Total Boosts:** {new_stats['boosts']}", 
              False)
    await ctx.send(embed=embed)

@bot.command(name='user-stats')
@is_admin()
@commands.cooldown(1, 2, commands.BucketType.user)
async def user_stats_cmd(ctx, user: discord.Member):
    """View user stats"""
    stats = get_user_stats(str(user.id))
    
    embed = create_info_embed(f"User Stats - {user.name}", f"Statistics for {user.mention}")
    add_field(embed, "📨 Invites", str(stats['invites']), True)
    add_field(embed, "🚀 Boosts", str(stats['boosts']), True)
    add_field(embed, "🖥️ VPS Owned", str(len(node_vps_user(str(user.id)))), True)
    add_field(embed, "🎁 Claimed VPS", str(stats.get('claimed_vps_count', 0)), True)
    
    await ctx.send(embed=embed)

@bot.command(name='invite-logs')
@is_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def invite_logs_cmd(ctx, user: discord.Member = None):
    """View invite logs - shows who invited whom"""
    if user:
        logs = get_invite_logs(str(user.id))
        title = f"Invite Logs for {user.name}"
    else:
        logs = get_invite_logs()
        title = "Recent Invite Logs"
    if not logs:
        await ctx.send(embed=create_info_embed(title, "No invite logs found."))
        return
    embed = create_info_embed(title, f"Found **{len(logs)}** entries")
    text = ""
    for log in logs[:20]:
        action_emoji = EMOJI_ONLINE if log['action'] == 'joined' else EMOJI_OFFLINE
        text += f"{action_emoji} **{log['user_name']}** (`{log['user_id']}`) {log['action']} via `{log['code']}` by <@{log['inviter_id']}>\n"
    if len(text) > 1024:
        mid = len(text) // 2
        split_point = text.rfind('\n', 0, mid) + 1
        add_field(embed, "Logs (1/2)", text[:split_point], False)
        add_field(embed, "Logs (2/2)", text[split_point:], False)
    else:
        add_field(embed, "Logs", text, False)
    await ctx.send(embed=embed)

@bot.command(name='boost-logs')
@is_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def boost_logs_cmd(ctx, user: discord.Member = None):
    """View boost logs - who boosted/unboosted"""
    if user:
        logs = get_boost_logs(str(user.id))
        title = f"Boost Logs for {user.name}"
    else:
        logs = get_boost_logs()
        title = "Recent Boost Logs"
    if not logs:
        await ctx.send(embed=create_info_embed(title, "No boost logs found."))
        return
    embed = create_info_embed(title, f"Found **{len(logs)}** entries")
    text = ""
    for log in logs[:20]:
        action_emoji = EMOJI_STAR if log['action'] == 'boosted' else EMOJI_CROSS
        text += f"{action_emoji} **{log['user_name']}** (`{log['user_id']}`) {log['action']}\n"
    if len(text) > 1024:
        mid = len(text) // 2
        split_point = text.rfind('\n', 0, mid) + 1
        add_field(embed, "Logs (1/2)", text[:split_point], False)
        add_field(embed, "Logs (2/2)", text[split_point:], False)
    else:
        add_field(embed, "Logs", text, False)
    await ctx.send(embed=embed)

# ==================================================== BOT SYSTEM COMMANDS END =====================================================

# ==================================================== PURGE PROTECTION COMMANDS =====================================================

@bot.command(name='purge-prot')
@is_main_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def purge_protect(ctx, vps_id: int = None):
    """Protect a VPS from purge-vm-all: purge-prot <vps-id>"""
    if vps_id is None:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}purge-prot <vps-id>`"))
        return

    vps = node_vps_get(vps_id)
    if not vps:
        await ctx.send(embed=create_error_embed("VPS Not Found", f"No VPS with id `{vps_id}`."))
        return

    if vps.get('purge_protected'):
        embed = create_info_embed("Already Protected", f"VPS `{vps_id}` (`{vps['container_name']}`) is already purge protected.")
    else:
        node_vps_update(vps_id, purge_protected=1)
        log_purge_protection(vps['container_name'], vps['user_id'], 'protect', str(ctx.author.id))
        embed = create_success_embed("Purge Protection Enabled",
            f"VPS `{vps_id}` (`{vps['container_name']}`) is now protected from `{PREFIX}purge-vm-all`.")
    await ctx.send(embed=embed)

@bot.command(name='purge-remove-prot')
@is_main_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def purge_remove_protect(ctx, vps_id: int = None):
    """Remove purge protection from a VPS: purge-remove-prot <vps-id>"""
    if vps_id is None:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}purge-remove-prot <vps-id>`"))
        return

    vps = node_vps_get(vps_id)
    if not vps:
        await ctx.send(embed=create_error_embed("VPS Not Found", f"No VPS with id `{vps_id}`."))
        return

    if not vps.get('purge_protected'):
        embed = create_info_embed("Not Protected", f"VPS `{vps_id}` (`{vps['container_name']}`) is not purge protected.")
    else:
        node_vps_update(vps_id, purge_protected=0)
        log_purge_protection(vps['container_name'], vps['user_id'], 'remove_protect', str(ctx.author.id))
        embed = create_success_embed("Purge Protection Removed",
            f"VPS `{vps_id}` (`{vps['container_name']}`) is no longer protected from `{PREFIX}purge-vm-all`.")
    await ctx.send(embed=embed)

@bot.command(name='purge-status')
@is_main_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def purge_status(ctx, vps_id: int = None):
    """Check if a VPS is purge protected: purge-status <vps-id>"""
    if vps_id is None:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}purge-status <vps-id>`"))
        return

    vps = node_vps_get(vps_id)
    if not vps:
        await ctx.send(embed=create_error_embed("VPS Not Found", f"No VPS with id `{vps_id}`."))
        return

    protected = bool(vps.get('purge_protected'))
    status_text = f"{EMOJI_ONLINE} Protected" if protected else f"{EMOJI_OFFLINE} Not Protected"
    embed = create_info_embed("Purge Protection Status",
        f"VPS `{vps_id}` (`{vps['container_name']}`)\n**Status:** {status_text}")
    try:
        user = await bot.fetch_user(int(vps['user_id']))
        add_field(embed, "Owner", f"{user.mention} (`{vps['user_id']}`)", False)
    except Exception:
        add_field(embed, "Owner", f"`{vps['user_id']}`", False)
    add_field(embed, "Node", f"`{node_name_of(vps.get('node_id'))}`", True)
    add_field(embed, "Plan", f"`{vps.get('plan_name') or 'Custom'}`", True)
    await ctx.send(embed=embed)

async def _purge_list_embed(ctx, node_id, protected: bool):
    name = 'purge-list-prot' if protected else 'purge-list-unprot'
    if not node_id:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}{name} <node-name>`"))
        return
    node = node_resolve(node_id)
    if not node:
        await ctx.send(embed=create_error_embed("Node Not Found", f"No node with name `{node_id}`."))
        return
    node_id = node['node_id']
    node_label = node_display_name(node)

    rows = []
    for vps in node_vps_all():
        if vps.get('node_id') != node_id:
            continue
        if bool(vps.get('purge_protected')) != protected:
            continue
        try:
            user = await bot.fetch_user(int(vps['user_id']))
            username = user.name
        except Exception:
            username = f"Unknown User ({vps['user_id']})"
        rows.append(f"• **{username}** - `{vps['container_name']}` ({vps.get('plan_name') or 'Custom'})")

    label = "Protected" if protected else "Unprotected"
    if not rows:
        embed = create_info_embed(f"Purge {label} VPS", f"No {label.lower()} VPS found on `{node_label}`.")
    else:
        embed = create_info_embed(f"Purge {label} VPS", f"Found **{len(rows)}** {label.lower()} VPS on `{node_label}`")
        chunks = [rows[i:i+10] for i in range(0, len(rows), 10)]
        for i, chunk in enumerate(chunks):
            add_field(embed, f"{label} VPS {i+1}", "\n".join(chunk), False)

    await ctx.send(embed=embed)


@bot.command(name='purge-list-prot')
@is_main_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def purge_list_prot(ctx, node_id: str = None):
    """List all purge protected VPS on a node"""
    await _purge_list_embed(ctx, node_id, protected=True)


@bot.command(name='purge-list-unprot')
@is_main_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def purge_list_unprot(ctx, node_id: str = None):
    """List all purge unprotected VPS on a node"""
    await _purge_list_embed(ctx, node_id, protected=False)

# ==================================================== PURGE PROTECTION COMMANDS END =====================================================

# ==================================================== UPDATED ADMIN COMMANDS - SERVER STATS =====================================================

@bot.command(name='serverstats')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def server_stats(ctx):
    """Server statistics - Shows detailed server overview"""
    
    all_rows = node_vps_all()
    total_users = len({v['user_id'] for v in all_rows})
    total_admins = len(admin_data.get("admins", [])) + len(MAIN_ADMIN_IDS)  # + main admins

    total_vps = 0
    running_vps = 0
    suspended_vps = 0
    whitelisted_vps = 0
    stopped_vps = 0

    total_ram = 0
    total_cpu = 0
    total_storage = 0

    for vps in all_rows:
        total_vps += 1

        # Parse resources (remove unit, keep decimals)
        try:
            ram_value = _to_num(vps.get('ram'))
            total_ram += ram_value
        except Exception:
            pass

        try:
            cpu_value = _to_num(vps.get('cpu'))
            total_cpu += cpu_value
        except Exception:
            pass

        try:
            storage_value = _to_num(vps.get('disk'))
            total_storage += storage_value
        except Exception:
            pass

        # Count status
        if vps.get('status') == 'running':
            running_vps += 1
        else:
            stopped_vps += 1

        if vps.get('status') == 'suspended':
            suspended_vps += 1
        if vps.get('whitelisted'):
            whitelisted_vps += 1
    
    # Port statistics
    total_port_allocation = 0
    total_port_used = 0
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT SUM(allocated_ports) FROM port_allocations')
    result = cur.fetchone()
    if result and result[0]:
        total_port_allocation = result[0]
    
    cur.execute('SELECT COUNT(*) FROM port_forwards')
    result = cur.fetchone()
    if result and result[0]:
        total_port_used = result[0]
    conn.close()
    
    # Create the embed
    embed = discord.Embed(
        title=f"{EMOJI_STAR} {BOT_NAME} - Server Statistics",
        description="## Current server overview",
        color=0x00ccff
    )
    
    # Set thumbnail if URL is provided
    if THUMBNAIL_URL:
        embed.set_thumbnail(url=THUMBNAIL_URL)
    
    # Set footer with timestamp and icon
    embed.set_footer(
        text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        icon_url=THUMBNAIL_URL
    )
    
    # Users section
    users_text = f"- **Total Users:** {total_users}\n- **Total Admins:** {total_admins}"
    embed.add_field(name="**Users**", value=users_text, inline=False)
    
    # VPS section
    vps_text = f"- **Total VPS:** {total_vps}\n- **Running:** {running_vps}\n- **Suspended:** {suspended_vps}\n- **Whitelisted:** {whitelisted_vps}\n- **Stopped:** {stopped_vps}"
    embed.add_field(name="**VPS**", value=vps_text, inline=False)
    
    # Resources section
    resources_text = f"- **Total RAM:** {total_ram}GB\n- **Total CPU:** {total_cpu} cores\n- **Total Storage:** {total_storage}GB"
    embed.add_field(name="**Resources**", value=resources_text, inline=False)
    
    # Ports section
    ports_text = f"- **Allocated:** {total_port_allocation}\n- **In Use:** {total_port_used}"
    embed.add_field(name="**Ports**", value=ports_text, inline=False)
    
    await ctx.send(embed=embed)

# ==================================================== UPDATED ADMIN COMMANDS - SERVER STATS END =====================================================

# ==================================================== UPDATED ADMIN COMMANDS - LIST ALL VPS =====================================================


# ==================================================== UPDATED ADMIN COMMANDS - LIST ALL VPS END =====================================================

# ==================================================== OTHER ADMIN COMMANDS =====================================================

@bot.command(name='admin-add')
@is_main_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def admin_add(ctx, user: discord.Member):
    """Add admin"""
    user_id = str(user.id)
    
    if user_id in MAIN_ADMIN_IDS:
        await ctx.send(embed=create_error_embed("Already Admin", "This user is already a main admin!"))
        return
    
    if user_id in admin_data.get("admins", []):
        await ctx.send(embed=create_error_embed("Already Admin", f"{user.mention} is already an admin!"))
        return
    
    admin_data["admins"].append(user_id)
    save_admin_data()
    
    embed = create_success_embed("Admin Added", f"{user.mention} has been added as an admin!")
    await ctx.send(embed=embed)

@bot.command(name='admin-remove')
@is_main_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def admin_remove(ctx, user: discord.Member):
    """Remove admin"""
    user_id = str(user.id)
    
    if user_id in MAIN_ADMIN_IDS:
        await ctx.send(embed=create_error_embed("Cannot Remove", "You cannot remove a main admin!"))
        return
    
    if user_id not in admin_data.get("admins", []):
        await ctx.send(embed=create_error_embed("Not Admin", f"{user.mention} is not an admin!"))
        return
    
    admin_data["admins"].remove(user_id)
    save_admin_data()
    
    embed = create_success_embed("Admin Removed", f"{user.mention} has been removed as an admin!")
    await ctx.send(embed=embed)

@bot.command(name='admin-list')
@is_main_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def admin_list(ctx):
    """List admins"""
    embed = create_info_embed("Admin List", "Current administrators of the system")
    
    main_admin_text = []
    for admin_id in MAIN_ADMIN_IDS:
        try:
            main_admin_user = await bot.fetch_user(int(admin_id))
            main_admin_text.append(f"• {main_admin_user.mention}")
        except:
            main_admin_text.append(f"• User ID: {admin_id}")
    add_field(embed, f"{EMOJI_MAIN_ADMIN} Main Admins", "\n".join(main_admin_text), False)
    
    if admin_data['admins']:
        admin_text = []
        for admin_id in admin_data['admins']:
            try:
                admin_user = await bot.fetch_user(int(admin_id))
                admin_text.append(f"• {admin_user.mention}")
            except:
                admin_text.append(f"• User ID: {admin_id}")
        
        add_field(embed, f"{EMOJI_ADMIN} Admins", "\n".join(admin_text), False)
    else:
        add_field(embed, f"{EMOJI_ADMIN} Admins", "No additional admins", False)
    
    await ctx.send(embed=embed)

@bot.command(name='create')
@is_admin()
@commands.cooldown(1, 10, commands.BucketType.user)
async def create_vps(ctx, ram: float, cpu: float, disk: float, time: str, *, tail: str = None):
    """Create a VPS with OS selection.
    Usage: $create <ram> <cpu> <disk> <time> <up/down> <y/n> @user <node-name> [flags]
    Bandwidth <up/down> e.g. 1kbps/900kbps (up=upload, down=download).
      small b = BITS (mbps/Mbps), capital B = BYTES (MBps/GBps, 8x).
    <y/n> = enable/disable the Ports button in $manage for the owner (admins always allowed).
    Flags: --bypass_cpu, --bypass_ram, --bypass_disk, --bypass_all (combine freely).
    Time formats: 1s, 1m, 1h, 1d, 1month, 1year"""
    if ram <= 0 or cpu <= 0 or disk <= 0:
        await ctx.send(embed=create_error_embed("Invalid Specs", "RAM, CPU, and Disk must be positive numbers."))
        return

    raw = (tail or '').strip()
    user = ctx.message.mentions[0] if ctx.message.mentions else None
    if user is not None:
        raw = re.sub(r'<@!?\d+>', ' ', raw)

    bandwidth_spec = None
    ports_spec = None
    node_tokens = []
    flags = []
    toks = raw.split()
    i = 0
    while i < len(toks):
        t = toks[i]
        if t.startswith('--'):
            if t == '--node':
                if i + 1 >= len(toks):
                    await ctx.send(embed=create_error_embed("Invalid Flag",
                        "`--node` requires a node name, e.g. `--node IN-NODE-1`"))
                    return
                node_tokens.append(toks[i + 1])
                i += 2
                continue
            flags.append(t)
        elif t.lower() in ('y', 'yes', 'n', 'no') and ports_spec is None:
            ports_spec = 'y' if t.lower() in ('y', 'yes') else 'n'
        elif '/' in t and bandwidth_spec is None:
            bandwidth_spec = t
        else:
            node_tokens.append(t)
        i += 1

    ports_enabled = 0 if ports_spec == 'n' else 1

    remote_node_id = node_tokens[0] if node_tokens else None
    if len(node_tokens) > 1:
        await ctx.send(embed=create_error_embed("Too Many Arguments",
            f"Unexpected extra argument(s): `{' '.join(node_tokens[1:])}`."))
        return
    if user is None:
        await ctx.send(embed=create_error_embed("User Required",
            f"Mention the VPS owner, e.g. `{PREFIX}create 1 1 10 30d 1kbps/900kbps @user <node-name>`."))
        return

    bandwidth = None
    if bandwidth_spec:
        try:
            bandwidth = parse_bandwidth(bandwidth_spec)
        except ValueError as e:
            await ctx.send(embed=create_error_embed("Invalid Bandwidth", str(e)))
            return

    bypasses = {'--bypass_cpu': False, '--bypass_ram': False, '--bypass_disk': False}
    valid_flags = {'--bypass_cpu', '--bypass_ram', '--bypass_disk', '--bypass_all'}
    for f in flags:
        if f not in valid_flags:
            await ctx.send(embed=create_error_embed("Invalid Flag",
                f"`{f}` is not valid. Valid flags: `--bypass_cpu`, `--bypass_ram`, `--bypass_disk`, `--bypass_all`"))
            return
    if '--bypass_all' in flags:
        bypasses = {'--bypass_cpu': True, '--bypass_ram': True, '--bypass_disk': True}
    else:
        for f in flags:
            bypasses[f] = True

    bypass_cpu = bypasses['--bypass_cpu']
    bypass_ram = bypasses['--bypass_ram']
    bypass_disk = bypasses['--bypass_disk']

    if not remote_node_id:
        await ctx.send(embed=create_error_embed("Node Required",
            f"This bot is **node-only**. Provide the target node name at the end:\n"
            f"`{PREFIX}create <ram> <cpu> <disk> <time> <up/down> @user <node-name>`\n"
            f"See `{PREFIX}node-list` for available node names."))
        return

    node = node_resolve(remote_node_id)
    if not node:
        await ctx.send(embed=create_error_embed("Unknown Node", f"No node with name `{remote_node_id}`."))
        return
    node_id = node['node_id']
    node_label = node_display_name(node)

    time_delta = parse_time_string(time)
    if not time_delta:
        await ctx.send(embed=create_error_embed("Invalid Time Format",
            "Use formats like: `1s`, `1m`, `1h`, `1d`, `1month`, `1year`"))
        return
    time_display = f"\n{EMOJI_UPTIME} **Timer:** {format_timedelta(time_delta)}"

    bypass_parts = []
    if bypass_cpu:
        bypass_parts.append("CPU")
    if bypass_ram:
        bypass_parts.append("RAM")
    if bypass_disk:
        bypass_parts.append("Disk")
    bypass_text = f"\n{EMOJI_WARNING} **Bypass:** `{', '.join(bypass_parts)}`" if bypass_parts else ""

    msg = await ctx.send(embed=create_info_embed("Checking Resources",
        f"{EMOJI_LOADING} Verifying available resources on `{node_label}`..."))
    client = node_client(node)
    try:
        res = await client.check_resources()
    except NodeError as e:
        await msg.edit(embed=create_error_embed("Node Offline", f"`{node_label}`: {e}"))
        return
    avail_cpu = res.get('cpu', {}).get('available', 0)
    avail_ram = res.get('ram', {}).get('available_gb', 0)
    avail_disk = res.get('disk', {}).get('available_gb', 0)
    if cpu > avail_cpu or ram > avail_ram or disk > avail_disk:
        await msg.edit(embed=create_error_embed("Not Enough Resources",
            f"{EMOJI_WARNING} Requested `{_fmt_num(ram)}GB` RAM / `{_fmt_num(cpu)}` CPU / `{_fmt_num(disk)}GB` disk but "
            f"`{node_label}` has `{_fmt_num(avail_ram)}GB` RAM, `{_fmt_num(avail_cpu)}` CPU, `{_fmt_num(avail_disk)}GB` disk free."))
        return

    bw_text = ""
    if bandwidth_spec:
        bw_text = f"\n{EMOJI_GLOBAL} **Bandwidth:** `{bandwidth_spec}`"
    ports_text = f"\n{EMOJI_PORTS} **Ports:** {'Enabled' if ports_enabled else 'Disabled'}"
    embed = create_info_embed("VPS Creation",
        f"Creating VPS for {user.mention}\n"
        f"**RAM:** {_fmt_num(ram)}GB\n"
        f"**CPU:** {_fmt_num(cpu)} Cores\n"
        f"**Disk:** {_fmt_num(disk)}GB{time_display}{bw_text}{ports_text}{bypass_text}\n\n"
        f"Select OS below.")
    view = RemoteOSSelectView(ram, cpu, disk, user, ctx, time, node_label, bandwidth=bandwidth,
                              bandwidth_spec=bandwidth_spec if bandwidth_spec else None,
                              ports_enabled=ports_enabled,
                              bypass_cpu=bypass_cpu, bypass_ram=bypass_ram, bypass_disk=bypass_disk)
    await msg.edit(embed=embed, view=view)

class AdminOSSelectView(discord.ui.View):
    def __init__(self, ram: int, cpu: int, disk: int, user: discord.Member, ctx, time_arg: str = None,
                 bypass_cpu=False, bypass_ram=False, bypass_disk=False):
        super().__init__(timeout=300)
        self.ram = ram
        self.cpu = cpu
        self.disk = disk
        self.user = user
        self.ctx = ctx
        self.time_arg = time_arg
        self.bypass_cpu = bypass_cpu
        self.bypass_ram = bypass_ram
        self.bypass_disk = bypass_disk
        self.selected_os = None
        
        options = []
        for o in OS_OPTIONS:
            emoji = o.get('emoji', '🐧')
            description = o.get('description', '')
            options.append(discord.SelectOption(
                label=o["label"], 
                value=o["value"], 
                emoji=emoji,
                description=description
            ))
        
        self.select = discord.ui.Select(
            placeholder="Select an OS for the VPS",
            options=options
        )
        self.select.callback = self.select_os
        self.add_item(self.select)
        cancel_btn = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger, row=1, emoji=EMOJI_CROSS)
        async def cancel_btn_cb(interaction: discord.Interaction):
            if str(interaction.user.id) != str(self.ctx.author.id):
                await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can cancel."), ephemeral=True)
                return
            await interaction.response.edit_message(embed=create_info_embed("Cancelled", "VPS creation cancelled."), view=None)
        cancel_btn.callback = cancel_btn_cb
        self.add_item(cancel_btn)
    
    async def select_os(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.ctx.author.id):
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can select."), ephemeral=True)
            return
        
        self.selected_os = self.select.values[0]
        await interaction.response.defer()
        
        confirm_view = discord.ui.View()
        confirm_button = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.success, emoji=EMOJI_SUCCESS)
        cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger, emoji=EMOJI_CROSS)
        
        async def confirm_callback(confirm_interaction):
            await self.create_vps(confirm_interaction)
        
        async def cancel_callback(cancel_interaction):
            if str(cancel_interaction.user.id) != str(self.ctx.author.id):
                await cancel_interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can cancel."), ephemeral=True)
                return
            await cancel_interaction.response.edit_message(embed=create_info_embed("Cancelled", "VPS creation cancelled."), view=None)
        
        confirm_button.callback = confirm_callback
        cancel_button.callback = cancel_callback
        
        confirm_view.add_item(confirm_button)
        confirm_view.add_item(cancel_button)
        
        time_confirm = ""
        if self.time_arg:
            td = parse_time_string(self.time_arg)
            if td:
                time_confirm = f"\n{EMOJI_UPTIME} **Timer:** {format_timedelta(td)}"

        bypass_parts = []
        if self.bypass_cpu: bypass_parts.append("CPU")
        if self.bypass_ram: bypass_parts.append("RAM")
        if self.bypass_disk: bypass_parts.append("Disk")
        bypass_display = f"\n{EMOJI_WARNING} **Bypassing:** {', '.join(bypass_parts)}" if bypass_parts else ""

        embed = create_info_embed("Confirm VPS Creation", 
            f"**User:** {self.user.mention}\n"
            f"**OS:** {get_os_emoji(self.selected_os)} {self.selected_os}\n"
            f"**RAM:** {_fmt_num(self.ram)}GB\n"
            f"**CPU:** {_fmt_num(self.cpu)} Cores\n"
            f"**Disk:** {_fmt_num(self.disk)}GB{time_confirm}{bypass_display}\n\n"
            f"Please confirm to proceed.")
        
        await interaction.edit_original_response(embed=embed, view=confirm_view)
    
    async def create_vps(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        user_id = str(self.user.id)
        allowed, limit_msg = check_vps_limit(user_id, is_paid=True)
        if not allowed:
            await interaction.edit_original_response(
                embed=create_error_embed("VPS Limit Reached", limit_msg), view=None)
            return
        
        can_create, error_msg = await check_resources(self.ram, self.cpu, self.disk,
            bypass_cpu=self.bypass_cpu, bypass_ram=self.bypass_ram, bypass_disk=self.bypass_disk)
        if not can_create:
            await interaction.edit_original_response(
                embed=create_error_embed("Insufficient Resources", error_msg), view=None)
            return
        
        creating_embed = create_info_embed("Creating VPS", f"{EMOJI_LOADING} Deploying {self.selected_os} VPS for {self.user.mention}...")
        await interaction.edit_original_response(embed=creating_embed, view=None)
        
        if user_id not in vps_data:
            vps_data[user_id] = []
        
        existing_nums = [get_vps_number(v['container_name']) for v in vps_data.get(user_id, [])]
        existing_nums = [n for n in existing_nums if n is not None]
        vps_count = max(existing_nums) + 1 if existing_nums else 1
        container_name = f"{BOT_NAME.lower()}-vps-{user_id}-{vps_count}"
        
        try:
            await ensure_lxdbr0()

            resolved_os = await ensure_image_available(self.selected_os)
            await ensure_container_name_available(container_name)
            await execute_lxc(f"lxc init {resolved_os} {shlex.quote(container_name)} -s {DEFAULT_STORAGE_POOL}", timeout=600)
            await apply_resource_limits(container_name, ram_gb=self.ram, cpu_cores=self.cpu, disk_gb=self.disk)
            await apply_lxc_config(container_name)
            await execute_lxc(f"lxc start {shlex.quote(container_name)}")
            await apply_internal_permissions(container_name)

            creating_embed.description = f"{EMOJI_GLOBAL} Fixing internet for `{container_name}`..."
            await interaction.edit_original_response(embed=creating_embed)
            progress_msg = await interaction.original_response()
            await fix_container_internet(container_name, msg=progress_msg)

            creating_embed.description = f"{EMOJI_LOADING} Finalizing..."
            await interaction.edit_original_response(embed=creating_embed)

            config_str = f"{_fmt_num(self.ram)}GB RAM / {_fmt_num(self.cpu)} CPU / {_fmt_num(self.disk)}GB Disk"
            expires_at = ""
            timer_status = ""
            td = None
            if self.time_arg:
                td = parse_time_string(self.time_arg)
                if td:
                    expires_at = (datetime.now() + td).isoformat()
                    timer_status = "running"
            vps_info = {
                "container_name": container_name,
                "plan_name": "Custom",
                "ram": f"{_fmt_num(self.ram)}GB",
                "cpu": _fmt_num(self.cpu),
                "storage": f"{_fmt_num(self.disk)}GB",
                "config": config_str,
                "os_version": self.selected_os,
                "status": "running",
                "suspended": False,
                "whitelisted": False,
                "purge_protected": False,
                "suspended_reason": "",
                "suspension_history": [],
                "created_at": datetime.now().isoformat(),
                "shared_with": [],
                "id": None,
                "expires_at": expires_at,
                "timer_paused_at": "",
                "timer_status": timer_status
            }
            vps_data[user_id].append(vps_info)
            save_vps_data()
            
            timer_success = f"\n{EMOJI_UPTIME} **Timer:** {format_timedelta(td)}" if td else ""
            success_embed = create_success_embed("VPS Created Successfully")
            add_field(success_embed, "Owner", self.user.mention, True)
            add_field(success_embed, "VPS ID", f"#{vps_count}", True)
            add_field(success_embed, "Container", f"`{container_name}`", True)
            add_field(success_embed, "Resources", f"**RAM:** {_fmt_num(self.ram)}GB\n**CPU:** {_fmt_num(self.cpu)} Cores\n**Storage:** {_fmt_num(self.disk)}GB{timer_success}", False)
            add_field(success_embed, "OS", f"{get_os_emoji(self.selected_os)} {self.selected_os}", True)

            await interaction.followup.send(embed=success_embed)

            bypass_parts = []
            if self.bypass_cpu: bypass_parts.append("CPU")
            if self.bypass_ram: bypass_parts.append("RAM")
            if self.bypass_disk: bypass_parts.append("Disk")
            log_bypass = f"\n{EMOJI_WARNING} **Bypassed:** {', '.join(bypass_parts)}" if bypass_parts else ""
            log_timer = f"\n{EMOJI_UPTIME} **Timer:** {format_timedelta(td)}" if td else ""
            await send_log(EMOJI_ADMIN, "VPS Created by Admin",
                f"{EMOJI_USER} **User:** {self.user.mention} (`{user_id}`)\n"
                f"{EMOJI_ADMIN} **Admin:** {self.ctx.author.mention}\n"
                f"{EMOJI_VPS} **Container:** `{container_name}`\n"
                f"{EMOJI_RAM} **RAM:** {_fmt_num(self.ram)}GB | {EMOJI_CPU} **CPU:** {_fmt_num(self.cpu)} | {EMOJI_DISK} **Disk:** {_fmt_num(self.disk)}GB\n"
                f"{get_os_emoji(self.selected_os)} **OS:** {self.selected_os}{log_timer}{log_bypass}",
                color=0x00ff88)
            
            try:
                dm_embed = create_success_embed(f"{EMOJI_SUCCESS} VPS Created!", f"Your VPS has been successfully deployed by an admin!")
                created_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                vps_details = f"**VPS ID:** #{vps_count}\n"
                vps_details += f"**Container Name:** `{container_name}`\n"
                vps_details += f"**Configuration:** {config_str}\n"
                vps_details += f"**Status:** Running\n"
                vps_details += f"**OS:** {get_os_emoji(self.selected_os)} {self.selected_os}\n"
                vps_details += f"**Created:** {created_time}"
                
                add_field(dm_embed, "VPS Details", vps_details, False)
                add_field(dm_embed, "Management", 
                         f"• Use `{PREFIX}manage` to start/stop your VPS\n• Use `{PREFIX}manage` → SSH for terminal access\n• Contact admin for upgrades or issues", 
                         False)
                
                await self.user.send(embed=dm_embed)
            except discord.Forbidden:
                await self.ctx.send(embed=create_info_embed("Notification Failed", f"Couldn't send DM to {self.user.mention}. Please ensure DMs are enabled."))
            except Exception as e:
                logger.error(f"Failed to send DM to {self.user.id}: {e}")
        
        except Exception as e:
            error_embed = create_error_embed("Creation Failed", f"Error: {str(e)}")
            await interaction.followup.send(embed=error_embed)

# ==================================================== OTHER ADMIN COMMANDS END =====================================================

# ==================================================== DELETE-VPS COMMAND WITH CONFIRMATION =====================================================

class DeleteVPSView(discord.ui.View):
    def __init__(self, ctx, user, user_id, vps_number, vps_data_entry, container_name, reason):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.user = user
        self.user_id = user_id
        self.vps_number = vps_number
        self.vps_data_entry = vps_data_entry
        self.container_name = container_name
        self.reason = reason
        self.message = None
        self._completed = False
    
    async def on_timeout(self):
        if self._completed:
            return
        if self.message:
            try:
                embed = create_info_embed(f"{EMOJI_UPTIME} Timeout", "VPS deletion cancelled due to timeout.")
                await self.message.edit(embed=embed, view=None)
            except (discord.NotFound, discord.Forbidden):
                pass
    
    @discord.ui.button(label=f"Confirm Delete", style=discord.ButtonStyle.danger, emoji=EMOJI_WARNING)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can confirm this action."), ephemeral=True)
            return

        user_id = self.user_id

        progress = discord.Embed(
            title=f"{EMOJI_CROSS} Deleting VPS",
            description=f"{EMOJI_LOADING} Initializing deletion...",
            color=0xffaa00
        )
        progress.set_footer(text=f"{BOT_NAME} VPS Manager - Deleting...", icon_url=THUMBNAIL_URL)
        if THUMBNAIL_URL:
            progress.set_thumbnail(url=THUMBNAIL_URL)

        await interaction.response.edit_message(embed=progress, view=None)

        try:
            progress.description = f"{EMOJI_LOADING} Deleting container `{self.container_name}`..."
            await interaction.edit_original_response(embed=progress)

            try:
                await execute_lxc(f"lxc delete {shlex.quote(self.container_name)} --force")
            except Exception as e:
                if "not found" not in str(e).lower():
                    raise
                logger.warning(f"Container {self.container_name} already gone, cleaning up DB record")

            progress.description = f"{EMOJI_LOADING} Cleaning up database records..."
            await interaction.edit_original_response(embed=progress)

            conn = get_db()
            cur = conn.cursor()
            cur.execute('DELETE FROM port_forwards WHERE vps_container = ?', (self.container_name,))
            cur.execute('DELETE FROM vps WHERE container_name = ?', (self.container_name,))
            conn.commit()
            conn.close()

            if user_id in vps_data:
                vps_data[user_id] = [v for v in vps_data[user_id] if v['container_name'] != self.container_name]
                if not vps_data[user_id]:
                    del vps_data[user_id]

            save_vps_data()

            if self.vps_data_entry.get('plan_name', '') != 'Custom':
                update_user_stats(user_id, claimed_vps_count=-1)

            log_suspension(self.container_name, user_id, 'delete', self.reason, str(self.ctx.author.id))

            user_display = self.user.mention if self.user else f"`{user_id}`"
            await send_log(EMOJI_CROSS, "VPS Deleted",
                f"{EMOJI_USER} **User:** {user_display}\n"
                f"{EMOJI_ADMIN} **Deleted By:** {self.ctx.author.mention}\n"
                f"{EMOJI_VPS} **Container:** `{self.container_name}`\n"
                f"{EMOJI_VPS} **VPS #:** {self.vps_number}\n"
                f"{EMOJI_INFO} **Reason:** {self.reason}",
                color=0xff3366)

            try:
                if self.user:
                    dm_embed = create_warning_embed("VPS Deleted", f"Your VPS has been deleted by an admin.")
                    add_field(dm_embed, "Container", f"`{self.container_name}`", True)
                    add_field(dm_embed, "Reason", self.reason, False)
                    add_field(dm_embed, "Deleted By", self.ctx.author.mention, False)
                    await self.user.send(embed=dm_embed)
            except (discord.Forbidden, discord.HTTPException, Exception):
                logger.warning(f"Failed to send DM to {user_id} about VPS deletion")

            progress.title = f"{EMOJI_SUCCESS} VPS Deleted Successfully"
            progress.description = (
                f"{EMOJI_USER} **Owner:** {user_display}\n"
                f"{EMOJI_ADMIN} **Deleted By:** {self.ctx.author.mention}\n"
                f"{EMOJI_VPS} **Container:** `{self.container_name}`\n"
                f"{EMOJI_VPS} **VPS #:** {self.vps_number}\n"
                f"{EMOJI_INFO} **Reason:** {self.reason}"
            )
            progress.color = 0x00ff88
            progress.set_footer(text=f"{BOT_NAME} VPS Manager - Deleted", icon_url=THUMBNAIL_URL)

            self._completed = True
            for item in self.children:
                item.disabled = True
            await interaction.edit_original_response(embed=progress, view=self)

        except Exception as e:
            progress.title = f"{EMOJI_CROSS} Deletion Failed"
            progress.description = f"Error: {str(e)}"
            progress.color = 0xff3366
            progress.set_footer(text=f"{BOT_NAME} VPS Manager - Failed", icon_url=THUMBNAIL_URL)
            self._completed = True
            for item in self.children:
                item.disabled = True
            await interaction.edit_original_response(embed=progress, view=self)
    
    @discord.ui.button(label=f"Cancel", style=discord.ButtonStyle.secondary, emoji=EMOJI_CROSS)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can cancel this action."), ephemeral=True)
            return
        
        embed = create_info_embed(f"{EMOJI_SUCCESS} Operation Cancelled", "VPS deletion has been cancelled.")
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)


# ==================================================== DELETE-VPS COMMAND WITH CONFIRMATION END =====================================================

# ==================================================== PURGE ALL VMS COMMAND (1 BY 1 DELETION) =====================================================

class PurgeAllVMSView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.message = None
        self.is_running = False
    
    async def on_timeout(self):
        if self.message and not self.is_running:
            try:
                embed = create_info_embed("⏰ Timeout", "Purge operation cancelled due to timeout.")
                await self.message.edit(embed=embed, view=None)
            except (discord.NotFound, discord.Forbidden):
                pass
    
    @discord.ui.button(label=f"Confirm Purge All", style=discord.ButtonStyle.danger, emoji=EMOJI_WARNING)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can confirm this action."), ephemeral=True)
            return
        
        self.is_running = True
        button.disabled = True
        self.children[1].disabled = True  # Disable cancel button
        await interaction.response.edit_message(view=self)
        
        # Count only non-protected VPS
        total_vps = 0
        protected_vps = 0
        for user_id, vps_list in vps_data.items():
            for vps in vps_list:
                if vps.get('purge_protected', False):
                    protected_vps += 1
                else:
                    total_vps += 1
        
        if total_vps == 0:
            if protected_vps > 0:
                embed = create_info_embed("All VPS Protected", 
                    f"Found **{protected_vps}** protected VPS but no unprotected VPS to purge.\n"
                    f"Use `{PREFIX}purge-list-prot <node-name>` to see protected VPS.")
            else:
                embed = create_info_embed("No VPS Found", "There are no VPS to purge.")
            await interaction.followup.send(embed=embed)
            return
        
        # Create progress embed
        progress_embed = discord.Embed(
            title="🧹 Purging Unprotected VPS",
            description=f"Starting purge of {total_vps} unprotected VPS...\n"
                       f"({protected_vps} protected VPS will be skipped)\n"
                       f"This will delete **1 VPS every 3 seconds** to prevent high server load.",
            color=0xffaa00
        )
        
        # Set thumbnail if URL is provided
        if THUMBNAIL_URL:
            progress_embed.set_thumbnail(url=THUMBNAIL_URL)
        
        # Set footer with timestamp and icon
        progress_embed.set_footer(
            text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            icon_url=THUMBNAIL_URL
        )
        
        add_field(progress_embed, "Status", f"{EMOJI_LOADING} Initializing...", False)
        add_field(progress_embed, "Progress", f"0/{total_vps} (0%)", False)
        add_field(progress_embed, "Protected VPS", f"{EMOJI_ADMIN} {protected_vps} VPS skipped", False)
        
        progress_msg = await interaction.followup.send(embed=progress_embed)
        
        deleted_count = 0
        skipped_count = 0
        failed_count = 0
        users_affected = set()
        
        # Create a list of all unprotected VPS to delete
        all_vps = []
        for user_id, vps_list in list(vps_data.items()):
            for vps in vps_list[:]:  # Use a copy of the list
                if not vps.get('purge_protected', False):
                    all_vps.append((user_id, vps))
                else:
                    skipped_count += 1
        
        total_to_delete = len(all_vps)
        
        # Delete VPS one by one with delay
        for i, (user_id, vps) in enumerate(all_vps, 1):
            container_name = vps['container_name']
            
            try:
                # Delete the container (tolerate "already gone")
                try:
                    await execute_lxc(f"lxc delete {shlex.quote(container_name)} --force", timeout=60)
                except Exception as e:
                    if "not found" not in str(e).lower():
                        raise
                    logger.warning(f"Container {container_name} already gone, cleaning up DB")
                
                # Delete port forwards and vps record
                conn = get_db()
                cur = conn.cursor()
                cur.execute('DELETE FROM port_forwards WHERE vps_container = ?', (container_name,))
                cur.execute('DELETE FROM vps WHERE container_name = ?', (container_name,))
                conn.commit()
                conn.close()
                
                # Remove from vps_data
                if user_id in vps_data:
                    vps_data[user_id] = [v for v in vps_data[user_id] if v['container_name'] != container_name]
                    if not vps_data[user_id]:
                        del vps_data[user_id]
                
                if vps.get('plan_name', '') != 'Custom':
                    update_user_stats(user_id, claimed_vps_count=-1)

                # Log the deletion
                log_suspension(container_name, user_id, 'purge_all', f"Purged by {self.ctx.author.name}", str(self.ctx.author.id))
                
                deleted_count += 1
                users_affected.add(user_id)
                
                # Update progress every 5 deletions or at the end
                if i % 5 == 0 or i == total_to_delete:
                    percentage = int((i / total_to_delete) * 100) if total_to_delete > 0 else 100
                    progress_embed = discord.Embed(
                        title="🧹 Purging Unprotected VPS",
                        description=f"Progress: {i}/{total_to_delete} VPS processed",
                        color=0xffaa00
                    )
                    
                    # Set thumbnail if URL is provided
                    if THUMBNAIL_URL:
                        progress_embed.set_thumbnail(url=THUMBNAIL_URL)
                    
                    # Set footer with timestamp and icon
                    progress_embed.set_footer(
                        text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                        icon_url=THUMBNAIL_URL
                    )
                    
                    status_text = f"{EMOJI_SUCCESS} Deleted: {deleted_count}\n"
                    status_text += f"{EMOJI_ADMIN} Skipped (Protected): {skipped_count}\n"
                    status_text += f"{EMOJI_CROSS} Failed: {failed_count}\n"
                    status_text += f"{EMOJI_USER} Users Affected: {len(users_affected)}"
                    
                    add_field(progress_embed, "Status", status_text, False)
                    add_field(progress_embed, "Progress Bar", self.create_progress_bar(percentage), False)
                    add_field(progress_embed, "Protected VPS", f"{EMOJI_ADMIN} {protected_vps} VPS remain protected", False)
                    
                    await progress_msg.edit(embed=progress_embed)
                
                # Save data periodically
                if i % 10 == 0:
                    save_vps_data()
                
                # Wait 3 seconds before next deletion to prevent high load
                await asyncio.sleep(3)
                
            except Exception as e:
                logger.error(f"Failed to delete VPS {container_name}: {e}")
                failed_count += 1
                
                # Still wait even on failure
                await asyncio.sleep(3)
        
        # Final save
        save_vps_data()
        
        # Send completion embed
        final_embed = discord.Embed(
            title=f"{EMOJI_SUCCESS} Purge Complete",
            description=f"Successfully purged {deleted_count} unprotected VPS",
            color=0x00ff88
        )
        
        # Set thumbnail if URL is provided
        if THUMBNAIL_URL:
            final_embed.set_thumbnail(url=THUMBNAIL_URL)
        
        # Set footer with timestamp and icon
        final_embed.set_footer(
            text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            icon_url=THUMBNAIL_URL
        )
        
        summary = f"**Total Unprotected VPS:** {total_to_delete}\n"
        summary += f"**Successfully Deleted:** {deleted_count}\n"
        summary += f"**Failed Deletions:** {failed_count}\n"
        summary += f"**Protected VPS (Skipped):** {skipped_count}\n"
        summary += f"**Users Affected:** {len(users_affected)}"
        
        add_field(final_embed, "Summary", summary, False)
        
        if skipped_count > 0:
            add_field(final_embed, "Note", f"{EMOJI_ADMIN} {skipped_count} protected VPS were skipped. Use `{PREFIX}purge-list-prot <node-name>` to see them.", False)
        
        await progress_msg.edit(embed=final_embed)
        
        # Disable all buttons in original message
        for item in self.children:
            item.disabled = True
        await interaction.edit_original_response(view=self)
    
    def create_progress_bar(self, percentage, length=20):
        """Create a text progress bar"""
        filled = int(length * percentage / 100)
        bar = "█" * filled + "░" * (length - filled)
        return f"`[{bar}] {percentage}%`"
    
    @discord.ui.button(label=f"{EMOJI_CROSS} Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can cancel this action."), ephemeral=True)
            return
        
        embed = create_info_embed("Operation Cancelled", "Purge all VPS operation has been cancelled.")
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)



# ==================================================== PURGE ALL VMS COMMAND (1 BY 1 DELETION) END =====================================================

# ==================================================== ADDITIONAL ADMIN COMMANDS =====================================================






@bot.command(name='userinfo')
@is_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def user_info(ctx, user: discord.Member):
    """User information with VPS numbers"""
    user_id = str(user.id)
    vps_list = node_vps_user(user_id)
    stats = get_user_stats(user_id)

    embed = discord.Embed(
        title=f"User Information - {user.name}",
        description=f"Detailed information for {user.mention}",
        color=0x1a1a1a
    )

    # Set thumbnail if URL is provided
    if THUMBNAIL_URL:
        embed.set_thumbnail(url=THUMBNAIL_URL)

    # Set footer with timestamp and icon
    embed.set_footer(
        text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        icon_url=THUMBNAIL_URL
    )

    user_details = f"**Name:** {user.name}\n"
    user_details += f"**ID:** {user.id}\n"
    user_details += f"**Joined:** {user.joined_at.strftime('%Y-%m-%d %H:%M:%S') if user.joined_at else 'Unknown'}"

    add_field(embed, "User Details", user_details, False)

    # Stats
    stats_info = f"**Invites:** {stats.get('invites', 0)}\n"
    stats_info += f"**Boosts:** {stats.get('boosts', 0)}\n"
    add_field(embed, "User Stats", stats_info, True)

    if vps_list:
        vps_info = []
        for i, vps in enumerate(vps_list, 1):
            status_emoji = EMOJI_ONLINE if vps.get('status') == 'running' else EMOJI_OFFLINE
            status_text = (vps.get('status', 'unknown') or 'unknown').upper()
            purge_text = " (protected)" if vps.get('purge_protected') else ""
            node = node_get(vps['node_id'])
            node_ok = EMOJI_GOOD_SIGNAL if node else EMOJI_BAD_SIGNAL
            timer_line = get_vps_timer_line(vps)
            vps_info.append(f"{status_emoji} **VPS `{vps['vps_id']}`:** `{vps['container_name']}` - {status_text}{purge_text} {node_ok} `{node_display_name(node)}`{timer_line}")

        add_field(embed, f"VPS List ({len(vps_list)})", "\n".join(vps_info), False)
        add_field(embed, "Manage", f"`{PREFIX}manage {user.mention}`", False)
    else:
        add_field(embed, "VPS Information", "**No VPS owned**", False)

    # Port quota
    port_quota = get_user_allocation(user_id)
    port_used = get_user_used_ports(user_id)
    add_field(embed, "Port Quota", f"Allocated: {port_quota}, Used: {port_used}", False)

    # Admin status
    is_admin_user = user_id in MAIN_ADMIN_IDS or user_id in admin_data.get("admins", [])
    add_field(embed, "Admin Status", f"**{'Yes' if is_admin_user else 'No'}**", False)

    await ctx.send(embed=embed)

# ==================================================== ADDITIONAL ADMIN COMMANDS END =====================================================

# ==================================================== OTHER COMMANDS =====================================================







# ==================================================== OTHER COMMANDS END =====================================================

# ==================================================== SYSTEM COMMANDS =====================================================

def _build_bot_activity(kind, name):
    """Build a discord.Activity for the given type keyword and name."""
    kind = (kind or 'watching').lower()
    if kind == 'streaming':
        return discord.Activity(type=discord.ActivityType.streaming, name=name, url=name)
    mapping = {
        'playing': discord.ActivityType.playing,
        'listening': discord.ActivityType.listening,
        'watching': discord.ActivityType.watching,
        'competing': discord.ActivityType.competing,
    }
    return discord.Activity(type=mapping.get(kind, discord.ActivityType.watching), name=name)

async def _apply_bot_presence():
    """Apply the saved maintenance/mode/activity state to Discord.

    Used on startup and after gateway resumes. Falls back to a plain status
    (no activity) if the stored activity cannot be built, so the bot never
    ends up offline because of a bad/expired activity (e.g. streaming URL).
    """
    if MAINTENANCE_MODE:
        await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="🔧 Maintenance Mode"))
        return

    status_types = {
        'online': discord.Status.online,
        'idle': discord.Status.idle,
        'dnd': discord.Status.dnd,
        'invisible': discord.Status.invisible,
    }
    status = status_types.get(BOT_STATUS, discord.Status.online)

    try:
        activity = _build_bot_activity(BOT_ACTIVITY, BOT_ACTIVITY_NAME)
    except Exception:
        activity = discord.Activity(type=discord.ActivityType.watching, name=BOT_ACTIVITY_NAME)

    try:
        await bot.change_presence(status=status, activity=activity)
    except Exception:
        await bot.change_presence(status=status, activity=None)

@bot.command(name='set-status')
@is_main_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def set_status(ctx, activity_type: str, *, name: str):
    """Set bot status"""
    global BOT_ACTIVITY, BOT_ACTIVITY_NAME

    aliases = {
        'p': 'playing', 'playing': 'playing',
        's': 'streaming', 'streaming': 'streaming',
        'l': 'listening', 'listening': 'listening',
        'w': 'watching', 'watching': 'watching',
        'c': 'competing', 'competing': 'competing',
    }
    kind = aliases.get(activity_type.lower())
    if not kind:
        await ctx.send(embed=create_error_embed("Invalid Type",
            "Valid types: `p` (playing), `s` (streaming), `l` (listening), `w` (watching), `c` (competing)"))
        return

    if kind == 'streaming' and not name.lower().startswith(('http://', 'https://')):
        await ctx.send(embed=create_error_embed("Invalid URL",
            "Streaming requires a valid Twitch/YouTube URL, e.g. `set-status s https://twitch.tv/you`."))
        return

    try:
        await bot.change_presence(status=bot.status, activity=_build_bot_activity(kind, name))
    except Exception as e:
        await ctx.send(embed=create_error_embed("Status Failed", f"Could not set status: `{e}`"))
        return

    BOT_ACTIVITY = kind
    BOT_ACTIVITY_NAME = name
    set_setting('bot_activity', kind)
    set_setting('bot_activity_name', name)

    verbs = {
        'playing': 'Playing', 'streaming': 'Streaming', 'listening': 'Listening to',
        'watching': 'Watching', 'competing': 'Competing in',
    }
    embed = create_success_embed("Status Updated", f"Set to {verbs[kind]}: {name}")
    await ctx.send(embed=embed)

@bot.command(name='change-prefix')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def change_prefix(ctx, new_prefix: str):
    """Change the bot command prefix: change-prefix <new-prefix>"""
    global PREFIX

    if not new_prefix or any(c.isspace() for c in new_prefix):
        await ctx.send(embed=create_error_embed("Invalid Prefix", "The prefix cannot be empty or contain spaces."))
        return

    if len(new_prefix) > 5:
        await ctx.send(embed=create_error_embed("Invalid Prefix", "The prefix must be 5 characters or fewer."))
        return

    old_prefix = PREFIX
    PREFIX = new_prefix
    set_setting('prefix', new_prefix)

    embed = create_success_embed("Prefix Changed", f"Command prefix changed from `{old_prefix}` to `{new_prefix}`.")
    add_field(embed, "Example", f"`{new_prefix}help`", True)
    await ctx.send(embed=embed)

@bot.command(name='change-mode')
@is_main_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def change_mode(ctx, mode: str):
    """Change bot mode"""
    global BOT_STATUS

    modes = {
        'online': discord.Status.online,
        'idle': discord.Status.idle,
        'dnd': discord.Status.dnd,
        'invis': discord.Status.invisible,
        'invisible': discord.Status.invisible,
    }
    key = mode.lower()
    if key not in modes:
        await ctx.send(embed=create_error_embed("Invalid Mode", "Valid modes: online, idle, dnd, invis"))
        return

    # A mode change must never take the bot offline. The activity type of the
    # current status may be a type Discord rejects (e.g. a stale/expired
    # streaming URL), which would make change_presence fail and leave the bot
    # offline. Retry without the activity if building it fails.
    canonical = 'invisible' if key == 'invis' else key
    try:
        await bot.change_presence(status=modes[key], activity=_build_bot_activity(BOT_ACTIVITY, BOT_ACTIVITY_NAME))
    except Exception:
        try:
            await bot.change_presence(status=modes[key], activity=None)
        except Exception as e:
            await ctx.send(embed=create_error_embed("Mode Failed", f"Could not change mode: `{e}`"))
            return

    BOT_STATUS = canonical
    set_setting('bot_status', canonical)

    embed = create_success_embed("Mode Changed", f"Bot mode set to {key}")
    await ctx.send(embed=embed)

@bot.command(name='maintenance')
@is_main_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def maintenance_mode(ctx, mode: str):
    """Toggle maintenance mode"""
    global MAINTENANCE_MODE, MAINTENANCE_STARTED_BY, MAINTENANCE_STARTED_AT
    
    mode = mode.lower()
    if mode not in ['on', 'off']:
        await ctx.send(embed=create_error_embed("Invalid Mode", "Please use `on` or `off`."))
        return
    
    if mode == 'on':
        MAINTENANCE_MODE = True
        MAINTENANCE_STARTED_BY = str(ctx.author.id)
        MAINTENANCE_STARTED_AT = datetime.now().isoformat()
        
        set_setting('maintenance_mode', 'true')
        set_setting('maintenance_started_by', str(ctx.author.id))
        set_setting('maintenance_started_at', MAINTENANCE_STARTED_AT)
        
        await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="🔧 Maintenance Mode"))
        
        embed = create_warning_embed("Maintenance Mode Active", "The bot is now in maintenance mode. Only administrators can use commands.")
        add_field(embed, "Started By", ctx.author.mention, True)
        add_field(embed, "Status", "Commands disabled for non-admins", True)
        
    else:
        MAINTENANCE_MODE = False
        MAINTENANCE_STARTED_BY = ''
        MAINTENANCE_STARTED_AT = ''
        
        set_setting('maintenance_mode', 'false')
        set_setting('maintenance_started_by', '')
        set_setting('maintenance_started_at', '')
        
        activity_types = {
            'playing': discord.ActivityType.playing,
            'watching': discord.ActivityType.watching,
            'listening': discord.ActivityType.listening,
        }
        activity_type = activity_types.get(BOT_ACTIVITY, discord.ActivityType.watching)
        status_types = {
            'online': discord.Status.online,
            'idle': discord.Status.idle,
            'dnd': discord.Status.dnd,
        }
        status = status_types.get(BOT_STATUS, discord.Status.online)
        
        await bot.change_presence(status=status, activity=discord.Activity(type=activity_type, name=BOT_ACTIVITY_NAME))
        
        embed = create_success_embed("Maintenance Mode Deactivated", "All commands are now available.")
    
    await ctx.send(embed=embed)
    
    if mode == 'on':
        await send_log(EMOJI_SYSTEM, "Maintenance Mode Enabled", f"Toggled by: {ctx.author.mention}", color=0xffaa00)
    else:
        await send_log(EMOJI_SYSTEM, "Maintenance Mode Disabled", f"Toggled by: {ctx.author.mention}", color=0x00ff88)

# ==================================================== SYSTEM COMMANDS END =====================================================

# ==================================================== PORT FORWARDING COMMANDS =====================================================

# Note: port-slot allocation commands ($ports-add-user / $ports-remove-user) were
# removed. Per-VPS port forwarding is now toggled with the <y/n> argument of $create.

# ==================================================== PORT FORWARDING COMMANDS END =====================================================

# ==================================================== MACHINE STATUS COMMAND =====================================================

async def _gather_machine_info():
    info = {}
    cmd = r"""
echo "os=$(cat /etc/os-release 2>/dev/null | grep '^PRETTY_NAME' | cut -d= -f2 | tr -d '\"' 2>/dev/null || echo 'Unknown')"
echo "kernel=$(uname -r 2>/dev/null || echo 'Unknown')"
echo "hostname=$(hostname 2>/dev/null || echo 'Unknown')"
echo "arch=$(uname -m 2>/dev/null || echo 'Unknown')"
echo "cpu_model=$(cat /proc/cpuinfo 2>/dev/null | grep 'model name' | head -1 | cut -d: -f2 | sed 's/^ *//' || echo 'Unknown')"
echo "cpu_cores=$(nproc 2>/dev/null || echo '0')"
echo "cpu_usage=$(LANG=C top -bn1 -d0.05 2>/dev/null | grep '%Cpu' | awk '{print $2+$4+$6}' || echo '0')"
echo "load_avg=$(cat /proc/loadavg 2>/dev/null | awk '{print $1, $2, $3}' || echo '0 0 0')"
echo "mem_total=$(free -h 2>/dev/null | grep Mem | awk '{print $2}' || echo '0')"
echo "mem_used=$(free -h 2>/dev/null | grep Mem | awk '{print $3}' || echo '0')"
echo "mem_avail=$(free -h 2>/dev/null | grep Mem | awk '{print $7}' || echo '0')"
echo "mem_pct=$(free 2>/dev/null | grep Mem | awk '{printf \"%.1f\", $3/$2*100}' || echo '0')"
echo "disk_total=$(df -h / 2>/dev/null | tail -1 | awk '{print $2}' || echo '0')"
echo "disk_used=$(df -h / 2>/dev/null | tail -1 | awk '{print $3}' || echo '0')"
echo "disk_avail=$(df -h / 2>/dev/null | tail -1 | awk '{print $4}' || echo '0')"
echo "disk_pct=$(df -h / 2>/dev/null | tail -1 | awk '{print $5}' || echo '0%')"
echo "uptime=$(uptime -p 2>/dev/null | sed 's/up //' || echo 'Unknown')"
echo "public_ip=$(curl -s --connect-timeout 3 ifconfig.me 2>/dev/null || hostname -I 2>/dev/null | awk '{print $1}' || echo 'Unknown')"
"""
    try:
        proc = await asyncio.create_subprocess_exec(
            "bash", "-c", cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=30)
        for line in stdout.decode().splitlines():
            if '=' in line:
                key, _, val = line.partition('=')
                info[key.strip()] = val.strip()
    except:
        pass

    gpu = "No GPU found"

    async def _run_cmd(*args, timeout=10):
        try:
            p = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            out, _ = await asyncio.wait_for(p.communicate(), timeout=timeout)
            return out.decode().strip() if p.returncode == 0 else ""
        except:
            return ""

    nv_out = await _run_cmd("nvidia-smi", "--query-gpu=gpu_name", "--format=csv,noheader")
    if nv_out:
        gpu = nv_out.split('\n')[0].strip()

    if gpu == "No GPU found":
        glx_out = await _run_cmd("glxinfo")
        if glx_out:
            for line in glx_out.splitlines():
                if 'OpenGL renderer' in line:
                    gpu = line.split(':', 1)[1].strip()
                    break

    if gpu == "No GPU found":
        neo_out = await _run_cmd("neofetch", "--stdout")
        if neo_out:
            for line in neo_out.splitlines():
                if line.lower().startswith('gpu'):
                    gpu_val = line.split(':', 1)[1].strip()
                    if gpu_val and 'vendor' not in gpu_val.lower() and 'device' not in gpu_val.lower():
                        gpu = gpu_val
                    break

    if gpu == "No GPU found":
        lspci_out = await _run_cmd("lspci", "-vnn")
        if lspci_out:
            for line in lspci_out.splitlines():
                low = line.lower()
                if any(x in low for x in ['vga', '3d', 'display']):
                    slot = line.split()[0]
                    driver = ""
                    sub = ""
                    detail = await _run_cmd("lspci", "-v", "-s", slot)
                    if detail:
                        for dl in detail.splitlines():
                            if 'Kernel driver in use' in dl:
                                driver = dl.split(':', 1)[1].strip()
                            if 'Subsystem' in dl:
                                raw = dl.split(':', 1)[1].strip() if ':' in dl else ""
                                raw = raw.split('[')[0].strip() if '[' in raw else raw
                                raw = re.sub(r'\bDevice\s+\S+\s*$', '', raw).strip()
                                raw = re.sub(r'\bSubsystem\s+\S+\s*$', '', raw).strip()
                                raw = re.sub(r'\([^)]*\)', '', raw).strip()
                                raw = re.sub(r'\s+', ' ', raw).strip()
                                if raw and 'Device' not in raw:
                                    sub = raw
                    parts = []
                    if driver:
                        parts.append(driver)
                    desc = line.split(':', 1)[1].strip() if ':' in line else line.strip()
                    desc_clean = re.sub(r'\[[\w:]+\]|\([^)]*\)', '', desc).strip()
                    desc_clean = re.sub(r'\s+', ' ', desc_clean).strip()
                    parts.append(sub if sub else desc_clean)
                    gpu = " - ".join(parts)
                    break

    if gpu == "No GPU found":
        lshw_out = await _run_cmd("lshw", "-c", "display")
        if lshw_out:
            for line in lshw_out.splitlines():
                if 'product:' in line:
                    gpu = line.split('product:', 1)[1].strip()
                    break

    info['gpu'] = gpu
    return info



# ==================================================== MACHINE STATUS COMMAND END =====================================================

# ==================================================== MULTI-NODE MANAGEMENT =====================================================

class NodeError(Exception):
    """Error talking to a remote SGM node API."""
    pass


class NodeClient:
    """HTTP client for a remote node (node-install.sh host)."""
    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint.rstrip('/')
        if not self.endpoint.startswith(('http://', 'https://')):
            self.endpoint = 'http://' + self.endpoint
        self.api_key = api_key

    async def _request(self, method, path, timeout=120, **kwargs):
        headers = {'X-API-Key': self.api_key}
        url = f"{self.endpoint}{path}"
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.request(method, url, headers=headers, **kwargs) as resp:
                    text = await resp.text()
                    if resp.status == 401:
                        raise NodeError("Invalid API key")
                    if resp.status >= 400:
                        try:
                            detail = json.loads(text).get('detail', text)
                        except Exception:
                            detail = text
                        raise NodeError(f"HTTP {resp.status}: {detail}")
                    try:
                        return json.loads(text)
                    except Exception:
                        return {'raw': text}
        except NodeError:
            raise
        except Exception as e:
            msg = str(e)
            if 'timeout' in msg.lower() or 'timed out' in msg.lower():
                raise NodeError(f"Node API unreachable (timeout): {self.endpoint}")
            raise NodeError(f"Node API unreachable: {msg}")

    async def health(self):
        return await self._request("GET", "/health")

    async def info(self):
        return await self._request("GET", "/info-vps")

    async def check_resources(self):
        return await self._request("GET", "/check-resources-data")

    async def list_containers(self):
        return await self._request("GET", "/list-containers")

    async def disks(self):
        return await self._request("GET", "/disks", timeout=10)

    async def images(self):
        return await self._request("GET", "/images")

    async def create(self, name, image, ram, cpu, disk, ingress=None, egress=None):
        body = {"name": name, "image": image, "ram": ram, "cpu": cpu, "disk": disk}
        if ingress:
            body["ingress"] = ingress
        if egress:
            body["egress"] = egress
        return await self._request("POST", "/create-container", json=body)

    async def set_bandwidth(self, name, ingress=None, egress=None):
        body = {"name": name}
        if ingress is not None:
            body["ingress"] = ingress
        if egress is not None:
            body["egress"] = egress
        return await self._request("POST", "/set-bandwidth", json=body)

    async def start(self, name):
        return await self._request("POST", "/start-container", json={"name": name})

    async def stop(self, name):
        return await self._request("POST", "/stop-container", json={"name": name})

    async def restart(self, name):
        return await self._request("POST", "/restart-container", json={"name": name})

    async def delete(self, name):
        return await self._request("POST", "/delete-container", json={"name": name})

    async def reinstall(self, name, image):
        return await self._request("POST", "/reinstall-container", json={"name": name, "image": image})

    async def resize(self, name, ram=None, cpu=None, disk=None):
        body = {"name": name}
        if ram is not None:
            body["ram"] = ram
        if cpu is not None:
            body["cpu"] = cpu
        if disk is not None:
            body["disk"] = disk
        return await self._request("POST", "/resize-container", json=body)

    async def container_info(self, name):
        return await self._request("GET", f"/container-info?name={name}")

    async def container_stats(self, name):
        return await self._request("GET", f"/container-stats?name={name}")

    async def container_logs(self, name, lines=50):
        return await self._request("GET", f"/container-logs?name={name}&lines={int(lines)}")

    async def exec(self, name, command, timeout=60):
        return await self._request("POST", "/container-exec",
                                   json={"name": name, "command": command, "timeout": timeout})

    async def freeze(self, name):
        return await self._request("POST", "/freeze-container", json={"name": name})

    async def unfreeze(self, name):
        return await self._request("POST", "/unfreeze-container", json={"name": name})

    async def fix_network(self):
        return await self._request("POST", "/fix-network")

    async def console(self, name, kind="sshx"):
        return await self._request("POST", "/console", json={"name": name, "kind": kind})

    async def ipv4_tunnel(self, name, action="start"):
        return await self._request("POST", "/ipv4-tunnel", json={"name": name, "action": action})

    async def file_manager(self, name, action="start", username="admin", password="admin"):
        return await self._request("POST", "/file-manager",
                                   json={"name": name, "action": action,
                                         "username": username, "password": password})

    async def stop_all(self):
        return await self._request("POST", "/stop-all")

    async def start_all(self):
        return await self._request("POST", "/start-all")

    async def port_list(self, container=None):
        path = "/port-forward/list"
        if container:
            path += f"?container={container}"
        return await self._request("GET", path)

    async def port_create(self, container, vps_port):
        return await self._request("POST", "/port-forward/create", json={"container": container, "vps_port": vps_port})

    async def port_remove(self, container, host_port):
        return await self._request("POST", "/port-forward/remove", json={"container": container, "host_port": host_port})


def node_client(node: dict) -> NodeClient:
    return NodeClient(node["endpoint"], node["api_key"])


def free_vps_node():
    """Return a pseudo-node dict for the configured FREE_VPS_NODE, or None if unconfigured."""
    try:
        endpoint, key = FREE_VPS_NODE
    except Exception:
        return None
    endpoint = (endpoint or "").strip()
    key = (key or "").strip()
    if not endpoint or not key:
        return None
    return {"node_id": "__free__", "endpoint": endpoint, "api_key": key}


def node_get(node_id: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM nodes WHERE node_id=?', (node_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def node_public_ip(node):
    """Public IPv4 of the node from its last health snapshot, or '' if unset/placeholder."""
    if not node:
        return ''
    try:
        snap = json.loads(node.get('last_snapshot') or '{}')
    except (ValueError, TypeError):
        return ''
    ip = (snap.get('public_ip') or '').strip()
    if not re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", ip):
        return ''
    return ip


def node_location(node):
    """Location string (country, region) of the node from its last health snapshot, or ''."""
    if not node:
        return ''
    try:
        snap = json.loads(node.get('last_snapshot') or '{}')
    except (ValueError, TypeError):
        return ''
    loc = snap.get('location')
    if isinstance(loc, dict):
        return (loc.get('display') or '').strip()
    return str(loc or '').strip()


def node_all():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM nodes ORDER BY added_at')
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def node_upsert(node_id, endpoint, api_key, node_name, added_by, snapshot=''):
    now = datetime.utcnow().isoformat()
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''INSERT INTO nodes (node_id, endpoint, api_key, node_name, added_by, online, last_snapshot, last_seen, added_at)
                   VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?)
                   ON CONFLICT(node_id) DO UPDATE SET endpoint=excluded.endpoint, api_key=excluded.api_key,
                   node_name=excluded.node_name, online=1, last_snapshot=excluded.last_snapshot, last_seen=excluded.last_seen''',
                (node_id, endpoint, api_key, node_name, str(added_by), json.dumps(snapshot), now, now))
    conn.commit()
    conn.close()


def node_set_status(node_id, online, snapshot=None):
    now = datetime.utcnow().isoformat()
    conn = get_db()
    cur = conn.cursor()
    if snapshot is not None:
        cur.execute('UPDATE nodes SET online=?, last_snapshot=?, last_seen=? WHERE node_id=?',
                    (1 if online else 0, json.dumps(snapshot), now, node_id))
    else:
        cur.execute('UPDATE nodes SET online=?, last_seen=? WHERE node_id=?', (1 if online else 0, now, node_id))
    conn.commit()
    conn.close()


def node_display_name(node):
    """Friendly node name (falls back to the node id)."""
    if not node:
        return ''
    return (node.get('node_name') or '').strip() or (node.get('node_id') or '')


def node_name_of(node_id):
    """Friendly name for a stored node_id (falls back to the id itself)."""
    if not node_id:
        return 'unknown'
    node = node_get(node_id)
    return node_display_name(node) if node else str(node_id)


def node_resolve(identifier):
    """Look up a node by its friendly name (case-insensitive)."""
    if not identifier:
        return None
    ident = str(identifier).strip().lower()
    nodes = node_all()
    for n in nodes:
        if (n.get('node_name') or '').strip().lower() == ident:
            return n
    return None



def node_remove(node_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM nodes WHERE node_id=?', (node_id,))
    cur.execute('DELETE FROM node_vps WHERE node_id=?', (node_id,))
    conn.commit()
    conn.close()


def node_vps_get(vps_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM node_vps WHERE vps_id=?', (int(vps_id),))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def node_vps_add(vps_id, user_id, node_id, container_name, ram, cpu, disk, os_image, expires_at, bandwidth='', ports_enabled=1):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''INSERT INTO node_vps (vps_id, user_id, node_id, container_name, ram, cpu, disk, os_image, status, created_at, expires_at, bandwidth, ports_enabled)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'running', ?, ?, ?, ?)''',
                (int(vps_id), str(user_id), node_id, container_name, str(ram), str(cpu), str(disk),
                 os_image, datetime.utcnow().isoformat(), expires_at.isoformat(), bandwidth or '', int(ports_enabled)))
    conn.commit()
    conn.close()


def node_vps_set_status(vps_id, status):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE node_vps SET status=? WHERE vps_id=?', (status, int(vps_id)))
    conn.commit()
    conn.close()


def node_vps_remove(vps_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM node_vps WHERE vps_id=?', (int(vps_id),))
    conn.commit()
    conn.close()


def node_vps_user(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM node_vps WHERE user_id=? ORDER BY vps_id', (str(user_id),))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def node_vps_all():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM node_vps ORDER BY node_id, vps_id')
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def node_vps_by_container(container_name):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM node_vps WHERE container_name=?', (container_name,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def node_vps_update(vps_id, **fields):
    """Update arbitrary node_vps columns for one vps_id."""
    if not fields:
        return
    cols = ", ".join(f"{k}=?" for k in fields)
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f'UPDATE node_vps SET {cols} WHERE vps_id=?', (*fields.values(), int(vps_id)))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------- BANDWIDTH HELPERS
_BW_UNITS = {'bps': 1, 'kbps': 1000, 'mbps': 1000 ** 2, 'gbps': 1000 ** 3, 'tbps': 1000 ** 4}


def parse_bw_value(tok):
    """Parse a single bandwidth token -> bits per second (int).

    The letter before "ps" decides bits vs bytes:
      small b (Mbps, mbps, gbps, kbps) -> BITS
      capital B (MBps, GBps, kBps)     -> BYTES (8x the same-size bits value)

    Returns None if the token is invalid."""
    if tok is None:
        return None
    s = str(tok).strip().replace(' ', '')
    if not s:
        return None
    m = re.fullmatch(r'(\d+(?:\.\d+)?)([A-Za-z]+)?', s)
    if not m:
        return None
    num = float(m.group(1))
    unit = m.group(2) or 'bps'
    lunit = unit.lower()
    if lunit not in _BW_UNITS:
        return None
    mult = _BW_UNITS[lunit]
    if lunit.endswith('bps') and unit.endswith('Bps'):
        mult = mult * 8  # capital B = bytes, bytes are 8x bits
    return int(round(num * mult))


def parse_bandwidth(spec):
    """Parse an 'up/down' spec (e.g. '1kbps/900kbps' or '10MBps/5mbps') -> (up_bps, down_bps).

    Raises ValueError with a friendly message when invalid."""
    if spec is None:
        return None
    parts = str(spec).strip().split('/')
    if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
        raise ValueError("Bandwidth must be in the format `<up>/<down>`, e.g. `1kbps/900kbps`.")
    up = parse_bw_value(parts[0])
    down = parse_bw_value(parts[1])
    if up is None or down is None:
        raise ValueError("Invalid bandwidth value. Units (small b = bits): `bps`, `kbps`, `mbps`, `gbps`, `tbps` | Units (capital B = bytes): `kBps`, `MBps`, `GBps`, `TBps`.")
    return up, down


def bw_lxd(bits):
    """Convert bits/s to an LXD limit string (e.g. 900000 -> '900000bit')."""
    return f"{int(bits)}bit"


def bw_human(bits):
    """Convert bits/s to a compact human string, keeping the largest whole unit."""
    try:
        b = float(bits)
    except (TypeError, ValueError):
        return "Unlimited"
    if b <= 0:
        return "Unlimited"
    for unit, div in (('tbps', 1000 ** 4), ('gbps', 1000 ** 3), ('mbps', 1000 ** 2), ('kbps', 1000), ('bps', 1)):
        if b >= div:
            val = b / div
            return f"{val:g}{unit}"
    return f"{b:g}bps"


def lxd_bw_to_human(s):
    """Convert an LXD limit string ('900000bit', '5mbit', ...) to a human string."""
    if not s:
        return None
    m = re.fullmatch(r'(\d+(?:\.\d+)?)\s*(tbit|gbit|mbit|kbit|bit|tb|gb|mb|kb|b)?', str(s).strip().lower())
    if not m:
        return str(s)
    num = float(m.group(1))
    unit = (m.group(2) or 'bit').lower()
    mult = {'bit': 1, 'kbit': 1000, 'mbit': 1000 ** 2, 'gbit': 1000 ** 3, 'tbit': 1000 ** 4,
            'b': 1, 'kb': 1000, 'mb': 1000 ** 2, 'gb': 1000 ** 3, 'tb': 1000 ** 4}
    return bw_human(int(round(num * mult.get(unit, 1))))


def bandwidth_display(spec):
    """Turn a stored 'u/d' spec into a friendly 'up X / down Y' string (units preserved)."""
    if not spec:
        return None
    parts = str(spec).split('/')
    if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
        return None
    return f"up {parts[0].strip()} / down {parts[1].strip()}"


def node_vps_shared_list(row):
    try:
        return json.loads(row.get('shared_with') or '[]')
    except Exception:
        return []


def node_vps_as_vpsinfo(row):
    """Adapt a node_vps row to the legacy vps_info dict shape (for shared UI code)."""
    try:
        shared = json.loads(row.get('shared_with') or '[]')
    except Exception:
        shared = []
    try:
        hist = json.loads(row.get('suspension_history') or '[]')
    except Exception:
        hist = []
    return {
        'id': row['vps_id'],
        'vps_id': row['vps_id'],
        'user_id': row['user_id'],
        'node_id': row['node_id'],
        'container_name': row['container_name'],
        'plan_name': row.get('plan_name') or 'Custom',
        'ram': f"{row['ram']}GB" if str(row.get('ram', '')).replace('.', '').isdigit() else str(row.get('ram', '')),
        'cpu': str(row.get('cpu', '')),
        'storage': f"{row['disk']}GB" if str(row.get('disk', '')).replace('.', '').isdigit() else str(row.get('disk', '')),
        'config': f"{row.get('ram')}GB RAM / {row.get('cpu')} CPU / {row.get('disk')}GB Disk",
        'os_version': row.get('os_image', 'ubuntu:22.04'),
        'status': row.get('status', 'running'),
        'suspended': row.get('status') == 'suspended',
        'whitelisted': bool(row.get('whitelisted', 0)),
        'purge_protected': bool(row.get('purge_protected', 0)),
        'suspended_reason': row.get('suspended_reason', ''),
        'suspension_history': hist,
        'created_at': row.get('created_at', ''),
        'shared_with': shared,
        'expires_at': row.get('expires_at', ''),
        'timer_paused_at': row.get('timer_paused_at', ''),
        'timer_status': row.get('timer_status', ''),
    }


def _new_remote_vps_id():
    conn = get_db()
    cur = conn.cursor()
    while True:
        vps_id = random.randint(1000, 99999)
        cur.execute('SELECT 1 FROM node_vps WHERE vps_id=?', (vps_id,))
        if not cur.fetchone():
            conn.close()
            return vps_id


async def resolve_remote_vps(ctx, vps_id, node_id=None, allow_admin=True):
    """Resolve a remote VPS by its globally-unique vps-id.
    If node_id is given, it must match the VPS's node. Returns (vps_row, node_row)."""
    vps = node_vps_get(vps_id)
    if not vps:
        await ctx.send(embed=create_error_embed("Not Found", f"No VPS with id `{vps_id}`."))
        return None, None
    # Ownership check: only owner or admin can access/control
    is_admin = user_is_admin(ctx.author)
    owner_id = str(vps.get('user_id'))
    if owner_id != str(ctx.author.id) and not is_admin:
        await ctx.send(embed=create_error_embed("Access Denied", "This is not your VPS!"))
        return None, None
    if node_id:
        _target = node_resolve(node_id)
        if _target and _target['node_id'] != vps['node_id']:
            await ctx.send(embed=create_error_embed("Wrong Node",
                   f"VPS `{vps_id}` is on node `{node_name_of(vps['node_id'])}`, not `{node_display_name(_target)}`."))
            return None, None
    node = node_get(vps['node_id'])
    if not node:
        await ctx.send(embed=create_error_embed("Node Missing",
               f"VPS `{vps_id}` references node `{node_name_of(vps['node_id'])}` which is not connected."))
        return None, None
    return vps, node


async def node_refresh_loop():
    """Background task: poll every connected node's status."""
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            for n in node_all():
                try:
                    info = await node_client(n).info()
                    node_set_status(n['node_id'], True, info)
                except Exception:
                    node_set_status(n['node_id'], False)
        except Exception as e:
            logger.error(f"node_refresh_loop error: {e}")
        await asyncio.sleep(60)


@bot.command(name='connect-vps')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def connect_vps(ctx, endpoint: str = None, api_key: str = None, *, name: str = None):
    """Connect a remote node: connect-vps <ip:port|domain> <api-key> [name]"""
    if not endpoint or not api_key:
        await ctx.send(embed=create_error_embed("Missing Argument",
            f"Usage: `{PREFIX}connect-vps <ip:port|domain> <api-key> [name]`\n"
            f"`[name]` sets a friendly node name (defaults to the node's own hostname)."))
        return

    custom_name = (name or '').strip() or None
    msg = await ctx.send(embed=create_info_embed("Connecting…", f"Talking to `{endpoint}`…"))
    client = NodeClient(endpoint, api_key)
    try:
        info = await client.info()
    except NodeError as e:
        await msg.edit(embed=create_error_embed("Connection Failed", f"`{endpoint}`\n```{e}```"))
        return

    node_id = info.get("node_id") or f"node-{random.randint(1000, 9999)}"
    existing = node_get(node_id)

    # Duplicate-name guard: another node (different id) already uses this name.
    if custom_name:
        clash = next((n for n in node_all()
                      if n['node_id'] != node_id and (n.get('node_name') or '') == custom_name), None)
        if clash:
            await msg.edit(embed=create_error_embed("Duplicate Node Name",
                f"A node with the name `{custom_name}` already exists (`{clash['endpoint']}`).\n"
                f"Choose a different name."))
            return

    node_name = custom_name or info.get("node_name") or info.get("hostname") or node_id
    node_upsert(node_id, client.endpoint, api_key, node_name, ctx.author.id, info)

    title = "Node Reconnected" if existing else "Node Connected"
    desc = f"`{node_name}` is now online."
    if existing and custom_name and (existing.get('node_name') or '') != custom_name:
        desc += f"\nName updated: `{existing.get('node_name')}` → `{custom_name}`"
    embed = create_success_embed(title, desc)
    add_field(embed, "Name", f"`{node_name}`", True)
    add_field(embed, "Endpoint", f"`{client.endpoint}`", True)
    add_field(embed, "Public IP", f"`{info.get('public_ip') or 'unknown'}`", True)
    add_field(embed, f"{EMOJI_CPU} CPU", f"`{info.get('cpu', {}).get('total', '?')} cores`", True)
    add_field(embed, f"{EMOJI_RAM} RAM", f"`{info.get('ram', {}).get('total_gb', '?')} GB`", True)
    add_field(embed, f"{EMOJI_DISK} Disk", f"`{info.get('disk', {}).get('host_total_gb', '?')} GB`", True)
    await msg.edit(embed=embed)


@bot.command(name='node-list')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def node_list(ctx, flag: str = None):
    """List all connected nodes: node-list [--hide]"""
    if not await maintenance_check(ctx):
        return
    hide = (flag or '').strip().lower() == '--hide'
    nodes = node_all()
    if not nodes:
        await ctx.send(embed=create_warning_embed("No Nodes", f"No nodes connected yet. Use `{PREFIX}connect-vps`."))
        return

    fields = []
    for n in nodes:
        snap = json.loads(n['last_snapshot']) if n.get('last_snapshot') else {}
        online = bool(n.get('online'))
        try:
            client = node_client(n)
            await asyncio.wait_for(client.health(), timeout=5)
            node_set_status(n['node_id'], True, None)
            online = True
        except Exception:
            node_set_status(n['node_id'], False)
            online = False
        status_icon = EMOJI_ONLINE if online else EMOJI_OFFLINE
        role = "Online" if online else "Offline"
        cpu = snap.get('cpu', {}).get('total', '?')
        ram = snap.get('ram', {}).get('total_gb', '?')
        disk = snap.get('disk', {}).get('host_total_gb', '?')
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM node_vps WHERE node_id=?', (n['node_id'],))
        vps_count = cur.fetchone()[0]
        conn.close()
        fields.append((f"{status_icon} {node_display_name(n)}",
                       f"**{role}** • `{('*' * len(n['endpoint'])) if hide else n['endpoint']}`\n"
                       f"{EMOJI_CPU} `{cpu}` cores  {EMOJI_RAM} `{ram}` GB  {EMOJI_DISK} `{disk}` GB\n"
                       f"{EMOJI_VPS} `{vps_count}` VPS"))

    per_page = 8
    chunks = [fields[i:i + per_page] for i in range(0, len(fields), per_page)]
    total_pages = len(chunks)
    for page, chunk in enumerate(chunks, 1):
        title = f"Connected Nodes — {len(nodes)} node(s)"
        desc = f"Page {page}/{total_pages}" if total_pages > 1 else f"{EMOJI_GLOBAL} All nodes online capacity overview"
        embed = create_info_embed(title, desc)
        for f_title, f_val in chunk:
            add_field(embed, f_title, f_val, False)
        await ctx.send(embed=embed)


@bot.command(name='node-creds')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def node_creds(ctx):
    """Show credentials (endpoint + API key) for every connected node."""
    if not await maintenance_check(ctx):
        return
    nodes = node_all()
    if not nodes:
        await ctx.send(embed=create_warning_embed("No Nodes", f"No nodes connected yet. Use `{PREFIX}connect-vps`."))
        return

    entries = []
    for n in nodes:
        icon = EMOJI_ONLINE if n.get('online') else EMOJI_OFFLINE
        name = n.get('node_name') or 'Unnamed'
        entries.append(
            f"{icon} **{name}**\n"
            f"🌐 Endpoint: `{n['endpoint']}`\n"
            f"🔑 API Key: ||`{n['api_key']}`||"
        )

    # Split into embeds under Discord's 4096-char description limit.
    pages, current, size = [], [], 0
    for entry in entries:
        if size + len(entry) + 2 > 3900 and current:
            pages.append(current)
            current, size = [], 0
        current.append(entry)
        size += len(entry) + 2
    if current:
        pages.append(current)

    for page, chunk in enumerate(pages, 1):
        title = f"Node Credentials — {len(nodes)} node(s)"
        desc = f"Page {page}/{len(pages)}\n\n" if len(pages) > 1 else ""
        embed = create_info_embed(title, desc + "\n\n".join(chunk))
        embed.set_footer(text="API keys are spoiler-hidden — click to reveal.")
        await ctx.send(embed=embed)


@bot.command(name='node-info')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def node_info(ctx, node_id: str = None):
    """Full details for one node: node-info <node-name>"""
    if not await maintenance_check(ctx):
        return
    if not node_id:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}node-info <node-name>`"))
        return
    node = node_resolve(node_id)
    if not node:
        await ctx.send(embed=create_error_embed("Not Found", f"No node with name `{node_id}`."))
        return
    node_id = node['node_id']
    node_label = node_display_name(node)

    client = node_client(node)
    try:
        info = await client.info()
        node_set_status(node_id, True, info)
    except NodeError as e:
        node_set_status(node_id, False)
        embed = create_error_embed(f"Node {node_label}", f"{EMOJI_BAD_SIGNAL} **Offline**\n```{e}```")
        if node.get('last_seen'):
            add_field(embed, "Last Seen", f"<t:{int(datetime.fromisoformat(node['last_seen']).timestamp())}:R>")
        await ctx.send(embed=embed)
        return

    total_cpu = info.get('cpu', {}).get('total', '?')
    total_ram = info.get('ram', {}).get('total_gb', '?')
    host_disk = info.get('disk', {}).get('host_total_gb', '?')
    pool = info.get('storage_pool', {})

    alloc_cpu = alloc_ram = alloc_disk = 0.0
    try:
        res = await client.check_resources()
        alloc_cpu = res.get('cpu', {}).get('allocated', 0)
        alloc_ram = res.get('ram', {}).get('allocated_gb', 0)
        alloc_disk = res.get('disk', {}).get('allocated_gb', 0)
    except NodeError:
        pass

    embed = create_info_embed(f"Node {node_label}", f"{EMOJI_GOOD_SIGNAL} **Online** — `{node_label}`")
    add_field(embed, f"{EMOJI_SYSTEM} System",
              f"{EMOJI_CPU} CPU: `{total_cpu}` cores\n"
              f"{EMOJI_RAM} RAM: `{total_ram}` GB\n"
              f"{EMOJI_DISK} Disk: `{host_disk}` GB", True)
    add_field(embed, "OS / Kernel",
              f"{info.get('os', '?')}\n`{info.get('kernel', '')}`\nLXD `{info.get('lxd_version', '?')}`", True)
    loc = info.get('location') or {}
    loc_parts = [str(p).strip() for p in (loc.get('country'), loc.get('region'), loc.get('city')) if p]
    loc_text = loc.get('display') or (", ".join(loc_parts) if loc_parts else 'Unknown')
    add_field(embed, "Location",
              f"{EMOJI_GLOBAL} `{loc_text}`", True)
    pool_total = pool.get('total_gb', 0) or host_disk
    add_field(embed, f"{EMOJI_VPS} Allocation",
              f"{EMOJI_CPU} `{alloc_cpu}` / `{total_cpu}` CPU\n"
              f"{EMOJI_RAM} `{alloc_ram}` / `{total_ram}` GB\n"
              f"{EMOJI_DISK} `{alloc_disk}` / `{pool_total}` GB\n"
              f"Pool: `{pool.get('name', '?')}` (enforced: `{pool.get('enforced', False)}`)", True)
    add_field(embed, f"{EMOJI_VPS} Containers",
              f"Total `{info.get('containers', {}).get('total', '?')}` • "
              f"Running `{info.get('containers', {}).get('running', '?')}`", True)
    add_field(embed, f"{EMOJI_UPTIME} Uptime", f"`{info.get('uptime', 'unknown')}`", True)
    if node.get('added_at'):
        try:
            add_field(embed, f"{EMOJI_STATUS} Connected",
                      f"<t:{int(datetime.fromisoformat(node['added_at']).timestamp())}:R>", True)
        except Exception:
            pass
    if node.get('last_seen'):
        try:
            add_field(embed, f"{EMOJI_ONLINE} Last Seen",
                      f"<t:{int(datetime.fromisoformat(node['last_seen']).timestamp())}:R>", True)
        except Exception:
            pass
    await ctx.send(embed=embed)


@bot.command(name='remove-node')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def remove_node(ctx, node_id: str = None):
    """Disconnect a node: remove-node <node-name>"""
    if not node_id:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}remove-node <node-name>`"))
        return
    node = node_resolve(node_id)
    if not node:
        await ctx.send(embed=create_error_embed("Not Found", f"No node with name `{node_id}`."))
        return
    node_id = node['node_id']
    node_remove(node_id)
    await ctx.send(embed=create_success_embed("Node Removed",
        f"`{node_display_name(node)}` disconnected. Its remote VPS entries were cleared from the bot."))


@bot.command(name='node-health')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def node_health(ctx, node_id: str = None):
    """Check one node's health: node-health <node-name>"""
    if not await maintenance_check(ctx):
        return
    if not node_id:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}node-health <node-name>`"))
        return
    n = node_resolve(node_id)
    if not n:
        await ctx.send(embed=create_error_embed("Not Found", f"No node with name `{node_id}`."))
        return
    node_id = n['node_id']
    node_label = node_display_name(n)
    try:
        info = await node_client(n).info()
        node_set_status(node_id, True, info)
        embed = create_success_embed("Node Online", f"{EMOJI_ONLINE} `{node_label}` is **online**")
        add_field(embed, f"{EMOJI_VPS} Containers",
                  f"`{info.get('containers', {}).get('running', '?')}` running", True)
        add_field(embed, f"{EMOJI_UPTIME} Uptime", f"`{info.get('uptime', 'unknown')}`", True)
    except NodeError:
        node_set_status(node_id, False)
        embed = create_error_embed("Node Offline", f"{EMOJI_OFFLINE} `{node_label}` is **offline**")
    await ctx.send(embed=embed)



















@bot.command(name='restart-node')
@is_admin()
@commands.cooldown(1, 10, commands.BucketType.user)
async def restart_node_cmd(ctx, node_id: str = None):
    """Restart a node: restart-node <node-name>"""
    if not await maintenance_check(ctx):
        return
    if not node_id:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}restart-node <node-name>`"))
        return
    n = node_resolve(node_id)
    if not n:
        await ctx.send(embed=create_error_embed("Not Found", f"No node with name `{node_id}`."))
        return
    node_id = n['node_id']
    node_label = node_display_name(n)
    embed = create_warning_embed("Confirm Node Restart", f"You are about to reboot `{node_label}`. This will cause temporary downtime.")
    view = RestartNodeConfirmView(ctx, node_id, node_label)
    view.message = await ctx.send(embed=embed, view=view)


class RestartNodeConfirmView(discord.ui.View):
    def __init__(self, ctx, node_id, node_label):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.node_id = node_id
        self.node_label = node_label
        self.message = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the requester can confirm."), ephemeral=True)
            return
        await interaction.response.defer()
        n = node_resolve(self.node_id)
        if not n:
            await interaction.edit_original_response(embed=create_error_embed("Not Found", f"No node with id `{self.node_id}`."), view=None)
            return
        try:
            embed = create_info_embed("Restarting Node Service", f"{EMOJI_LOADING} Sending reboot request to `{self.node_label}`...")
            await interaction.edit_original_response(embed=embed, view=None)
            res = await node_client(n)._request("POST", "/reboot-node")
            msg = res.get("message", "Reboot request received.")
            embed = create_success_embed("Restart Node", f"`{self.node_label}`: {msg}")
            await interaction.edit_original_response(embed=embed, view=None)
        except Exception as e:
            await interaction.edit_original_response(embed=create_error_embed("Failed", f"```{str(e)}```"), view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the requester can cancel."), ephemeral=True)
            return
        await interaction.response.defer()
        await interaction.edit_original_response(embed=create_info_embed("Cancelled", "Node restart cancelled."), view=None)





async def _remote_vps_op(ctx, op, vps_id, arg=None):
    """Shared handler for every remote VPS operation. VPS is identified by its unique vps-id."""
    vps, node = await resolve_remote_vps(ctx, vps_id)
    if not vps:
        return
    client = node_client(node)
    name = vps['container_name']
    node_id = vps['node_id']
    node_label = node_display_name(node)
    loading = getattr(ctx, '_sgm_loading', None)
    try:
        if op == 'start':
            info = await client.container_info(name)
            if (info.get('status') or '').lower() == 'running':
                await ctx.send(embed=create_warning_embed("Already Running", f"`{name}` on `{node_label}` is already running."))
                return
            await client.start(name)
            node_vps_set_status(vps_id, 'running')
            await ctx.send(embed=create_success_embed("VPS Started", f"`{name}` on `{node_label}` is now running."))
        elif op == 'stop':
            info = await client.container_info(name)
            if (info.get('status') or '').lower() != 'running':
                await ctx.send(embed=create_warning_embed("Already Stopped", f"`{name}` on `{node_label}` is already stopped."))
                return
            await client.stop(name)
            node_vps_set_status(vps_id, 'stopped')
            await ctx.send(embed=create_success_embed("VPS Stopped", f"`{name}` on `{node_label}` is now stopped."))
        elif op == 'restart':
            info = await client.container_info(name)
            if (info.get('status') or '').lower() != 'running':
                await ctx.send(embed=create_warning_embed("VPS Not Running", f"`{name}` on `{node_label}` is not running. Start it first."))
                return
            await client.restart(name)
            node_vps_set_status(vps_id, 'running')
            await ctx.send(embed=create_success_embed("VPS Restarted", f"`{name}` on `{node_label}` has been restarted."))
        elif op == 'stats':
            s = await client.container_stats(name)
            embed = create_info_embed("VPS Stats", f"`{name}` on `{node_label}` • ID `{vps_id}`")
            add_field(embed, f"{EMOJI_CPU} CPU", f"`{s.get('cpu', 'N/A')}`", True)
            add_field(embed, f"{EMOJI_RAM} RAM", f"`{s.get('memory', 'N/A')}`", True)
            add_field(embed, f"{EMOJI_DISK} Disk", f"`{s.get('disk', 'N/A')}`", True)
            add_field(embed, f"{EMOJI_UPTIME} Uptime", f"`{s.get('uptime', 'unknown')}`", True)
            add_field(embed, f"{EMOJI_STATUS} Status", f"`{s.get('status', '?')}`", True)
            await ctx.send(embed=embed)
        elif op == 'info':
            info = await client.container_info(name)
            embed = create_info_embed("VPS Info", f"`{name}` on `{node_label}` • ID `{vps_id}`")
            add_field(embed, "Status", f"`{info.get('status', '?')}`", True)
            add_field(embed, "IP", f"`{info.get('ip') or 'no IP'}`", True)
            add_field(embed, f"{EMOJI_CPU} CPU", f"`{info.get('cpu', '?')}`", True)
            add_field(embed, f"{EMOJI_RAM} RAM", f"`{info.get('ram', '?')}GB`", True)
            add_field(embed, f"{EMOJI_DISK} Disk", f"`{info.get('disk', '?')}GB`", True)
            add_field(embed, f"{EMOJI_UPTIME} Uptime", f"`{info.get('uptime', 'unknown')}`", True)
            bw = info.get('bandwidth') or {}
            bw_up = lxd_bw_to_human(bw.get('egress'))
            bw_down = lxd_bw_to_human(bw.get('ingress'))
            if bw_up or bw_down:
                add_field(embed, "Bandwidth",
                          f"up {bw_up or 'Unlimited'} / down {bw_down or 'Unlimited'}", True)
            await ctx.send(embed=embed)
        elif op == 'logs':
            data = await client.container_logs(name, lines=int(arg) if arg else 50)
            logs = data.get('logs') or data.get('output') or data.get('raw') or ''
            await ctx.send(embed=create_info_embed("VPS Logs", f"```\n{truncate_text(str(logs), 1900)}\n```"))
        elif op == 'suspend':
            await client.freeze(name)
            node_vps_set_status(vps_id, 'suspended')
            await ctx.send(embed=create_success_embed("VPS Suspended", f"`{name}` is now frozen."))
        elif op == 'unsuspend':
            await client.unfreeze(name)
            node_vps_set_status(vps_id, 'running')
            await ctx.send(embed=create_success_embed("VPS Resumed", f"`{name}` is running again."))
    except asyncio.TimeoutError:
        try:
            loading = getattr(ctx, '_sgm_loading', None)
            if loading:
                await loading.edit(embed=create_error_embed("Node Offline", f"VPS node API is unreachable or offline."))
                ctx._sgm_loading_used = True
                return
        except Exception:
            pass
        await ctx.send(embed=create_error_embed("Node Offline", "VPS node API is unreachable or offline."))
    except NodeError as e:
        await ctx.send(embed=create_error_embed(f"VPS {op.title()} Failed", f"```{e}```"))


@bot.command(name='start')
@commands.cooldown(1, 3, commands.BucketType.user)
async def remote_start(ctx, vps_id: int = None):
    """Start a VPS: start <vps-id>"""
    if not await maintenance_check(ctx):
        return
    if vps_id is None:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}start <vps-id>`"))
        return
    await _remote_vps_op(ctx, 'start', vps_id)


@bot.command(name='stop')
@commands.cooldown(1, 3, commands.BucketType.user)
async def remote_stop(ctx, vps_id: int = None):
    """Stop a VPS: stop <vps-id>"""
    if not await maintenance_check(ctx):
        return
    if vps_id is None:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}stop <vps-id>`"))
        return
    await _remote_vps_op(ctx, 'stop', vps_id)


@bot.command(name='restart')
@commands.cooldown(1, 3, commands.BucketType.user)
async def remote_restart(ctx, vps_id: int = None):
    """Restart a VPS: restart <vps-id>"""
    if not await maintenance_check(ctx):
        return
    if vps_id is None:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}restart <vps-id>`"))
        return
    await _remote_vps_op(ctx, 'restart', vps_id)


@bot.command(name='delete-vps')
@is_admin()
@commands.cooldown(1, 10, commands.BucketType.user)
async def remote_delete_vps(ctx, vps_id: str = None):
    """Delete a VPS: delete-vps <vps-id>"""
    if vps_id is None:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}delete-vps <vps-id>`"))
        return

    vps = node_vps_get(vps_id) if vps_id.isdigit() else None
    if not vps:
        vps = node_vps_by_container(vps_id)
    if not vps:
        await ctx.send(embed=create_error_embed("Not Found", f"No VPS `{vps_id}`."))
        return

    node = node_get(vps['node_id'])
    if not node:
        await ctx.send(embed=create_error_embed("Node Offline", f"Node `{node_name_of(vps['node_id'])}` is not connected."))
        return

    user = None
    try:
        user = await bot.fetch_user(int(vps['user_id']))
    except Exception:
        user = None
    reason = "No reason provided"
    user_display = user.mention if user else f"`{vps['user_id']}`"
    os_display = get_os_display_name(vps.get('os_image', 'ubuntu:22.04'))

    embed = discord.Embed(title=f"{EMOJI_WARNING} Confirm VPS Deletion",
                          description="Are you sure you want to delete this VPS?", color=0xffaa00)
    if THUMBNAIL_URL:
        embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_footer(text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                     icon_url=THUMBNAIL_URL)
    details = (f"**Owner:** {user_display}\n"
               f"**VPS #{vps['vps_id']}:** `{vps['container_name']}`\n"
               f"**Node:** `{node_name_of(vps['node_id'])}`\n"
               f"**Plan:** {vps.get('plan_name') or 'Custom'}\n"
               f"**Resources:** {vps.get('ram')} RAM | {vps.get('cpu')} CPU | {vps.get('disk')} Storage\n"
               f"**OS:** {get_os_emoji(vps.get('os_image', 'ubuntu:22.04'))} {os_display}\n"
               f"**Status:** {vps.get('status', 'unknown').upper()}\n"
               f"**Reason:** {reason}")
    add_field(embed, "VPS Details", details, False)
    add_field(embed, f"{EMOJI_WARNING} Warning",
              "This action is **permanent** and cannot be undone!\nAll data on this VPS will be lost.", False)

    view = RemoteDeleteVPSView(ctx, vps, node, reason, user)
    msg = await ctx.send(embed=embed, view=view)
    view.message = msg


@bot.command(name='resize')
@is_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def remote_resize(ctx, vps_id: int = None, ram: float = None, cpu: float = None, disk: float = None):
    """Resize a VPS: resize <vps-id> <ram> <cpu> <disk>"""
    if vps_id is None or ram is None or cpu is None or disk is None:
        await ctx.send(embed=create_error_embed("Missing Argument",
            f"Usage: `{PREFIX}resize <vps-id> <ram> <cpu> <disk>`"))
        return
    vps, node = await resolve_remote_vps(ctx, vps_id)
    if not vps:
        return
    client = node_client(node)
    try:
        await client.resize(vps['container_name'], ram=ram, cpu=cpu, disk=disk)
    except NodeError as e:
        await ctx.send(embed=create_error_embed("Resize Failed", f"```{e}```"))
        return
    conn = get_db()
    conn.execute("UPDATE node_vps SET ram=?, cpu=?, disk=? WHERE vps_id=?",
                 (str(ram), str(cpu), str(disk), int(vps_id)))
    conn.commit()
    conn.close()
    await ctx.send(embed=create_success_embed("Resized", f"`{vps['container_name']}` on `{node_name_of(vps['node_id'])}`"))


@bot.command(name='info')
@commands.cooldown(1, 3, commands.BucketType.user)
async def remote_info(ctx, vps_id: int = None):
    """VPS info: info <vps-id>"""
    if not await maintenance_check(ctx):
        return
    if vps_id is None:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}info <vps-id>`"))
        return
    await _remote_vps_op(ctx, 'info', vps_id)


@bot.command(name='change-bw')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def change_bw(ctx, bandwidth: str = None, vps_id: int = None):
    """Change a VPS bandwidth limit: change-bw <up/down> <vps-id>
    e.g. change-bw 1kbps/900kbps 12345"""
    if not await maintenance_check(ctx):
        return
    if not bandwidth or vps_id is None:
        await ctx.send(embed=create_error_embed("Missing Argument",
            f"Usage: `{PREFIX}change-bw <up/down> <vps-id>`\n"
            f"e.g. `{PREFIX}change-bw 1kbps/900kbps 12345`"))
        return
    try:
        up_bps, down_bps = parse_bandwidth(bandwidth)
    except ValueError as e:
        await ctx.send(embed=create_error_embed("Invalid Bandwidth", str(e)))
        return

    vps, node = await resolve_remote_vps(ctx, vps_id, allow_admin=True)
    if not vps:
        return
    client = node_client(node)
    loading = getattr(ctx, '_sgm_loading', None)
    try:
        await client.set_bandwidth(vps['container_name'],
                                  ingress=bw_lxd(down_bps), egress=bw_lxd(up_bps))
        node_vps_update(vps_id, bandwidth=bandwidth)
        embed = create_success_embed("Bandwidth Updated",
            f"`{vps['container_name']}` on `{node_name_of(vps['node_id'])}` (ID `{vps_id}`)")
        add_field(embed, "Bandwidth", f"`{bandwidth}`", True)
        await ctx.send(embed=embed)
    except asyncio.TimeoutError:
        if loading:
            try:
                await loading.edit(embed=create_error_embed("Node Offline", "VPS node API is unreachable or offline."))
                ctx._sgm_loading_used = True
                return
            except Exception:
                pass
        await ctx.send(embed=create_error_embed("Node Offline", "VPS node API is unreachable or offline."))
    except NodeError as e:
        await ctx.send(embed=create_error_embed("Bandwidth Update Failed", f"```{e}```"))


@bot.command(name='bw-info')
@is_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def bw_info(ctx):
    """Explain bandwidth units used by $create and $change-bw."""
    if not await maintenance_check(ctx):
        return
    embed = create_info_embed("Bandwidth Limits", "How to set network bandwidth on a VPS")
    add_field(embed, "Format", "`<up>/<down>` — upload/download, e.g. `1kbps/900kbps`", False)
    add_field(embed, "Bits vs Bytes (IMPORTANT)",
              "The letter **before** `ps` decides it:\n"
              "**small b → bits**: `mbps`, `gbps`, `kbps`, `Mbps` (e.g. `80Mbps` = 80 Mbit/s)\n"
              "**capital B → bytes**: `MBps`, `GBps`, `kBps` (e.g. `80MBps` = 80 MByte/s = 640 Mbit/s)\n"
              "`Mbps` and `MBps` are **NOT** the same — a **byte is 8x bigger than a bit** (1 Byte = 8 bits).", False)
    add_field(embed, "Units (bits)",
              "`bps`  = 1 bit per second\n"
              "`kbps` = 1,000 bps (1 kbit/s)\n"
              "`mbps` = 1,000,000 bps (1 Mbit/s)\n"
              "`gbps` = 1,000,000,000 bps (1 Gbit/s)\n"
              "`tbps` = 1,000,000,000,000 bps (1 Tbit/s)", False)
    add_field(embed, "Units (bytes)",
              "`kBps` = 1,000 bytes/s (8,000 bits)\n"
              "`MBps` = 1,000,000 bytes/s (8 Mbit/s)\n"
              "`GBps` = 1,000,000,000 bytes/s (8 Gbit/s)\n"
              "`TBps` = 1,000,000,000,000 bytes/s (8 Tbit/s)", False)
    add_field(embed, "Examples",
              "`500bps/500bps` — 500 bit/s up and down\n"
              "`1kbps/900kbps` — 1 kbit/s upload, 900 kbit/s download\n"
              "`10Mbps/10Mbps` — 10 Mbit/s up and down (small b = bits)\n"
              "`10MBps/10MBps` — 10 MByte/s up and down = 80 Mbit/s (capital B = bytes)", False)
    add_field(embed, "Usage",
              f"Set at creation: `{PREFIX}create <ram> <cpu> <disk> <time> <up/down> <y/n> @user <node-name>`\n"
              f"Change later (admin): `{PREFIX}change-bw <up/down> <vps-id>`\n\n"
              f"View current limit: `{PREFIX}info <vps-id>` or `{PREFIX}manage`", False)
    await ctx.send(embed=embed)


@bot.command(name='change-pstate')
@is_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def change_pstate(ctx, state: str = None, vps_id: int = None):
    """Enable/disable a VPS's Ports button: change-pstate <y/n> <vps-id>"""
    if not await maintenance_check(ctx):
        return
    if not state or vps_id is None:
        await ctx.send(embed=create_error_embed("Missing Argument",
            f"Usage: `{PREFIX}change-pstate <y/n> <vps-id>`\n"
            f"e.g. `{PREFIX}change-pstate n 35044`"))
        return
    st = state.strip().lower()
    if st in ('y', 'yes', 'on', 'enable', 'enabled', '1', 'true'):
        enabled = 1
    elif st in ('n', 'no', 'off', 'disable', 'disabled', '0', 'false'):
        enabled = 0
    else:
        await ctx.send(embed=create_error_embed("Invalid State",
            "State must be `y` (enable) or `n` (disable)."))
        return
    vps = node_vps_get(vps_id)
    if not vps:
        await ctx.send(embed=create_error_embed("Not Found", f"No VPS with id `{vps_id}`."))
        return
    node_vps_update(vps_id, ports_enabled=enabled)
    embed = create_success_embed("Ports State Updated",
        f"`{vps['container_name']}` on node `{node_name_of(vps['node_id'])}` (ID `{vps_id}`)")
    add_field(embed, "Owner", f"<@{vps['user_id']}>", True)
    add_field(embed, f"{EMOJI_PORTS} Ports", "Enabled" if enabled else "Disabled", True)
    await ctx.send(embed=embed)
    await send_log(EMOJI_PORTS, "Ports State Changed",
        f"VPS: `{vps['container_name']}` (ID `{vps_id}`) | State: {'Enabled' if enabled else 'Disabled'} | Admin: {ctx.author.mention}",
        color=0x00ff88 if enabled else 0xffaa00)
    try:
        dm = create_info_embed("Ports State Changed",
            f"Port forwarding for your VPS `{vps['container_name']}` (ID `{vps_id}`) has been "
            f"{'**enabled**' if enabled else '**disabled**'} by an admin.")
        await (await bot.fetch_user(int(vps['user_id']))).send(embed=dm)
    except Exception:
        pass


@bot.command(name='logs')
@is_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def remote_logs(ctx, vps_id: int = None, lines: int = 50):
    """VPS logs: logs <vps-id> [lines]"""
    if vps_id is None:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}logs <vps-id> [lines]`"))
        return
    await _remote_vps_op(ctx, 'logs', vps_id, arg=lines)


@bot.command(name='suspend-vps')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def remote_suspend(ctx, vps_id: int = None):
    """Suspend (freeze) a VPS: suspend-vps <vps-id>"""
    if vps_id is None:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}suspend-vps <vps-id>`"))
        return
    await _remote_vps_op(ctx, 'suspend', vps_id)


@bot.command(name='unsuspend-vps')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def remote_unsuspend(ctx, vps_id: int = None):
    """Resume (unfreeze) a VPS: unsuspend-vps <vps-id>"""
    if vps_id is None:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}unsuspend-vps <vps-id>`"))
        return
    await _remote_vps_op(ctx, 'unsuspend', vps_id)


@bot.command(name='renew-vps')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def remote_renew(ctx, vps_id: int = None, time_str: str = None):
    """Renew a VPS timer: renew-vps <vps-id> <time> [--force]"""
    if vps_id is None or not time_str:
        await ctx.send(embed=create_error_embed("Missing Argument",
            f"Usage: `{PREFIX}renew-vps <vps-id> <time>` e.g. `1month`"))
        return
    vps = node_vps_get(vps_id)
    if not vps:
        await ctx.send(embed=create_error_embed("Not Found", f"No VPS with id `{vps_id}`."))
        return
    force = '--force' in time_str
    ts = time_str.replace('--force', '').strip()
    delta = parse_time_string(ts)
    if not delta:
        await ctx.send(embed=create_error_embed("Invalid Time", "Time formats: 1s, 1m, 1h, 1d, 1month, 1year"))
        return
    try:
        base = datetime.fromisoformat(vps['expires_at'])
    except Exception:
        base = datetime.utcnow()
    now = datetime.utcnow()
    start_at = now if force or base < now else base
    new_exp = start_at + delta
    conn = get_db()
    conn.execute("UPDATE node_vps SET expires_at=?, timer_status='running', auto_delete_warned=0 WHERE vps_id=?",
                 (new_exp.isoformat(), int(vps_id)))
    conn.commit()
    conn.close()
    await ctx.send(embed=create_success_embed("VPS Renewed",
        f"`{vps['container_name']}` now expires <t:{int(new_exp.timestamp())}:F>"))


@bot.group(name='ports', invoke_without_command=True)
@commands.cooldown(1, 3, commands.BucketType.user)
async def ports_cmd(ctx):
    """Port forwarding help: ports add <vps-id> <vps_port> | ports list [vps-id] | ports remove <host_port>"""
    embed = create_info_embed("Port Forwarding",
        f"`{PREFIX}ports add <vps-id> <vps_port>` — forward a VPS port\n"
        f"`{PREFIX}ports list [vps-id]` — list forwards\n"
        f"`{PREFIX}ports remove <host_port>` — remove a forward")
    await ctx.send(embed=embed)


@ports_cmd.command(name='add')
@commands.cooldown(1, 5, commands.BucketType.user)
async def ports_add(ctx, vps_id: int = None, vps_port: int = None):
    """Add a port forward: ports add <vps-id> <vps_port>"""
    if vps_id is None or vps_port is None:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}ports add <vps-id> <vps_port>`"))
        return
    vps, node = await resolve_remote_vps(ctx, vps_id)
    if not vps:
        return
    try:
        res = await node_client(node).port_create(vps['container_name'], vps_port)
    except NodeError as e:
        await ctx.send(embed=create_error_embed("Port Forward Failed", f"```{e}```"))
        return
    hp = res.get('host_port')
    conn = get_db()
    conn.execute('INSERT INTO port_forwards (user_id, vps_container, vps_port, host_port, created_at) VALUES (?, ?, ?, ?, ?)',
                 (str(ctx.author.id), vps['container_name'], vps_port, hp, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    embed = create_success_embed("Port Forwarded",
        f"`{res.get('public_ip', node['endpoint'])}:{hp}` → `{vps['container_name']}:{vps_port}`")
    add_field(embed, "Host Port", f"`{hp}`", True)
    add_field(embed, f"{EMOJI_VPS} VPS ID", f"`{vps_id}`", True)
    await ctx.send(embed=embed)


@ports_cmd.command(name='list')
@commands.cooldown(1, 3, commands.BucketType.user)
async def ports_list(ctx, vps_id: int = None):
    """List port forwards: ports list [vps-id]"""
    container = None
    node = None
    if vps_id is not None:
        vps, node = await resolve_remote_vps(ctx, vps_id)
        if not vps:
            return
        container = vps['container_name']
    conn = get_db()
    cur = conn.cursor()
    if container:
        cur.execute('SELECT * FROM port_forwards WHERE vps_container=?', (container,))
    else:
        cur.execute('SELECT * FROM port_forwards WHERE user_id=?', (str(ctx.author.id),))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    if not rows:
        await ctx.send(embed=create_warning_embed("No Forwards", "No port forwards found."))
        return
    lines = "\n".join(f"• `{r['host_port']}` → `{r['vps_container']}:{r['vps_port']}`" for r in rows)
    await ctx.send(embed=create_info_embed("Port Forwards", lines))


@ports_cmd.command(name='remove')
@commands.cooldown(1, 3, commands.BucketType.user)
async def ports_remove(ctx, host_port: int = None):
    """Remove a port forward: ports remove <host_port>"""
    if host_port is None:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}ports remove <host_port>`"))
        return
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM port_forwards WHERE host_port=?', (int(host_port),))
    row = cur.fetchone()
    conn.close()
    if not row:
        await ctx.send(embed=create_error_embed("Not Found", f"No forward for host port `{host_port}`."))
        return
    row = dict(row)
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM node_vps WHERE container_name=?', (row['vps_container'],))
    r = cur.fetchone()
    conn.close()
    if not r:
        await ctx.send(embed=create_error_embed("VPS Missing", f"Container `{row['vps_container']}` is not tracked."))
        return
    vps = dict(r)
    node = node_get(vps['node_id'])
    if node:
        try:
            await node_client(node).port_remove(row['vps_container'], int(host_port))
        except NodeError as e:
            await ctx.send(embed=create_error_embed("Removal Failed", f"```{e}```"))
            return
    conn = get_db()
    conn.execute('DELETE FROM port_forwards WHERE host_port=?', (int(host_port),))
    conn.commit()
    conn.close()
    await ctx.send(embed=create_success_embed("Forward Removed", f"Host port `{host_port}` released."))


@bot.command(name='check-resources')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def node_check_resources(ctx, node_id: str = None):
    """Check a node's free resources: check-resources <node-name>"""
    if node_id is None:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}check-resources <node-name>`"))
        return
    n = node_resolve(node_id)
    if not n:
        await ctx.send(embed=create_error_embed("Not Found", f"No node with name `{node_id}`."))
        return
    node_id = n['node_id']
    node_label = node_display_name(n)
    try:
        res = await node_client(n).check_resources()
    except NodeError as e:
        await ctx.send(embed=create_error_embed("Node Offline", f"`{node_label}`\n```{e}```"))
        return
    embed = create_info_embed(f"Node {node_label} Resources", "Available capacity")
    add_field(embed, f"{EMOJI_CPU} CPU",
              f"`{res.get('cpu', {}).get('available', '?')}` / `{res.get('cpu', {}).get('total', '?')}` free", True)
    add_field(embed, f"{EMOJI_RAM} RAM",
              f"`{res.get('ram', {}).get('available_gb', '?')}` / `{res.get('ram', {}).get('total_gb', '?')}` GB free", True)
    add_field(embed, f"{EMOJI_DISK} Disk",
              f"`{res.get('disk', {}).get('available_gb', '?')}` / `{res.get('disk', {}).get('total_gb', '?')}` GB free", True)
    await ctx.send(embed=embed)


@bot.command(name='lxc-list')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def node_lxc_list(ctx, node_id: str = None):
    """List containers on a node: lxc-list <node-name>"""
    if node_id is None:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}lxc-list <node-name>`"))
        return
    n = node_resolve(node_id)
    if not n:
        await ctx.send(embed=create_error_embed("Not Found", f"No node with name `{node_id}`."))
        return
    node_id = n['node_id']
    node_label = node_display_name(n)
    try:
        data = await node_client(n).list_containers()
    except NodeError as e:
        await ctx.send(embed=create_error_embed("Node Offline", f"`{node_label}`\n```{e}```"))
        return
    conts = data.get('containers', []) if isinstance(data, dict) else data
    if not conts:
        await ctx.send(embed=create_warning_embed("No Containers", f"`{node_label}` has no containers."))
        return
    lines = []
    for c in conts[:40]:
        nm = c.get('name') if isinstance(c, dict) else c
        st = c.get('status', '?') if isinstance(c, dict) else '?'
        lines.append(f"{EMOJI_ONLINE if st == 'running' else EMOJI_OFFLINE} `{nm}` — `{st}`")
    await ctx.send(embed=create_info_embed(f"Containers · {node_label}", "\n".join(lines)))


@bot.command(name='machine-status')
@is_admin()
@commands.cooldown(1, 10, commands.BucketType.user)
async def node_machine_status(ctx, node_id: str = None, seconds: int = 15):
    """Live node status: machine-status <node-name> [seconds]"""
    if node_id is None:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}machine-status <node-name> [seconds]`"))
        return
    n = node_resolve(node_id)
    if not n:
        await ctx.send(embed=create_error_embed("Not Found", f"No node with name `{node_id}`."))
        return
    node_id = n['node_id']
    node_label = node_display_name(n)
    seconds = max(3, min(int(seconds), 180))
    msg = await ctx.send(embed=create_info_embed("Loading…", f"{EMOJI_LOADING} Polling `{node_label}`…"))
    import time as _t
    end = _t.time() + seconds
    while _t.time() < end:
        try:
            info = await node_client(n).info()
            node_set_status(node_id, True, info)
            cpu = info.get('cpu', {})
            ram = info.get('ram', {})
            disk = info.get('disk', {})
            cont = info.get('containers', {})
            embed = create_info_embed(f"Live · {node_label}", f"{EMOJI_GOOD_SIGNAL} {info.get('hostname', '')}")
            add_field(embed, f"{EMOJI_CPU} Load", f"`{cpu.get('load1', '?')}` / `{cpu.get('total', '?')}` cores", True)
            add_field(embed, f"{EMOJI_RAM} RAM", f"`{ram.get('total_gb', '?')}` GB", True)
            add_field(embed, f"{EMOJI_DISK} Disk", f"`{disk.get('host_free_gb', '?')}` GB free", True)
            add_field(embed, f"{EMOJI_VPS} Containers", f"`{cont.get('running', '?')}`/`{cont.get('total', '?')}` running", True)
            add_field(embed, f"{EMOJI_UPTIME} Uptime", f"`{info.get('uptime', 'unknown')}`", True)
        except NodeError:
            node_set_status(node_id, False)
            embed = create_error_embed("Node Offline", f"{EMOJI_OFFLINE} `{node_label}`")
        try:
            await msg.edit(embed=embed)
        except Exception:
            return
        await asyncio.sleep(3)


@bot.command(name='stop-vps-all')
@is_admin()
@commands.cooldown(1, 10, commands.BucketType.user)
async def node_stop_all(ctx, node_id: str = None):
    """Stop all VPS on a node: stop-vps-all <node-name>"""
    if node_id is None:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}stop-vps-all <node-name>`"))
        return
    n = node_resolve(node_id)
    if not n:
        await ctx.send(embed=create_error_embed("Not Found", f"No node with name `{node_id}`."))
        return
    node_id = n['node_id']
    node_label = node_display_name(n)
    msg = await ctx.send(embed=create_info_embed("Stopping all…", f"{EMOJI_LOADING} `{node_label}`"))
    try:
        res = await node_client(n).stop_all()
    except NodeError as e:
        await msg.edit(embed=create_error_embed("Failed", f"```{e}```"))
        return
    await msg.edit(embed=create_success_embed("Stopped",
        f"Stopped `{len(res.get('stopped', []))}` container(s) on `{node_label}`."))


@bot.command(name='start-all')
@is_admin()
@commands.cooldown(1, 10, commands.BucketType.user)
async def node_start_all(ctx, node_id: str = None):
    """Start all VPS on a node: start-all <node-name>"""
    if node_id is None:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}start-all <node-name>`"))
        return
    n = node_resolve(node_id)
    if not n:
        await ctx.send(embed=create_error_embed("Not Found", f"No node with name `{node_id}`."))
        return
    node_id = n['node_id']
    node_label = node_display_name(n)
    msg = await ctx.send(embed=create_info_embed("Starting all…", f"{EMOJI_LOADING} `{node_label}`"))
    try:
        res = await node_client(n).start_all()
    except NodeError as e:
        await msg.edit(embed=create_error_embed("Failed", f"```{e}```"))
        return
    await msg.edit(embed=create_success_embed("Started",
        f"Started `{len(res.get('started', []))}` container(s) on `{node_label}`."))


@bot.command(name='myvps')
@commands.cooldown(1, 5, commands.BucketType.user)
async def my_vps(ctx):
    """List your VPS"""
    if not await maintenance_check(ctx):
        return
    rows = node_vps_user(ctx.author.id)
    if not rows:
        await ctx.send(embed=create_warning_embed("No VPS", f"You have no VPS. See `{PREFIX}plans`."))
        return
    embed = create_info_embed(f"{EMOJI_VPS} Your VPS ({len(rows)})", f"Owned by {ctx.author.mention}")
    for r in rows[:25]:
        try:
            ts = int(datetime.fromisoformat(r['expires_at']).timestamp())
        except Exception:
            ts = 0
        embed.add_field(
            name=f"ID `{r['vps_id']}` • {r['status']}",
            value=f"`{r['ram']}GB` RAM · `{r['cpu']}` CPU · `{r['disk']}GB` disk\n"
                  f"Node `{node_name_of(r['node_id'])}` · expires <t:{ts}:R>",
            inline=False)
    await ctx.send(embed=embed)


@bot.command(name='list')
@commands.cooldown(1, 5, commands.BucketType.user)
async def list_user_vps(ctx):
    """Detailed list of your VPS"""
    if not await maintenance_check(ctx):
        return
    rows = node_vps_user(ctx.author.id)
    if not rows:
        await ctx.send(embed=create_warning_embed("No VPS", "You have no VPS."))
        return
    embed = create_info_embed("VPS List", f"{EMOJI_VPS} {len(rows)} VPS")
    for r in rows[:20]:
        embed.add_field(
            name=f"{EMOJI_VPS} VPS #{r['vps_id']}",
            value=f"```\nName : {r['container_name']}\n"
                  f"Node : {node_name_of(r['node_id'])}\n"
                  f"RAM  : {r['ram']} GB\n"
                  f"CPU  : {r['cpu']}\n"
                  f"Disk : {r['disk']} GB\n"
                  f"OS   : {r['os_image']}\n"
                  f"State: {r['status']}```",
            inline=False)
    await ctx.send(embed=embed)


@bot.command(name='list-all')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def list_all_vps(ctx):
    """List every VPS across all nodes (Admin)"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM node_vps ORDER BY node_id, vps_id')
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    if not rows:
        await ctx.send(embed=create_warning_embed("No VPS", "No VPS across any node."))
        return
    _node_map = {n['node_id']: node_display_name(n) for n in node_all()}
    lines = [f"`{r['vps_id']}` · <@{r['user_id']}> · `{r['container_name']}` · `{_node_map.get(r['node_id'], r['node_id'])}` · `{r['status']}`"
             for r in rows[:40]]
    await ctx.send(embed=create_info_embed(f"All VPS ({len(rows)})", "\n".join(lines)))


class RemoteOSSelectView(discord.ui.View):
    """OS dropdown for node-only VPS creation, mirroring bot.py's AdminOSSelectView."""
    def __init__(self, ram, cpu, disk, user, ctx, time_arg, node_id, bandwidth=None,
                 bandwidth_spec=None, ports_enabled=1, bypass_cpu=False, bypass_ram=False, bypass_disk=False):
        super().__init__(timeout=300)
        self.ram = ram
        self.cpu = cpu
        self.disk = disk
        self.user = user
        self.ctx = ctx
        self.time_arg = time_arg
        self.node_id = node_id
        self.bandwidth = bandwidth
        self.bypass_cpu = bypass_cpu
        self.bypass_ram = bypass_ram
        self.bypass_disk = bypass_disk
        self.bandwidth_spec = bandwidth_spec
        self.ports_enabled = ports_enabled
        self.selected_os = None

        options = []
        for o in OS_OPTIONS:
            options.append(discord.SelectOption(
                label=o["label"], value=o["value"],
                emoji=o.get('emoji', '🐧'), description=o.get('description', '')))
        self.select = discord.ui.Select(placeholder="Select an OS for the VPS", options=options)
        self.select.callback = self.select_os
        self.add_item(self.select)

        cancel_btn = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger, row=1, emoji=EMOJI_CROSS)
        async def cancel_btn_cb(interaction: discord.Interaction):
            if str(interaction.user.id) != str(self.ctx.author.id):
                await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can cancel."), ephemeral=True)
                return
            await interaction.response.edit_message(embed=create_info_embed("Cancelled", "VPS creation cancelled."), view=None)
        cancel_btn.callback = cancel_btn_cb
        self.add_item(cancel_btn)

    async def select_os(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.ctx.author.id):
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can select."), ephemeral=True)
            return
        self.selected_os = self.select.values[0]
        await interaction.response.defer()

        confirm_view = discord.ui.View(timeout=180)
        confirm_button = discord.ui.Button(label="Confirm", style=discord.ButtonStyle.success, emoji=EMOJI_SUCCESS)
        cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger, emoji=EMOJI_CROSS)

        async def confirm_callback(confirm_interaction: discord.Interaction):
            if str(confirm_interaction.user.id) != str(self.ctx.author.id):
                await confirm_interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can confirm."), ephemeral=True)
                return
            await self.create_remote(confirm_interaction)

        async def cancel_callback(cancel_interaction: discord.Interaction):
            if str(cancel_interaction.user.id) != str(self.ctx.author.id):
                await cancel_interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can cancel."), ephemeral=True)
                return
            await cancel_interaction.response.edit_message(embed=create_info_embed("Cancelled", "VPS creation cancelled."), view=None)

        confirm_button.callback = confirm_callback
        cancel_button.callback = cancel_callback
        confirm_view.add_item(confirm_button)
        confirm_view.add_item(cancel_button)

        time_confirm = ""
        if self.time_arg:
            td = parse_time_string(self.time_arg)
            if td:
                time_confirm = f"\n{EMOJI_UPTIME} **Timer:** {format_timedelta(td)}"
        bw_confirm = f"\n{EMOJI_GLOBAL} **Bandwidth:** `{self.bandwidth_spec}`" if self.bandwidth_spec else ""
        ports_confirm = f"\n{EMOJI_PORTS} **Ports:** {'Enabled' if self.ports_enabled else 'Disabled'}"
        bypass_parts = []
        if self.bypass_cpu:
            bypass_parts.append("CPU")
        if self.bypass_ram:
            bypass_parts.append("RAM")
        if self.bypass_disk:
            bypass_parts.append("Disk")
        bypass_display = f"\n{EMOJI_WARNING} **Bypassing:** {', '.join(bypass_parts)}" if bypass_parts else ""

        embed = create_info_embed("Confirm VPS Creation",
            f"**User:** {self.user.mention}\n"
            f"**Node:** `{self.node_id}`\n"
            f"**OS:** {get_os_emoji(self.selected_os)} {get_os_display_name(self.selected_os)}\n"
            f"**RAM:** {_fmt_num(self.ram)}GB\n"
            f"**CPU:** {_fmt_num(self.cpu)} Cores\n"
            f"**Disk:** {_fmt_num(self.disk)}GB{time_confirm}{bw_confirm}{ports_confirm}{bypass_display}\n\n"
            f"Please confirm to proceed.")
        await interaction.edit_original_response(embed=embed, view=confirm_view)

    async def create_remote(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = str(self.user.id)

        allowed, limit_msg = check_vps_limit(user_id, is_paid=True)
        if not allowed:
            await interaction.edit_original_response(embed=create_error_embed("VPS Limit Reached", limit_msg), view=None)
            return

        node = node_resolve(self.node_id)
        if not node:
            await interaction.edit_original_response(embed=create_error_embed("Unknown Node", f"No node with name `{self.node_id}`."), view=None)
            return
        node_id = node['node_id']
        node_label = node_display_name(node)
        client = node_client(node)
        try:
            res = await client.check_resources()
        except NodeError as e:
            await interaction.edit_original_response(embed=create_error_embed("Node Offline", f"`{node_label}`: {e}"), view=None)
            return
        avail_cpu = res.get('cpu', {}).get('available', 0)
        avail_ram = res.get('ram', {}).get('available_gb', 0)
        avail_disk = res.get('disk', {}).get('available_gb', 0)
        if self.cpu > avail_cpu or self.ram > avail_ram or self.disk > avail_disk:
            await interaction.edit_original_response(embed=create_error_embed("Not Enough Resources",
                f"{EMOJI_WARNING} Requested `{_fmt_num(self.ram)}GB` RAM / `{_fmt_num(self.cpu)}` CPU / `{_fmt_num(self.disk)}GB` disk but "
                f"`{node_label}` has `{_fmt_num(avail_ram)}GB` RAM, `{_fmt_num(avail_cpu)}` CPU, `{_fmt_num(avail_disk)}GB` disk free."), view=None)
            return

        vps_id = _new_remote_vps_id()
        container_name = f"vps-{self.user.id}-{vps_id}"

        creating_embed = create_info_embed("Creating VPS",
            f"{EMOJI_LOADING} Deploying {get_os_display_name(self.selected_os)} VPS for {self.user.mention}...")
        await interaction.edit_original_response(embed=creating_embed, view=None)
        ingress = bw_lxd(self.bandwidth[1]) if self.bandwidth else None
        egress = bw_lxd(self.bandwidth[0]) if self.bandwidth else None
        try:
            await client.create(container_name, self.selected_os, self.ram, self.cpu, self.disk,
                                ingress=ingress, egress=egress)
        except NodeError as e:
            await interaction.edit_original_response(embed=create_error_embed("Creation Failed", f"```{e}```"), view=None)
            return

        td = parse_time_string(self.time_arg) if self.time_arg else None
        expires_at = (datetime.utcnow() + td) if td else (datetime.utcnow() + timedelta(days=1))
        bw_store = self.bandwidth_spec if self.bandwidth_spec else (''
                   if not self.bandwidth else f"{bw_human(self.bandwidth[0])}/{bw_human(self.bandwidth[1])}")
        node_vps_add(vps_id, self.user.id, node_id, container_name,
                     self.ram, self.cpu, self.disk, self.selected_os, expires_at, bandwidth=bw_store,
                     ports_enabled=self.ports_enabled)

        timer_success = f"\n{EMOJI_UPTIME} **Timer:** {format_timedelta(td)}" if td else ""
        bw_success = f"\n{EMOJI_GLOBAL} **Bandwidth:** `{bw_store}`" if bw_store else ""
        ports_success = f"\n{EMOJI_PORTS} **Ports:** {'Enabled' if self.ports_enabled else 'Disabled'}"
        success_embed = create_success_embed("VPS Created Successfully")
        add_field(success_embed, "Owner", self.user.mention, True)
        add_field(success_embed, f"{EMOJI_VPS} VPS ID", f"`{vps_id}`", True)
        add_field(success_embed, f"{EMOJI_GLOBAL} Node", f"`{node_label}`", True)
        add_field(success_embed, "Container", f"`{container_name}`", True)
        add_field(success_embed, "Resources",
                  f"**RAM:** {_fmt_num(self.ram)}GB\n**CPU:** {_fmt_num(self.cpu)} Cores\n"
                  f"**Storage:** {_fmt_num(self.disk)}GB{timer_success}{bw_success}{ports_success}", False)
        add_field(success_embed, "OS", f"{get_os_emoji(self.selected_os)} {get_os_display_name(self.selected_os)}", True)
        if td:
            add_field(success_embed, f"{EMOJI_UPTIME} Expires", f"<t:{int(expires_at.timestamp())}:F>", True)
        try:
            pub = (await client.info()).get('public_ip') or 'unknown'
        except NodeError:
            pub = 'unknown'
        add_field(success_embed, "Access", f"Public IP: `{pub}`", True)
        await interaction.followup.send(embed=success_embed)

        try:
            bypass_parts = []
            if self.bypass_cpu:
                bypass_parts.append("CPU")
            if self.bypass_ram:
                bypass_parts.append("RAM")
            if self.bypass_disk:
                bypass_parts.append("Disk")
            log_bypass = f"\n{EMOJI_WARNING} **Bypassed:** {', '.join(bypass_parts)}" if bypass_parts else ""
            log_timer = f"\n{EMOJI_UPTIME} **Timer:** {format_timedelta(td)}" if td else ""
            await send_log(EMOJI_ADMIN, "VPS Created by Admin",
                f"{EMOJI_USER} **User:** {self.user.mention} (`{user_id}`)\n"
                f"{EMOJI_ADMIN} **Admin:** {self.ctx.author.mention}\n"
                f"{EMOJI_VPS} **Container:** `{container_name}`\n"
                f"{EMOJI_GLOBAL} **Node:** `{node_label}` (ID `{vps_id}`)\n"
                f"{EMOJI_RAM} **RAM:** {_fmt_num(self.ram)}GB | {EMOJI_CPU} **CPU:** {_fmt_num(self.cpu)} | {EMOJI_DISK} **Disk:** {_fmt_num(self.disk)}GB\n"
                f"{get_os_emoji(self.selected_os)} **OS:** {self.selected_os}{log_timer}{log_bypass}",
                color=0x00ff88)
        except Exception:
            pass

        try:
            dm_embed = create_success_embed(f"{EMOJI_SUCCESS} VPS Created!", "Your VPS has been successfully deployed by an admin!")
            created_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            vps_details = f"**VPS ID:** `{vps_id}`\n"
            vps_details += f"**Container Name:** `{container_name}`\n"
            vps_details += f"**Node:** `{node_label}`\n"
            vps_details += f"**Configuration:** {_fmt_num(self.ram)}GB RAM / {_fmt_num(self.cpu)} CPU / {_fmt_num(self.disk)}GB Disk\n"
            vps_details += f"**Status:** Running\n"
            vps_details += f"**OS:** {get_os_emoji(self.selected_os)} {get_os_display_name(self.selected_os)}\n"
            vps_details += f"**Created:** {created_time}"
            add_field(dm_embed, "VPS Details", vps_details, False)
            add_field(dm_embed, "Management",
                      f"• Use `{PREFIX}manage` to manage your VPS\n"
                      f"• Use `{PREFIX}info {vps_id}` for live details\n"
                      f"• Contact admin for upgrades or issues", False)
            await self.user.send(embed=dm_embed)
        except discord.Forbidden:
            pass

def user_is_admin(member):
    """Return True if the given member/user/id is a bot admin."""
    uid = str(getattr(member, 'id', member))
    try:
        return uid in MAIN_ADMIN_IDS or uid in admin_data.get("admins", [])
    except Exception:
        return uid in MAIN_ADMIN_IDS


class RemoteConfirmView(discord.ui.View):
    """Generic yes/no confirmation for destructive remote actions."""
    def __init__(self, author_id, on_confirm, confirm_label="Confirm"):
        super().__init__(timeout=90)
        self.author_id = str(author_id)
        self._on_confirm = on_confirm
        yes = discord.ui.Button(label=confirm_label, style=discord.ButtonStyle.danger, emoji=EMOJI_SUCCESS)
        no = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary, emoji=EMOJI_CROSS)
        yes.callback = self._yes
        no.callback = self._no
        self.add_item(yes)
        self.add_item(no)

    async def _yes(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.author_id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Not your confirmation."), ephemeral=True)
            return
        await self._on_confirm(interaction)

    async def _no(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.author_id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Not your confirmation."), ephemeral=True)
            return
        await interaction.response.edit_message(embed=create_info_embed("Cancelled", "Action cancelled."), view=None)


class RemoteReinstallOSView(discord.ui.View):
    """OS dropdown for reinstalling a remote VPS (mirrors ReinstallOSView)."""
    def __init__(self, ctx, vps, node, requester_id):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.vps = vps
        self.node = node
        self.requester_id = str(requester_id)
        options = [discord.SelectOption(label=o["label"], value=o["value"],
                                        emoji=o.get('emoji', '🐧'), description=o.get('description', ''))
                   for o in OS_OPTIONS]
        self.select = discord.ui.Select(placeholder="Select the new operating system", options=options)
        self.select.callback = self._select
        self.add_item(self.select)
        cancel = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary, emoji=EMOJI_CROSS)
        cancel.callback = self._cancel
        self.add_item(cancel)

    async def _cancel(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.requester_id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Not your session."), ephemeral=True)
            return
        await interaction.response.edit_message(embed=create_info_embed("Cancelled", "Reinstall cancelled."), view=None)

    async def _select(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.requester_id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Not your session."), ephemeral=True)
            return
        await interaction.response.defer()
        os_img = self.select.values[0]
        name = self.vps['container_name']
        client = node_client(self.node)
        await interaction.edit_original_response(
            embed=create_info_embed("Reinstalling…", f"{EMOJI_LOADING} `{name}` → `{os_img}`"), view=None)
        try:
            await client.reinstall(name, os_img)
        except NodeError as e:
            await interaction.edit_original_response(embed=create_error_embed("Reinstall Failed", f"```{e}```"))
            return
        node_vps_update(self.vps['vps_id'], os_image=os_img, status='running')
        await interaction.edit_original_response(embed=create_success_embed(
            f"{EMOJI_SUCCESS} VPS Reinstalled",
            f"`{name}` is now running {get_os_emoji(os_img)} {get_os_display_name(os_img)}."))


class RemoteAddPortModal(discord.ui.Modal, title="Forward a Port"):
    def __init__(self, vps, node, ports_view=None):
        super().__init__()
        self.vps = vps
        self.node = node
        self.ports_view = ports_view
        self.port = discord.ui.TextInput(label="Container port", placeholder="e.g. 25565 (TCP + UDP)")
        self.add_item(self.port)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            p = int(str(self.port.value).strip())
            if not (1 <= p <= 65535):
                raise ValueError
        except ValueError:
            await interaction.followup.send(embed=create_error_embed("Invalid Port", "Enter a port between 1 and 65535."), ephemeral=True)
            return
        client = node_client(self.node)
        try:
            res = await client.port_create(self.vps['container_name'], p)
        except NodeError as e:
            await interaction.followup.send(embed=create_error_embed("Port Forward Failed", f"```{e}```"), ephemeral=True)
            return
        host_port = res.get('host_port', '?')
        pub = res.get('public_ip') or self.node.get('endpoint', '')
        await interaction.followup.send(embed=create_success_embed("Port Forwarded",
            f"Container `{self.vps['container_name']}` port `{p}` → host `{pub}:{host_port}` (TCP+UDP)."), ephemeral=True)
        if self.ports_view:
            await self.ports_view.refresh()


class RemoteDeletePortModal(discord.ui.Modal, title="Remove a Port Forward"):
    def __init__(self, vps, node, ports_view=None):
        super().__init__()
        self.vps = vps
        self.node = node
        self.ports_view = ports_view
        self.port = discord.ui.TextInput(label="Host or local port", placeholder="e.g. 20123 or 25565")
        self.add_item(self.port)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            p = int(str(self.port.value).strip())
        except ValueError:
            await interaction.followup.send(embed=create_error_embed("Invalid Port", "Enter a valid port number."), ephemeral=True)
            return
        client = node_client(self.node)
        try:
            data = await client.port_list(self.vps['container_name'])
            forwards = data.get('forwards', [])
        except NodeError:
            forwards = []
        match = next((f for f in forwards
                      if f.get('container') == self.vps['container_name']
                      and (f.get('host_port') == p or f.get('local_port') == p)), None)
        if not match:
            await interaction.followup.send(embed=create_error_embed("Not Found",
                f"No forward found for port `{p}` on `{self.vps['container_name']}`."), ephemeral=True)
            return
        host_port = match.get('host_port')
        try:
            await client.port_remove(self.vps['container_name'], host_port)
        except NodeError as e:
            await interaction.followup.send(embed=create_error_embed("Remove Failed", f"```{e}```"), ephemeral=True)
            return
        await interaction.followup.send(embed=create_success_embed("Port Removed",
            f"Removed forward `{match.get('local_port')} → {host_port}` for `{self.vps['container_name']}`."), ephemeral=True)
        if self.ports_view:
            await self.ports_view.refresh()


class RemotePortsView(discord.ui.View):
    """List / add / remove forwarded ports for a remote VPS."""
    def __init__(self, ctx, vps, node, requester_id):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.vps = vps
        self.node = node
        self.requester_id = str(requester_id)
        self.message = None
        add = discord.ui.Button(label="Add Port", style=discord.ButtonStyle.success, emoji=EMOJI_PORTS)
        add.callback = self._add
        delete = discord.ui.Button(label="Delete Port", style=discord.ButtonStyle.danger, emoji=EMOJI_CROSS)
        delete.callback = self._delete
        close = discord.ui.Button(label="Close", style=discord.ButtonStyle.secondary, emoji=EMOJI_CROSS)
        close.callback = self._close
        self.add_item(add)
        self.add_item(delete)
        self.add_item(close)

    async def refresh(self):
        client = node_client(self.node)
        forwards, pub = [], None
        try:
            data = await client.port_list(self.vps['container_name'])
            forwards = [f for f in data.get('forwards', []) if f.get('container') == self.vps['container_name']]
            pub = data.get('public_ip')
        except NodeError:
            pass
        if self.message:
            try:
                await self.message.edit(embed=self._embed(forwards, pub), view=self)
            except discord.HTTPException:
                pass

    def _embed(self, forwards, public_ip=None):
        embed = create_info_embed("Port Forwarding", f"`{self.vps['container_name']}` on `{node_name_of(self.node['node_id'])}`")
        pub = (public_ip or '').strip()
        if not pub or pub.upper().startswith('PUT_') or pub.lower() in ('no ip', 'unknown', 'none', 'null', 'n/a'):
            ep = (self.node.get('endpoint') or '')
            if '//' in ep:
                ep = ep.split('//', 1)[1]
            pub = ep.split(':', 1)[0] if ep else 'unknown'
        if not forwards:
            add_field(embed, "Forwards", "No ports forwarded yet. Use **Add Port**.", False)
        else:
            lines = "\n".join(
                f"• `{pub}:{f.get('host_port')}` → `{f.get('local_port')}`"
                for f in forwards)
            add_field(embed, "Forwards", lines, False)
        return embed

    async def _add(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.requester_id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Not your session."), ephemeral=True)
            return
        await interaction.response.send_modal(RemoteAddPortModal(self.vps, self.node, self))

    async def _delete(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.requester_id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Not your session."), ephemeral=True)
            return
        await interaction.response.send_modal(RemoteDeletePortModal(self.vps, self.node, self))

    async def _close(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.requester_id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Not your session."), ephemeral=True)
            return
        await interaction.response.edit_message(view=None)


class RemoteDeleteVPSView(discord.ui.View):
    """Node-aware confirmation for $delete-vps."""
    def __init__(self, ctx, vps, node, reason, user=None):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.vps = vps
        self.node = node
        self.reason = reason
        self.user = user
        self.message = None
        self._completed = False

    async def on_timeout(self):
        if self._completed:
            return
        if self.message:
            try:
                await self.message.edit(embed=create_info_embed(f"{EMOJI_UPTIME} Timeout", "VPS deletion cancelled due to timeout."), view=None)
            except (discord.NotFound, discord.Forbidden):
                pass

    @discord.ui.button(label="Confirm Delete", style=discord.ButtonStyle.danger, emoji=EMOJI_WARNING)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can confirm this action."), ephemeral=True)
            return
        progress = discord.Embed(title=f"{EMOJI_CROSS} Deleting VPS",
                                 description=f"{EMOJI_LOADING} Initializing deletion...", color=0xffaa00)
        progress.set_footer(text=f"{BOT_NAME} VPS Manager - Deleting...", icon_url=THUMBNAIL_URL)
        if THUMBNAIL_URL:
            progress.set_thumbnail(url=THUMBNAIL_URL)
        await interaction.response.edit_message(embed=progress, view=None)
        try:
            progress.description = f"{EMOJI_LOADING} Deleting container `{self.vps['container_name']}`..."
            await interaction.edit_original_response(embed=progress)
            client = node_client(self.node)
            await client.delete(self.vps['container_name'])
            progress.description = f"{EMOJI_LOADING} Cleaning up database records..."
            await interaction.edit_original_response(embed=progress)
            node_vps_remove(self.vps['vps_id'])
            user_id = self.vps.get('user_id')
            update_user_stats(user_id, claimed_vps_count=-1)
            log_suspension(self.vps['container_name'], user_id, 'delete', self.reason, str(self.ctx.author.id))
            user_display = self.user.mention if self.user else f"`{user_id}`"
            send_log(EMOJI_CROSS, "VPS Deleted",
                     f"{EMOJI_USER} **User:** {user_display}\n"
                     f"{EMOJI_ADMIN} **Deleted By:** {self.ctx.author.mention}\n"
                     f"{EMOJI_VPS} **Container:** `{self.vps['container_name']}`\n"
                     f"{EMOJI_VPS} **VPS #:** {self.vps['vps_id']}\n"
                     f"{EMOJI_INFO} **Reason:** {self.reason}", color=0xff3366)
            try:
                if self.user:
                    dm = create_warning_embed("VPS Deleted", "Your VPS has been deleted by an admin.")
                    add_field(dm, "Container", f"`{self.vps['container_name']}`", True)
                    add_field(dm, "Reason", self.reason, False)
                    add_field(dm, "Deleted By", self.ctx.author.mention, False)
                    await self.user.send(embed=dm)
            except (discord.Forbidden, discord.HTTPException, Exception):
                logger.warning(f"Failed to send DM to {user_id} about VPS deletion")
            progress.title = f"{EMOJI_SUCCESS} VPS Deleted Successfully"
            progress.description = (f"{EMOJI_USER} **Owner:** {user_display}\n"
                                    f"{EMOJI_ADMIN} **Deleted By:** {self.ctx.author.mention}\n"
                                    f"{EMOJI_VPS} **Container:** `{self.vps['container_name']}`\n"
                                    f"{EMOJI_VPS} **VPS #:** {self.vps['vps_id']}\n"
                                    f"{EMOJI_INFO} **Reason:** {self.reason}")
            progress.color = 0x00ff88
            progress.set_footer(text=f"{BOT_NAME} VPS Manager - Deleted", icon_url=THUMBNAIL_URL)
            self._completed = True
            for item in self.children:
                item.disabled = True
            await interaction.edit_original_response(embed=progress, view=self)
        except Exception as e:
            logger.error(f"Delete VPS error: {e}", exc_info=True)
            progress.title = f"{EMOJI_CROSS} Deletion Failed"
            progress.description = f"Error: {str(e)}"
            progress.color = 0xff3366
            progress.set_footer(text=f"{BOT_NAME} VPS Manager - Failed", icon_url=THUMBNAIL_URL)
            self._completed = True
            for item in self.children:
                item.disabled = True
            await interaction.edit_original_response(embed=progress, view=self)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, emoji=EMOJI_CROSS)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can cancel this action."), ephemeral=True)
            return
        embed = create_info_embed(f"{EMOJI_SUCCESS} Operation Cancelled", "VPS deletion has been cancelled.")
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)


class RemoteManageSelectView(discord.ui.View):
    """Picker shown by $manage: lists the user's VPS + a dropdown to pick one."""
    def __init__(self, requester_id, rows, is_admin=False, owner_id=None, ctx=None):
        super().__init__(timeout=180)
        self.requester_id = str(requester_id)
        self.rows = rows
        self.is_admin = is_admin
        self.owner_id = str(owner_id or requester_id)
        self.ctx = ctx
        self.message = None
        options = [discord.SelectOption(
            label=f"VPS {v['vps_id']} ({(v.get('plan_name') or 'Custom')})",
            description=f"{v.get('status', 'unknown')} • {v.get('ram')}GB/{v.get('cpu')}cpu/{v.get('disk')}GB • node {node_name_of(v.get('node_id'))}",
            value=str(i)) for i, v in enumerate(rows[:25])]
        self.select = discord.ui.Select(placeholder="Select a VPS to manage", options=options)
        self.select.callback = self._select
        self.add_item(self.select)

    def list_embed(self):
        embed = create_info_embed(f"{EMOJI_VPS} Your VPS", f"Select a VPS from the dropdown below to manage it.")
        if THUMBNAIL_URL:
            embed.set_thumbnail(url=THUMBNAIL_URL)
        for v in self.rows[:25]:
            add_field(embed, f"{EMOJI_VPS} VPS {v['vps_id']}",
                      f"`{v['container_name']}`\n{v.get('status', 'unknown')} • {v.get('ram')}GB / {v.get('cpu')}cpu / {v.get('disk')}GB\nNode `{node_name_of(v.get('node_id'))}`",
                      False)
        embed.set_footer(text=f"{BOT_NAME} VPS Manager", icon_url=THUMBNAIL_URL)
        return embed

    async def _select(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.requester_id and not self.is_admin:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "This is not your VPS list."), ephemeral=True)
            return
        await interaction.response.defer()
        idx = int(self.select.values[0])
        row = self.rows[idx]
        if not node_get(row['node_id']):
            await interaction.edit_original_response(
                embed=create_error_embed("Node Offline", f"Node `{node_name_of(row['node_id'])}` is not connected."), view=None)
            return
        view = RemoteManageView(self.requester_id, [row], is_admin=self.is_admin,
                                owner_id=self.owner_id, ctx=self.ctx)
        await interaction.edit_original_response(embed=await view.create_embed(0), view=view)
        view.message = await interaction.original_response()


class RemoteManageView(discord.ui.View):
    """Node-aware replica of bot.py's ManageView (integrated VPS dropdown + action buttons)."""
    def __init__(self, requester_id, rows, is_shared=False, owner_id=None, is_admin=False,
                 actual_index=None, ctx=None):
        super().__init__(timeout=300)
        self.requester_id = str(requester_id)
        self.rows = rows[:]
        self.selected_index = 0 if rows else None
        self.is_shared = is_shared
        self.owner_id = str(owner_id or requester_id)
        self.is_admin = is_admin
        self.actual_index = actual_index
        self.indices = list(range(len(rows)))
        self.message = None
        self.ctx = ctx
        self.full_status = 'unknown'

        if self.is_shared and self.actual_index is None:
            raise ValueError("actual_index required for shared views")

        if len(rows) > 1:
            options = [
                discord.SelectOption(
                    label=f"VPS {i + 1} ({(r.get('plan_name') or 'Custom')})",
                    description=f"{r.get('status', 'unknown')} • {r.get('ram')}GB/{r.get('cpu')}cpu/{r.get('disk')}GB",
                    value=str(i)
                ) for i, r in enumerate(rows)
            ]
            self.select = discord.ui.Select(placeholder="Select a VPS to manage", options=options)
            self.select.callback = self.select_vps
            self.add_item(self.select)
        else:
            self.add_action_buttons()

    def _row(self):
        idx = self.actual_index if self.is_shared else self.indices[self.selected_index]
        return self.rows[idx]

    async def create_embed(self, index):
        row = self.rows[index]
        container_name = row['container_name']
        node = node_get(row['node_id'])
        info = {}
        stats = {}
        if node:
            client = node_client(node)
            try:
                info = await client.container_info(container_name)
            except NodeError:
                info = {}
            try:
                stats = await client.container_stats(container_name)
            except NodeError:
                stats = {}

        status = (info.get('status') or row.get('status') or 'unknown').lower()
        self.full_status = status
        suspended = row.get('status') == 'suspended'
        whitelisted = bool(row.get('whitelisted', 0))
        purge_protected = bool(row.get('purge_protected', 0))
        status_color = 0x00ff88 if status == 'running' and not suspended else 0xffaa00 if suspended else 0xff3366

        owner_text = ""
        if self.is_admin and self.owner_id != self.requester_id:
            owner_text = f"\n**Owner:** <@{self.owner_id}>"

        embed = discord.Embed(
            title=f"{EMOJI_VPS} VPS Management",
            description=f"Managing VPS #{row['vps_id']}: `{container_name}`{owner_text}",
            color=status_color
        )
        if THUMBNAIL_URL:
            embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.set_footer(
            text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            icon_url=THUMBNAIL_URL
        )

        status_text = status.upper()
        if suspended:
            status_text += " (SUSPENDED)"
        if whitelisted:
            status_text += " (WHITELISTED)"
        purge_text = f"{EMOJI_ONLINE} Enabled" if purge_protected else f"{EMOJI_OFFLINE} Disabled"
        os_display = get_os_display_name(row.get('os_image', 'ubuntu:22.04'))

        res = f"**Plan:** {row.get('plan_name') or 'Custom'}\n"
        res += f"{EMOJI_STATUS} **Status:** {status_text}\n"
        res += f"{EMOJI_RAM} **RAM:** {row.get('ram')}GB\n"
        res += f"{EMOJI_CPU} **CPU:** {row.get('cpu')} Cores\n"
        res += f"{EMOJI_DISK} **Storage:** {row.get('disk')}GB\n"
        res += f"{get_os_emoji(row.get('os_image', 'ubuntu:22.04'))} **OS:** {os_display}\n"
        _ip_val = node_public_ip(node)
        if _ip_val:
            res += f"{EMOJI_GLOBAL} **IP:** `{_ip_val}`\n"
        _bw_spec = row.get('bandwidth')
        _ports_val = int(row.get('ports_enabled', 1) or 0)
        res += f"{EMOJI_PORTS} **Ports:** {'Enabled' if _ports_val else 'Disabled'}\n"
        if _bw_spec:
            _bw_parts = str(_bw_spec).split('/')
            if len(_bw_parts) == 2:
                res += f"{EMOJI_ONLINE} **Up:** {_bw_parts[0].strip()}  {EMOJI_OFFLINE} **Down:** {_bw_parts[1].strip()}\n"
        res += f"{EMOJI_UPTIME} **Uptime:** {stats.get('uptime', 'unknown')}\n"
        res += get_vps_timer_line(node_vps_as_vpsinfo(row))
        res += f"\n**Purge Protection:** {purge_text}"

        embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Resources", value=res, inline=True)
        _loc_val = node_location(node)
        _node_val = f"`{node_display_name(node)}`"
        if _loc_val:
            _node_val += f"\n\n{EMOJI_ARROW_RIGHT} Location\n{_loc_val}"
        embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Node", value=_node_val, inline=True)

        if suspended:
            embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Suspended",
                            value="This VPS is suspended. Contact an admin to unsuspend.", inline=False)
        if whitelisted:
            embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Whitelisted",
                            value="This VPS is exempt from auto-suspension.", inline=False)
        if purge_protected:
            embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Purge Protected",
                            value=f"This VPS is protected from `{PREFIX}purge-vm-all` command.", inline=False)

        live = (f"**CPU Usage:** {stats.get('cpu', 'N/A')}\n"
                f"**Memory:** {stats.get('memory', 'N/A')}\n"
                f"**Disk:** {stats.get('disk', 'N/A')}")
        embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Live Usage", value=live, inline=False)
        embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Controls", value="Use the buttons below to manage your VPS", inline=False)
        return embed

    def add_action_buttons(self):
        start_button = discord.ui.Button(label="Start", style=discord.ButtonStyle.success, emoji=EMOJI_START)
        start_button.callback = lambda inter: self.action_callback(inter, 'start')

        stop_button = discord.ui.Button(label="Stop", style=discord.ButtonStyle.secondary, emoji=EMOJI_STOP)
        stop_button.callback = lambda inter: self.action_callback(inter, 'stop')

        restart_button = discord.ui.Button(label="Restart", style=discord.ButtonStyle.primary, emoji=EMOJI_LOADING)
        restart_button.callback = lambda inter: self.action_callback(inter, 'restart')

        ssh_button = discord.ui.Button(label="SSHX", style=discord.ButtonStyle.primary, emoji=EMOJI_SSHX)
        ssh_button.callback = lambda inter: self.action_callback(inter, 'ssh')

        tmate_button = discord.ui.Button(label="Tmate", style=discord.ButtonStyle.success, emoji=EMOJI_TMATE)
        tmate_button.callback = lambda inter: self.action_callback(inter, 'tmate')

        ipv4_button = discord.ui.Button(label="IPv4-SSH", style=discord.ButtonStyle.secondary, emoji=EMOJI_GLOBAL)
        ipv4_button.callback = lambda inter: self.action_callback(inter, 'ipv4_ssh')

        filemanager_button = discord.ui.Button(label="File-Manager", style=discord.ButtonStyle.secondary, emoji=EMOJI_FOLDER)
        filemanager_button.callback = lambda inter: self.action_callback(inter, 'filemanager')

        stats_button = discord.ui.Button(label="Stats", style=discord.ButtonStyle.secondary, emoji=EMOJI_STATS)
        stats_button.callback = lambda inter: self.action_callback(inter, 'stats')

        try:
            _ports_on = int(self._row().get('ports_enabled', 1) or 0)
        except Exception:
            _ports_on = 1
        _requester_admin = user_is_admin(self.requester_id) or self.is_admin
        ports_button = discord.ui.Button(label="Ports", style=discord.ButtonStyle.secondary,
                                         emoji=EMOJI_PORTS, disabled=(not _requester_admin and not _ports_on))
        ports_button.callback = lambda inter: self.action_callback(inter, 'ports')

        self.add_item(start_button)
        self.add_item(restart_button)
        self.add_item(stop_button)
        if not self.is_shared and not self.is_admin:
            reinstall_button = discord.ui.Button(label="Reinstall", style=discord.ButtonStyle.danger, emoji=EMOJI_REINSTALL)
            reinstall_button.callback = lambda inter: self.action_callback(inter, 'reinstall')
            self.add_item(reinstall_button)
        self.add_item(ssh_button)
        self.add_item(tmate_button)
        self.add_item(ipv4_button)
        self.add_item(filemanager_button)
        self.add_item(stats_button)
        self.add_item(ports_button)

    async def select_vps(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.requester_id and not self.is_admin:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "This is not your VPS!"), ephemeral=True)
            return
        await interaction.response.defer()
        self.selected_index = int(self.select.values[0])
        new_embed = await self.create_embed(self.selected_index)
        self.clear_items()
        self.add_action_buttons()
        await interaction.edit_original_response(embed=new_embed, view=self)
        self.message = await interaction.original_response()

    async def action_callback(self, interaction: discord.Interaction, action: str):
        if str(interaction.user.id) != self.requester_id and not self.is_admin:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "This is not your VPS!"), ephemeral=True)
            return

        if self.selected_index is None and len(self.rows) == 1:
            self.selected_index = 0
        if self.selected_index is None:
            await interaction.response.send_message(embed=create_error_embed("No VPS Selected", "Please select a VPS first."), ephemeral=True)
            return

        row = self._row()
        node = node_get(row['node_id'])
        container_name = row['container_name']
        suspended = row.get('status') == 'suspended'
        owner_id = str(row['user_id'])

        if suspended and not self.is_admin and action != 'stats':
            await interaction.response.send_message(
                embed=create_error_embed("Access Denied", "This VPS is suspended. Contact an admin to unsuspend."), ephemeral=True)
            return
        if not node:
            await interaction.response.send_message(
                embed=create_error_embed("Node Offline", f"Node `{node_name_of(row['node_id'])}` is not connected."), ephemeral=True)
            return
        client = node_client(node)

        try:
            _live = await client.container_info(container_name)
            self.full_status = (_live.get('status') or row.get('status') or 'unknown').lower()
        except NodeError:
            self.full_status = (row.get('status') or 'unknown').lower()
        running = self.full_status == 'running'

        if action == 'stats':
            if not running:
                await interaction.response.send_message(
                    embed=create_warning_embed(f"{EMOJI_WARNING} VPS Not Running", f"`{container_name}` is not running. Start it first."), ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
            progress_msg = await interaction.followup.send(
                embed=create_info_embed(f"{EMOJI_STATS} Live Statistics", f"{EMOJI_LOADING} Starting live stats..."),
                ephemeral=True, wait=True)
            start = time.time()
            try:
                while (time.time() - start) < 3600:
                    iter_start = time.time()
                    try:
                        s = await client.container_stats(container_name)
                    except NodeError as e:
                        await progress_msg.edit(embed=create_error_embed("Stats Error", f"```{e}```"))
                        return
                    embed = create_info_embed(f"{EMOJI_STATS} Live Statistics", f"Real-time stats for `{container_name}`")
                    add_field(embed, f"{EMOJI_STATUS} Status", f"`{str(s.get('status', '?')).upper()}`", True)
                    add_field(embed, f"{EMOJI_CPU} CPU", f"`{s.get('cpu', 'N/A')}`", True)
                    add_field(embed, f"{EMOJI_RAM} Memory", f"`{s.get('memory', 'N/A')}`", True)
                    add_field(embed, f"{EMOJI_DISK} Disk", f"`{s.get('disk', 'N/A')}`", True)
                    add_field(embed, f"{EMOJI_UPTIME} Uptime", f"`{s.get('uptime', 'unknown')}`", True)
                    timer_line = get_vps_timer_line(node_vps_as_vpsinfo(row))
                    if timer_line:
                        add_field(embed, f"{EMOJI_UPTIME} Auto-Suspend Timer", timer_line.replace("\n", ""), True)
                    await progress_msg.edit(embed=embed)
                    elapsed = time.time() - iter_start
                    await asyncio.sleep(max(0, 1 - elapsed))
            except Exception:
                pass
            return

        if action == 'reinstall':
            if self.is_shared or self.is_admin:
                await interaction.response.send_message(
                    embed=create_error_embed("Access Denied", "Only the VPS owner can reinstall!"), ephemeral=True)
                return
            if suspended:
                await interaction.response.send_message(
                    embed=create_error_embed("Cannot Reinstall", "Unsuspend the VPS first."), ephemeral=True)
                return
            os_view = RemoteReinstallOSView(self.ctx, row, node, interaction.user.id)
            embed = discord.Embed(
                title=f"{EMOJI_REINSTALL} Reinstall VPS",
                description=f"Choose a new operating system for **{container_name}**",
                color=0xffaa00)
            if THUMBNAIL_URL:
                embed.set_thumbnail(url=THUMBNAIL_URL)
            embed.set_footer(
                text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                icon_url=THUMBNAIL_URL)
            current_os_display = get_os_display_name(row.get('os_image', 'ubuntu:22.04'))
            embed.add_field(name=f"{EMOJI_INFO} Current Configuration",
                            value=f"**Container:** `{container_name}`\n**Current OS:** {current_os_display}", inline=False)
            embed.add_field(name=f"{EMOJI_WARNING} Warning",
                            value="This will erase ALL data on this VPS. Make sure to backup important files first.", inline=False)
            await interaction.response.send_message(embed=embed, view=os_view, ephemeral=True)
            return

        if action == 'ipv4_ssh':
            if not running:
                await interaction.response.send_message(
                    embed=create_warning_embed(f"{EMOJI_WARNING} VPS Not Running", f"`{container_name}` is not running. Start it first."), ephemeral=True)
                return
            view = IPv4SSHView(container_name, owner_id, interaction.user, node=node)
            desc = (f"{EMOJI_INFO} Press **Start** to begin the persistent IPv4 SSH tunnel"
                    if container_name not in _remote_ipv4_tunnels else f"{EMOJI_ONLINE} Tunnel is active")
            await interaction.response.send_message(embed=view._status_embed(desc), view=view, ephemeral=True)
            return

        if action == 'filemanager':
            if not running:
                await interaction.response.send_message(
                    embed=create_warning_embed(f"{EMOJI_WARNING} VPS Not Running", f"`{container_name}` is not running. Start it first."), ephemeral=True)
                return
            view = FileManagerView(container_name, owner_id, interaction.user, node=node)
            desc = (f"{EMOJI_INFO} Press **Start** to set up File Manager"
                    if container_name not in _remote_filemanager else f"{EMOJI_ONLINE} File Manager is active")
            await interaction.response.send_message(embed=view._status_embed(desc), view=view, ephemeral=True)
            return

        if action == 'ports':
            if not (user_is_admin(interaction.user.id) or self.is_admin) and not int(row.get('ports_enabled', 1) or 0):
                await interaction.response.send_message(
                    embed=create_error_embed("Ports Disabled",
                        "Port forwarding is disabled for this VPS. Contact an admin to enable it."), ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True, thinking=True)
            view = RemotePortsView(self.ctx, row, node, interaction.user.id)
            try:
                data = await client.port_list(container_name)
                forwards = [f for f in data.get('forwards', []) if f.get('container') == container_name]
            except NodeError as e:
                await interaction.followup.send(embed=create_error_embed("Ports Unavailable", f"```{e}```"), ephemeral=True, view=view)
                return
            msg = await interaction.followup.send(embed=view._embed(forwards, data.get('public_ip')), view=view, ephemeral=True)
            view.message = msg
            return

        await interaction.response.defer(ephemeral=True)

        if action == 'start':
            if running:
                await interaction.followup.send(
                    embed=create_warning_embed(f"{EMOJI_WARNING} Already Running", f"`{container_name}` is already running."), ephemeral=True)
                return
            progress_msg = await interaction.followup.send(
                embed=create_info_embed(f"{EMOJI_START} Starting VPS", f"{EMOJI_LOADING} Starting `{container_name}`, please wait..."),
                ephemeral=True, wait=True)
            try:
                await client.start(container_name)
                node_vps_set_status(row['vps_id'], 'running')
                await progress_msg.edit(embed=create_success_embed(f"{EMOJI_SUCCESS} VPS Started", f"VPS `{container_name}` is now running!"))
            except NodeError as e:
                await progress_msg.edit(embed=create_error_embed(f"{EMOJI_WARNING} Start Failed", f"```{e}```"))

        elif action == 'stop':
            if not running:
                await interaction.followup.send(
                    embed=create_warning_embed(f"{EMOJI_WARNING} Already Stopped", f"`{container_name}` is already stopped."), ephemeral=True)
                return
            progress_msg = await interaction.followup.send(
                embed=create_info_embed(f"{EMOJI_STOP} Stopping VPS", f"{EMOJI_LOADING} Stopping `{container_name}`, please wait..."),
                ephemeral=True, wait=True)
            try:
                await client.stop(container_name)
                node_vps_set_status(row['vps_id'], 'stopped')
                await progress_msg.edit(embed=create_success_embed(f"{EMOJI_SUCCESS} VPS Stopped", f"VPS `{container_name}` has been stopped!"))
            except NodeError as e:
                await progress_msg.edit(embed=create_error_embed(f"{EMOJI_WARNING} Stop Failed", f"```{e}```"))

        elif action == 'restart':
            if not running:
                await interaction.followup.send(
                    embed=create_warning_embed(f"{EMOJI_WARNING} VPS Not Running", f"`{container_name}` is not running. Start it first."), ephemeral=True)
                return
            progress_msg = await interaction.followup.send(
                embed=create_info_embed(f"{EMOJI_LOADING} Restarting VPS", f"{EMOJI_LOADING} Restarting `{container_name}`, please wait..."),
                ephemeral=True, wait=True)
            try:
                await client.restart(container_name)
                node_vps_set_status(row['vps_id'], 'running')
                await progress_msg.edit(embed=create_success_embed(f"{EMOJI_SUCCESS} VPS Restarted", f"VPS `{container_name}` has been restarted!"))
            except NodeError as e:
                await progress_msg.edit(embed=create_error_embed(f"{EMOJI_WARNING} Restart Failed", f"```{e}```"))

        elif action in ('ssh', 'tmate'):
            is_ssh = (action == 'ssh')
            label = "SSHX" if is_ssh else "Tmate"
            label_emoji = EMOJI_SSHX if is_ssh else EMOJI_TMATE
            if not running:
                await interaction.followup.send(
                    embed=create_warning_embed(f"{EMOJI_WARNING} VPS Not Running", f"`{container_name}` is not running. Start it first."), ephemeral=True)
                return
            progress_msg = await interaction.followup.send(
                embed=create_info_embed(f"{label_emoji} {label} Access", "Starting session..."),
                ephemeral=True, wait=True)
            try:
                url = await self._remote_sshx(client, container_name, progress_msg) if is_ssh \
                    else await self._remote_tmate(client, container_name, progress_msg)
            except Exception as e:
                logger.error(f"{label} error for {container_name}: {e}", exc_info=True)
                await progress_msg.edit(embed=create_error_embed(f"{EMOJI_WARNING} {label} Error", str(e)))
                return
            if not url:
                await progress_msg.edit(embed=create_info_embed(f"{label} Started",
                    f"Session started but no URL was returned. Run `{PREFIX}exec {container_name} cat /tmp/{'sgm_sshx.out' if is_ssh else 'sgm_tmate.out'}` to see the URL."))
                return
            try:
                dm = create_info_embed(f"{label} Access", f"Session for `{container_name}`:")
                add_field(dm, "Command / URL", f"```{url}```", False)
                add_field(dm, f"{EMOJI_SYSTEM} Security", "This link is temporary. Do not share it.", False)
                await interaction.user.send(embed=dm)
                await progress_msg.edit(embed=create_success_embed(f"{EMOJI_SUCCESS} {label} Ready", "Check your DMs for the link!"))
            except discord.Forbidden:
                await progress_msg.edit(embed=create_error_embed("DM Failed", "Enable DMs to receive the link."))

    async def _remote_sshx(self, client, container_name, progress_msg):
        await progress_msg.edit(embed=create_info_embed(f"{EMOJI_SSHX} SSHX Access", "Starting SSHX session..."))
        chk = await client.exec(container_name, "which sshx")
        if not (chk.get('stdout') or '').strip():
            await progress_msg.edit(embed=create_info_embed(f"{EMOJI_SSHX} Installing SSHX",
                f"{EMOJI_LOADING} Step 1/5: Updating packages and installing curl..."))
            await client.exec(container_name, "apt-get update -y", timeout=180)
            await client.exec(container_name, "apt-get install -y curl", timeout=120)
            await progress_msg.edit(embed=create_info_embed(f"{EMOJI_SSHX} Installing SSHX",
                f"{EMOJI_LOADING} Step 2/5: Downloading sshx installer..."))
            await client.exec(container_name, "curl -L --connect-timeout 30 --max-time 300 https://sshx.io/get -o /tmp/sshx_install.sh", timeout=310)
            await progress_msg.edit(embed=create_info_embed(f"{EMOJI_SSHX} Installing SSHX",
                f"{EMOJI_LOADING} Step 3/5: Running sshx installer..."))
            await client.exec(container_name, "sh /tmp/sshx_install.sh", timeout=120)
            await client.exec(container_name, "rm -f /tmp/sshx_install.sh", timeout=10)
        await progress_msg.edit(embed=create_info_embed(f"{EMOJI_SSHX} Starting SSHX",
            f"{EMOJI_LOADING} Launching session..."))
        await client.exec(container_name, "pkill -9 sshx 2>/dev/null; rm -f /tmp/sshx_output.txt", timeout=10)
        await client.exec(container_name, "nohup sshx > /tmp/sshx_output.txt 2>&1 &", timeout=10)
        await asyncio.sleep(5)
        out = await client.exec(container_name, "cat /tmp/sshx_output.txt", timeout=10)
        clean = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', (out.get('stdout') or ''))
        m = re.search(r'https?://sshx\.io/\S+', clean)
        return m.group(0) if m else None

    async def _remote_tmate(self, client, container_name, progress_msg):
        await progress_msg.edit(embed=create_info_embed(f"{EMOJI_TMATE} Tmate Access", "Starting Tmate session..."))
        chk = await client.exec(container_name, "which tmate")
        if not (chk.get('stdout') or '').strip():
            await progress_msg.edit(embed=create_info_embed(f"{EMOJI_TMATE} Installing Tmate",
                f"{EMOJI_LOADING} Installing tmate (this may take a minute)..."))
            await client.exec(container_name, "apt-get update -y", timeout=180)
            await client.exec(container_name, "apt-get install -y tmate", timeout=120)
        await progress_msg.edit(embed=create_info_embed(f"{EMOJI_TMATE} Starting Tmate",
            f"{EMOJI_LOADING} Generating SSH keys..."))
        await client.exec(container_name, "mkdir -p /root/.ssh && [ -f /root/.ssh/id_rsa ] || ssh-keygen -t rsa -f /root/.ssh/id_rsa -N '' -q", timeout=30)
        session_name = f"{BOT_NAME.lower()}-tmate-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        await client.exec(container_name, f"pkill -9 tmate 2>/dev/null; rm -f /tmp/{session_name}.sock", timeout=10)
        await progress_msg.edit(embed=create_info_embed(f"{EMOJI_TMATE} Starting Tmate",
            f"{EMOJI_LOADING} Launching tmate session..."))
        await client.exec(container_name, f"tmate -S /tmp/{session_name}.sock new-session -d", timeout=15)
        await asyncio.sleep(3)
        await progress_msg.edit(embed=create_info_embed(f"{EMOJI_TMATE} Starting Tmate",
            f"{EMOJI_LOADING} Waiting for connection..."))
        ssh_url = None
        last_error = ""
        for _ in range(15):
            await asyncio.sleep(2)
            r = await client.exec(container_name, f"tmate -S /tmp/{session_name}.sock display -p '#{{tmate_ssh}}'", timeout=15)
            url = (r.get('stdout') or '').strip()
            if url and not url.startswith("waiting") and "tmate" in url.lower():
                ssh_url = url
                break
            if r.get('stderr'):
                last_error = (r.get('stderr') or '').strip()
        if not ssh_url and last_error:
            raise RuntimeError(last_error)
        return ssh_url


@bot.command(name='manage')
@commands.cooldown(1, 5, commands.BucketType.user)
async def manage_cmd(ctx, query: str = None):
    """Manage a VPS: manage [vps-id] | manage @user (admin)"""
    if not await maintenance_check(ctx):
        return
    user_id = str(ctx.author.id)
    admin = user_is_admin(ctx.author)

    if query:
        member = ctx.message.mentions[0] if ctx.message.mentions else None
        if member is not None:
            if not admin:
                await ctx.send(embed=create_error_embed("Access Denied", "Only admins can manage other users' VPS."))
                return
            rows = node_vps_user(member.id)
            if not rows:
                embed = create_no_vps_embed()
                embed.title = f"{EMOJI_STAR} {BOT_NAME} - No VPS Found"
                embed.description = f"{member.mention} doesn't have any VPS."
                await ctx.send(embed=embed)
                return
            sel = RemoteManageSelectView(ctx.author.id, rows, is_admin=True, owner_id=str(member.id), ctx=ctx)
            sel.message = await ctx.send(embed=sel.list_embed(), view=sel)
            return

        token = query.strip().lstrip('#')
        target = node_vps_get(int(token)) if token.isdigit() else None
        if target is None and token:
            target = node_vps_by_container(token)
        if target is None:
            await ctx.send(embed=create_error_embed("Not Found",
                f"No VPS found for `{query}`.\nUsage: `{PREFIX}manage [vps-id]`"))
            return

        owner = str(target['user_id'])
        if owner != user_id and not admin:
            await ctx.send(embed=create_error_embed("Access Denied", "This is not your VPS!"))
            return
        if not target.get('node_id') or not node_get(target['node_id']):
            await ctx.send(embed=create_error_embed("Node Offline", f"Node `{node_name_of(target.get('node_id'))}` is not connected."))
            return
        view = RemoteManageView(user_id, [target], is_admin=(owner != user_id), owner_id=owner, ctx=ctx)
        view.message = await ctx.send(embed=await view.create_embed(0), view=view)
        return

    rows = node_vps_user(user_id)
    if not rows:
        await ctx.send(embed=create_no_vps_embed())
        return
    sel = RemoteManageSelectView(user_id, rows, is_admin=False, ctx=ctx)
    sel.message = await ctx.send(embed=sel.list_embed(), view=sel)


@bot.command(name='manage-shared')
@commands.cooldown(1, 3, commands.BucketType.user)
async def manage_shared_remote(ctx, owner: discord.Member, vps_id: int):
    """Manage a VPS that has been shared with you: manage-shared @owner <vps-id>"""
    if not await maintenance_check(ctx):
        return
    requester = str(ctx.author.id)
    owner_id = str(owner.id)
    vps = node_vps_get(vps_id)
    if not vps or str(vps['user_id']) != owner_id:
        await ctx.send(embed=create_error_embed("Not Found", f"{owner.mention} has no VPS with id `{vps_id}`."))
        return
    shared = node_vps_shared_list(vps)
    if requester not in shared:
        await ctx.send(embed=create_error_embed("Access Denied", f"This VPS has not been shared with you."))
        return
    if not node_get(vps['node_id']):
        await ctx.send(embed=create_error_embed("Node Offline", f"Node `{node_name_of(vps['node_id'])}` is not connected."))
        return
    view = RemoteManageView(requester, [vps], is_shared=True, owner_id=owner_id, actual_index=0, ctx=ctx)
    view.message = await ctx.send(embed=await view.create_embed(0), view=view)



class RemotePurgeAllVMSView(discord.ui.View):
    """Node-aware purge-all view: deletes every unprotected node_vps via the node API."""
    def __init__(self, ctx, node_id=None):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.node_id = node_id
        self.message = None
        self.is_running = False

    async def on_timeout(self):
        if self.message and not self.is_running:
            try:
                await self.message.edit(embed=create_info_embed("Timeout", "Purge operation cancelled due to timeout."), view=None)
            except (discord.NotFound, discord.Forbidden):
                pass

    def _progress_bar(self, percentage, length=20):
        filled = int(length * percentage / 100)
        bar = "█" * filled + "░" * (length - filled)
        return f"`[{bar}] {percentage}%`"

    @discord.ui.button(label="Confirm Purge All", style=discord.ButtonStyle.danger, emoji=EMOJI_WARNING)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can confirm this action."), ephemeral=True)
            return
        self.is_running = True
        button.disabled = True
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)

        rows = node_vps_all()
        if self.node_id:
            rows = [v for v in rows if v.get('node_id') == self.node_id]
        all_vps = [v for v in rows if not v.get('purge_protected')]
        protected_vps = len(rows) - len(all_vps)

        if not all_vps:
            msg = (f"Found **{protected_vps}** protected VPS but no unprotected VPS to purge."
                   if protected_vps else "There are no VPS to purge.")
            await interaction.followup.send(embed=create_info_embed("Nothing To Purge", msg))
            return

        total_to_delete = len(all_vps)
        progress_embed = discord.Embed(
            title="Purging Unprotected VPS",
            description=f"Deleting {total_to_delete} unprotected VPS (1 every 3s).\n{protected_vps} protected VPS will be skipped.",
            color=0xffaa00)
        if THUMBNAIL_URL:
            progress_embed.set_thumbnail(url=THUMBNAIL_URL)
        add_field(progress_embed, "Status", f"{EMOJI_LOADING} Initializing...", False)
        progress_msg = await interaction.followup.send(embed=progress_embed)

        deleted_count = skipped_count = failed_count = 0
        users_affected = set()
        node_cache = {}

        for i, vps in enumerate(all_vps, 1):
            name = vps['container_name']
            try:
                node = node_cache.get(vps['node_id']) or node_get(vps['node_id'])
                if node:
                    node_cache[vps['node_id']] = node
                if node:
                    try:
                        await node_client(node).delete(name)
                    except NodeError as e:
                        if "not found" not in str(e).lower():
                            raise
                node_vps_remove(vps['vps_id'])
                if (vps.get('plan_name') or 'Custom') != 'Custom':
                    update_user_stats(str(vps['user_id']), claimed_vps_count=-1)
                log_suspension(name, vps['user_id'], 'purge_all', f"Purged by {self.ctx.author.name}", str(self.ctx.author.id))
                deleted_count += 1
                users_affected.add(vps['user_id'])
                if i % 5 == 0 or i == total_to_delete:
                    percentage = int((i / total_to_delete) * 100)
                    status_text = (f"{EMOJI_SUCCESS} Deleted: {deleted_count}\n"
                                   f"{EMOJI_CROSS} Failed: {failed_count}\n"
                                   f"{EMOJI_USER} Users Affected: {len(users_affected)}")
                    progress_embed = discord.Embed(title="Purging Unprotected VPS",
                                                   description=f"Progress: {i}/{total_to_delete} VPS processed",
                                                   color=0xffaa00)
                    if THUMBNAIL_URL:
                        progress_embed.set_thumbnail(url=THUMBNAIL_URL)
                    add_field(progress_embed, "Status", status_text, False)
                    add_field(progress_embed, "Progress Bar", self._progress_bar(percentage), False)
                    await progress_msg.edit(embed=progress_embed)
            except Exception as e:
                logger.error(f"Failed to purge {name}: {e}")
                failed_count += 1
            await asyncio.sleep(3)

        final_embed = discord.Embed(title=f"{EMOJI_SUCCESS} Purge Complete",
                                    description=f"Successfully purged {deleted_count} unprotected VPS", color=0x00ff88)
        if THUMBNAIL_URL:
            final_embed.set_thumbnail(url=THUMBNAIL_URL)
        summary = (f"**Total Unprotected VPS:** {total_to_delete}\n"
                   f"**Successfully Deleted:** {deleted_count}\n"
                   f"**Failed Deletions:** {failed_count}\n"
                   f"**Protected VPS (Skipped):** {skipped_count}\n"
                   f"**Users Affected:** {len(users_affected)}")
        add_field(final_embed, "Summary", summary, False)
        await progress_msg.edit(embed=final_embed)


@bot.command(name='purge-vm-all')
@is_main_admin()
@commands.cooldown(1, 300, commands.BucketType.user)
async def purge_all_vms_remote(ctx, node_id: str = None):
    """Purge ALL unprotected VPS on a node (with confirmation button)."""
    if not node_id:
        await ctx.send(embed=create_error_embed("Missing Argument", f"Usage: `{PREFIX}purge-vm-all <node-name>`"))
        return
    node = node_resolve(node_id)
    if not node:
        await ctx.send(embed=create_error_embed("Node Not Found", f"No node with name `{node_id}`."))
        return
    node_id = node['node_id']
    node_label = node_display_name(node)
    rows = [v for v in node_vps_all() if v.get('node_id') == node_id]
    total_vps = sum(1 for v in rows if not v.get('purge_protected'))
    protected_vps = len(rows) - total_vps

    if total_vps == 0:
        if protected_vps > 0:
            embed = create_info_embed("All VPS Protected",
                f"Found **{protected_vps}** protected VPS on `{node_label}` but no unprotected VPS to purge.")
        else:
            embed = create_info_embed("No VPS Found", f"There are no VPS on `{node_label}` to purge.")
        await ctx.send(embed=embed)
        return

    estimated_time = total_vps * 3
    embed = discord.Embed(title=f"{EMOJI_WARNING} PURGE ALL UNPROTECTED VPS {EMOJI_WARNING}",
                          description=f"This will delete **ALL {total_vps} UNPROTECTED VPS** on `{node_label}`!",
                          color=0xff0000)
    if THUMBNAIL_URL:
        embed.set_thumbnail(url=THUMBNAIL_URL)
    warning = (f"**Node:** `{node_label}`\n"
               f"**Unprotected VPS to delete:** {total_vps}\n"
               f"**Protected VPS (skipped):** {protected_vps}\n"
               f"**Deletion speed:** 1 VPS every 3 seconds\n"
               f"**Estimated time:** {estimated_time // 60} minutes and {estimated_time % 60} seconds\n\n"
               f"**{EMOJI_WARNING} THIS ACTION CANNOT BE UNDONE!**")
    add_field(embed, "Warning", warning, False)
    view = RemotePurgeAllVMSView(ctx, node_id)
    msg = await ctx.send(embed=embed, view=view)
    view.message = msg


@bot.command(name='suspension-logs')
@is_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def suspension_logs_remote(ctx, container_name: str = None):
    """View suspension logs: suspension-logs [container]"""
    logs = get_suspension_logs(container_name)
    if not logs:
        await ctx.send(embed=create_info_embed("Suspension Logs", "No logs found."))
        return
    log_text = ""
    for log in logs[:10]:
        log_text += f"**{log['action']}** - {log['container_name']}\n"
        log_text += f"Time: {log['created_at'][:19]}\n"
        if log['reason']:
            log_text += f"Reason: {log['reason']}\n"
        log_text += "\n"
    await ctx.send(embed=create_info_embed("Suspension Logs", log_text))


# ==================================================== MULTI-NODE MANAGEMENT END =====================================================

# ==================================================== HELP SYSTEM =====================================================

class HelpView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.current_category = "user"
        self.message = None
        
        self.select = discord.ui.Select(
            placeholder="Select a category...",
            options=[
                discord.SelectOption(label="User Commands", value="user", emoji=EMOJI_USER, description="Basic commands for all users"),
                discord.SelectOption(label="VPS Management", value="vps", emoji=EMOJI_VPS, description="Manage your VPS containers"),
                discord.SelectOption(label="Node Management", value="node", emoji=EMOJI_GLOBAL, description="Manage VPS on remote nodes"),
                discord.SelectOption(label="Port Forwarding", value="ports", emoji=EMOJI_PORTS, description="Manage port forwards"),
                discord.SelectOption(label="Bot System Commands", value="bot_system", emoji=EMOJI_BOT, description="Bot economy and stats"),
                discord.SelectOption(label="System Commands", value="system", emoji=EMOJI_SYSTEM, description="Bot and system commands"),
                discord.SelectOption(label="Admin Commands", value="admin", emoji=EMOJI_ADMIN, description="Administrator commands"),
                discord.SelectOption(label="Main Admin Commands", value="main_admin", emoji=EMOJI_MAIN_ADMIN, description="Main administrator commands"),
            ]
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)
        
        self.update_embed()
    
    async def select_callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("This help menu is not for you!", ephemeral=True)
            return
        
        self.current_category = interaction.data["values"][0]
        self.update_embed()
        await interaction.response.edit_message(embed=self.embed, view=self)
    
    def update_embed(self):
        colors = {
            "user": 0x3498db,
            "vps": 0x2ecc71,
            "node": 0x00ccff,
            "ports": 0xe74c3c,
            "bot_system": 0x9b59b6,
            "system": 0xf39c12,
            "admin": 0xe67e22,
            "main_admin": 0xf1c40f
        }
        
        color = colors.get(self.current_category, 0x5865F2)
        
        if self.current_category == "user":
            embed = discord.Embed(
                title=f"{EMOJI_HELP} {BOT_NAME} Help - {EMOJI_USER} User Commands",
                description="Basic commands available to all users",
                color=color
            )
            commands = [
                f"**`{PREFIX}ping`** - Check bot latency",
                f"**`{PREFIX}ping <node-name>`** - Check a node's latency",
                f"**`{PREFIX}uptime <node-name>`** - Show node/bot uptime",
                f"**`{PREFIX}plans`** - View free VPS plans with emojis",
                f"**`{PREFIX}freeplans`** - Free plans list",
                f"**`{PREFIX}stats`** - View your invite/boost stats",
                f"**`{PREFIX}myvps`** - List your VPS",
                f"**`{PREFIX}list`** - Detailed VPS list",
                f"**`{PREFIX}manage [vps-id]`** - Interactive VPS control panel",
                f"**`{PREFIX}claimfree inv <1-6>`** - Claim invite VPS",
                f"**`{PREFIX}claimfree boost <1-5>`** - Claim boost VPS",
                f"**`{PREFIX}share-user @user <vps-id>`** - Share VPS access",
                f"**`{PREFIX}share-ruser @user <vps-id>`** - Revoke VPS access",
                f"**`{PREFIX}manage-shared @owner <vps-id>`** - Manage shared VPS"
            ]
            total = 14
            
        elif self.current_category == "vps":
            embed = discord.Embed(
                title=f"{EMOJI_HELP} {BOT_NAME} Help - {EMOJI_VPS} VPS Management",
                description="Commands for managing your VPS",
                color=color
            )
            commands = [
                f"**`{PREFIX}myvps`** - List your VPS",
                f"**`{PREFIX}list`** - Detailed VPS list",
                 f"**`{PREFIX}manage [vps-id]`** - Interactive VPS control panel",
                 f"**`{PREFIX}start <vps-id>`** - Start VPS",
                f"**`{PREFIX}stop <vps-id>`** - Stop VPS",
                f"**`{PREFIX}restart <vps-id>`** - Restart VPS",
                f"**`{PREFIX}info <vps-id>`** - VPS information",
                f"**`{PREFIX}stats <vps-id>`** - VPS stats",
            ]
            total = 8
            
        elif self.current_category == "node":
            embed = discord.Embed(
                title=f"{EMOJI_HELP} {BOT_NAME} Help - {EMOJI_GLOBAL} Node Management",
                description="Connect and manage VPS across remote nodes",
                color=color
            )
            commands = [
                f"**`{PREFIX}connect-vps <ip:port> <api-key> [name]`** - Connect a node (Admin)",
                f"**`{PREFIX}node-list --hide`** - List all connected nodes",
                f"**`{PREFIX}node-creds`** - Show node endpoints + API keys (Admin)",
                f"**`{PREFIX}node-info <node-name>`** - Full node details",
                f"**`{PREFIX}node-health <node-name>`** - Quick node health check",
                f"**`{PREFIX}remove-node <node-name>`** - Disconnect a node (Admin)",
                f"**`{PREFIX}restart-node <node-name>`** - Restart a node (Admin)",
                f"**`{PREFIX}restart-bot`** - Restart bot service (Admin)"
            ]
            total = 8
            
        elif self.current_category == "ports":
            embed = discord.Embed(
                title=f"{EMOJI_HELP} {BOT_NAME} Help - {EMOJI_PORTS} Port Forwarding",
                description="Manage port forwarding for your VPS",
                color=color
            )
            commands = [
                f"**`{PREFIX}ports add <vps-id> <vps_port>`** - Add port forward",
                f"**`{PREFIX}ports list [vps-id]`** - List port forwards",
                f"**`{PREFIX}ports remove <host_port>`** - Remove port forward",
            ]
            total = 3
            
        elif self.current_category == "bot_system":
            embed = discord.Embed(
                title=f"{EMOJI_HELP} {BOT_NAME} Help - {EMOJI_BOT} Bot System Commands",
                description="Bot economy and statistics commands",
                color=color
            )
            commands = [
                f"**`{PREFIX}plans`** - View free VPS plans",
                f"**`{PREFIX}stats`** - View your invite/boost stats",
                f"**`{PREFIX}addinv @user <amount>`** - Add invites (Admin)",
                f"**`{PREFIX}removeinv @user <amount>`** - Remove invites (Admin)",
                f"**`{PREFIX}addboost @user <amount>`** - Add boosts (Admin)",
                f"**`{PREFIX}removeboost @user <amount>`** - Remove boosts (Admin)",
                f"**`{PREFIX}user-stats @user`** - View user stats (Admin)"
            ]
            total = 7
            
        elif self.current_category == "system":
            embed = discord.Embed(
                title=f"{EMOJI_HELP} {BOT_NAME} Help - {EMOJI_SYSTEM} System Commands",
                description="Bot and system management commands",
                color=color
            )
            commands = [
                f"**`{PREFIX}ping`** - Check bot latency",
                f"**`{PREFIX}uptime <node-name>`** - Show node/bot uptime",
                f"**`{PREFIX}serverstats`** - Server statistics (Admin)",
                f"**`{PREFIX}change-prefix <new-prefix>`** - Change command prefix (Admin)"
            ]
            total = 4
            
        elif self.current_category == "admin":
            embed = discord.Embed(
                title=f"{EMOJI_HELP} {BOT_NAME} Help - {EMOJI_ADMIN} Admin Commands",
                description="Commands for server administrators",
                color=color
            )
            commands = [
                f"**`{PREFIX}create <ram> <cpu> <disk> <time> <up/down> <y/n> @user <node-name>`** - Create VPS (`<y/n>` = enable/disable owner's Ports button; bandwidth e.g. `1kbps/900kbps` — small b = bits, capital B = bytes (`MBps`); flags: `--bypass_cpu`, `--bypass_ram`, `--bypass_disk`, `--bypass_all`)",
                f"**`{PREFIX}change-bw <up/down> <vps-id>`** - Change VPS bandwidth limit",
                f"**`{PREFIX}change-pstate <y/n> <vps-id>`** - Enable/disable a VPS's Ports button",
                f"**`{PREFIX}bw-info`** - Explain bandwidth units",
                f"**`{PREFIX}delete-vps <vps-id>`** - Delete VPS (with confirmation)",
                f"**`{PREFIX}resize <vps-id> <ram> <cpu> <disk>`** - Resize VPS",
                f"**`{PREFIX}suspend-vps <vps-id>`** - Suspend VPS",
                f"**`{PREFIX}unsuspend-vps <vps-id>`** - Unsuspend VPS",
                f"**`{PREFIX}renew-vps <vps-id> <time> [--force]`** - Renew/force-renew VPS timer",
                 f"**`{PREFIX}logs <vps-id> [lines]`** - View VPS logs",
                 f"**`{PREFIX}suspension-logs [container]`** - View suspension logs",
                 f"**`{PREFIX}list-all`** - List all VPS across nodes",
                 f"**`{PREFIX}check-resources <node-name>`** - Node free resources",
                 f"**`{PREFIX}lxc-list <node-name>`** - List containers on a node",
                 f"**`{PREFIX}machine-status <node-name> [seconds]`** - Live node status",
                 f"**`{PREFIX}stop-vps-all <node-name>`** - Stop all VPS on a node",
                f"**`{PREFIX}start-all <node-name>`** - Start all VPS on a node",
                f"**`{PREFIX}userinfo @user`** - User information",
                f"**`{PREFIX}invite-logs [@user]`** - View invite tracking logs",
                f"**`{PREFIX}boost-logs [@user]`** - View boost tracking logs"
            ]
            total = 20

        elif self.current_category == "main_admin":
            embed = discord.Embed(
                title=f"{EMOJI_HELP} {BOT_NAME} Help - {EMOJI_MAIN_ADMIN} Main Admin Commands",
                description="Commands for the main administrator only",
                color=color
            )
            commands = [
                f"**`{PREFIX}admin-add @user`** - Add admin",
                f"**`{PREFIX}admin-remove @user`** - Remove admin",
                f"**`{PREFIX}admin-list`** - List admins",
                f"**`{PREFIX}maintenance <on/off>`** - Maintenance mode",
                f"**`{PREFIX}set-status <p/s/l/w/c> <name>`** - Set bot status",
                f"**`{PREFIX}change-mode <online/idle/dnd/invis>`** - Change bot mode",
                f"**`{PREFIX}purge-prot <vps-id>`** - Protect VPS from purge",
                f"**`{PREFIX}purge-remove-prot <vps-id>`** - Remove purge protection",
                f"**`{PREFIX}purge-status <vps-id>`** - View a VPS's purge protection status",
                f"**`{PREFIX}purge-list-prot <node-name>`** - List protected VPS on a node",
                f"**`{PREFIX}purge-list-unprot <node-name>`** - List unprotected VPS on a node",
                f"**`{PREFIX}purge-vm-all <node-name>`** - Purge ALL unprotected VPS on a node (1 by 1)"
            ]
            total = 12
            
        else:
            embed = discord.Embed(
                title=f"{EMOJI_HELP} {BOT_NAME} Help",
                description="Select a category from the dropdown",
                color=color
            )
            commands = []
            total = 0
        
        # Set thumbnail if URL is provided
        if THUMBNAIL_URL:
            embed.set_thumbnail(url=THUMBNAIL_URL)
        
        # Set footer with timestamp and icon
        embed.set_footer(
            text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            icon_url=THUMBNAIL_URL
        )
        
        commands_str = "\n".join(commands) if commands else "No commands available"
        if len(commands_str) > 1024:
            mid = len(commands) // 2
            part1 = "\n".join(commands[:mid])
            part2 = "\n".join(commands[mid:])
            embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Commands (1/2)", value=part1, inline=False)
            embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Commands (2/2)", value=part2, inline=False)
        else:
            embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Commands", value=commands_str, inline=False)
        embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Navigation", 
                       value=f"• Use dropdown to switch categories\n• Total commands: {total}\n• Prefix: `{PREFIX}`", 
                       inline=False)
        
        self.embed = embed

@bot.command(name='help')
@commands.cooldown(1, 3, commands.BucketType.user)
async def help_command(ctx):
    """Show interactive help menu"""
    if not await maintenance_check(ctx):
        return
    
    # Check if user already has an active help menu
    user_id = ctx.author.id
    if user_id in active_help_menus:
        try:
            await active_help_menus[user_id].delete()
        except:
            pass
        del active_help_menus[user_id]
    
    view = HelpView(ctx)
    msg = await ctx.send(embed=view.embed, view=view)
    active_help_menus[user_id] = msg
    
    # Remove from dict when menu expires
    async def remove_from_dict():
        await asyncio.sleep(300)
        if user_id in active_help_menus:
            del active_help_menus[user_id]
    
    asyncio.create_task(remove_from_dict())

# ==================================================== HELP SYSTEM END =====================================================

# ==================================================== DISK USAGE MONITOR BACKGROUND TASK =====================================================

async def _send_disk_full_notice(user_id, vps, usage, total):
    """DM the owner once; fall back to a channel mention if DMs are closed."""
    container = vps['container_name']
    pct = (usage / total * 100) if total > 0 else 100
    embed = create_warning_embed(
        f"{EMOJI_DISK} VPS Storage Full - Action Required",
        f"Your VPS **`{container}`** has reached **100%** of its disk limit and can no longer write data.\n\n"
        f"{EMOJI_WARNING} You must free up space to use your VPS again."
    )
    add_field(embed, "Disk Usage",
        f"{EMOJI_DISK} **Used:** {_format_bytes(usage)} / {_format_bytes(total)} (`{pct:.1f}%`)\n"
        f"{EMOJI_FOLDER} **Remaining:** {_format_bytes(max(0, total - usage))}",
        False)
    add_field(embed, "How to fix",
        f"• Delete large or unneeded files inside your VPS\n"
        f"• Use `{PREFIX}manage` to review your VPS\n"
        f"• Contact an admin if you need a bigger plan",
        False)
    add_field(embed, "What happens now",
        f"{EMOJI_LOCK} Writes to your VPS will **fail** until space is freed. Your existing data is safe.",
        False)

    sent = await safe_dm(str(user_id), embed)
    if not sent:
        # Fallback: ping the user in the log channel with the same notice
        try:
            channel = bot.get_channel(LOGGIN_CHANNEL) if LOGGIN_CHANNEL else None
            if channel is None and LOGGIN_CHANNEL:
                channel = await bot.fetch_channel(LOGGIN_CHANNEL)
            if channel is not None:
                await channel.send(content=f"<@{user_id}>", embed=embed)
                sent = True
        except Exception:
            pass
    return sent

async def check_all_disks_once():
    """Single pass over every running VPS, applying the disk-full notify logic."""
    for user_id, vps_list in list(vps_data.items()):
        for vps in list(vps_list):
            if vps.get('suspended', False) or vps.get('status') != 'running':
                continue
            container = vps.get('container_name')
            if not container:
                continue
            usage, total = await get_container_disk_info(container)
            if total <= 0:
                continue  # no measurable quota on this storage driver

            # If reported usage massively exceeds the reported limit, the storage
            # driver is NOT actually enforcing a quota (e.g. the 'dir' driver
            # reports the host filesystem, not the container's quota). Only warn
            # on genuinely enforced quotas so admins/users are never false-pinged.
            if usage > total * 1.2:
                if vps.get('disk_full_notified', False):
                    vps['disk_full_notified'] = False
                    save_vps_data()
                continue

            pct = (usage / total * 100) if total else 0

            if pct >= 100:
                if not vps.get('disk_full_notified', False):
                    vps['disk_full_notified'] = True
                    save_vps_data()
                    delivered = await _send_disk_full_notice(user_id, vps, usage, total)
                    await send_log(EMOJI_DISK, "VPS Disk Full",
                        f"{EMOJI_VPS} **Container:** `{container}`\n"
                        f"{EMOJI_USER} **User:** <@{user_id}>\n"
                        f"{EMOJI_DISK} **Usage:** {_format_bytes(usage)} / {_format_bytes(total)} (`{pct:.1f}%`)\n"
                        f"{EMOJI_INFO} **Notified:** {'yes' if delivered else 'failed (DMs closed)'}",
                        color=0xff3366)
            elif pct < DISK_FULL_RESET_PERCENT and vps.get('disk_full_notified', False):
                vps['disk_full_notified'] = False
                save_vps_data()

async def monitor_disk_usage():
    """Watch every running VPS and warn its owner exactly once when it hits 100%.

    The 'disk_full_notified' flag is re-armed automatically once usage drops back
    below DISK_FULL_RESET_PERCENT, so the user is pinged again the next time the
    disk fills up.
    """
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            await check_all_disks_once()
        except Exception as e:
            logger.error(f"Error in disk usage monitor: {e}")
        await asyncio.sleep(DISK_MONITOR_INTERVAL)

async def check_all_node_disks_once():
    """Poll every node once for container disk usage and warn owners at 100%.

    One batched request per node (`/disks`) returns every running container's
    root-disk usage/limit, so the bot never does a request per VPS.
    """
    all_vps = node_vps_all()
    by_node = {}
    for vps in all_vps:
        by_node.setdefault(vps.get('node_id'), []).append(vps)

    async def poll(node):
        node_id = node['node_id']
        vps_list = by_node.get(node_id)
        if not vps_list:
            return
        try:
            data = await node_client(node).disks()
        except Exception:
            return
        disks = {d.get('name'): d for d in (data.get('disks') or []) if d.get('name')}

        for vps in vps_list:
            if vps.get('status') != 'running':
                continue
            info = disks.get(vps.get('container_name'))
            if not info:
                continue
            total = int(info.get('total') or 0)
            usage = int(info.get('usage') or 0)
            if total <= 0:
                continue

            # Quota not actually enforced (driver reports host filesystem): skip.
            if usage > total * 1.2:
                if vps.get('disk_full_notified'):
                    node_vps_update(vps['vps_id'], disk_full_notified=0)
                continue

            pct = usage / total * 100
            if pct >= 100:
                if not vps.get('disk_full_notified'):
                    node_vps_update(vps['vps_id'], disk_full_notified=1)
                    delivered = await _send_disk_full_notice(vps['user_id'], vps, usage, total)
                    await send_log(EMOJI_DISK, "VPS Disk Full",
                        f"{EMOJI_VPS} **Container:** `{vps['container_name']}`\n"
                        f"{EMOJI_USER} **User:** <@{vps['user_id']}>\n"
                        f"{EMOJI_DISK} **Usage:** {_format_bytes(usage)} / {_format_bytes(total)} (`{pct:.1f}%`)\n"
                        f"{EMOJI_INFO} **Notified:** {'yes' if delivered else 'failed (DMs closed)'}",
                        color=0xff3366)
            elif pct < DISK_FULL_RESET_PERCENT and vps.get('disk_full_notified'):
                node_vps_update(vps['vps_id'], disk_full_notified=0)

    await asyncio.gather(*(poll(n) for n in node_all()))

async def node_disk_monitor_loop():
    """Watch every running node VPS and warn its owner once when it hits 100%.

    The 'disk_full_notified' flag is re-armed once usage drops below
    DISK_FULL_RESET_PERCENT, so the owner is pinged again on the next fill-up.
    """
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            await check_all_node_disks_once()
        except Exception as e:
            logger.error(f"Error in node disk monitor: {e}")
        await asyncio.sleep(DISK_MONITOR_INTERVAL)

# ==================================================== DISK USAGE MONITOR BACKGROUND TASK END =====================================================

# ==================================================== AUTO-SUSPEND EXPIRED NODE VPS =====================================================

async def check_expired_node_vps():
    """Auto-suspend node VPS whose timer has expired (node-aware).

    Node replacement for the legacy check_expired_vps(): reads the node_vps
    table and freezes each expired container via its node's API, so timers
    actually stop a running VPS and record the suspension.
    """
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            now = datetime.utcnow()
            for vps in node_vps_all():
                if vps.get('timer_status') == 'expired':
                    continue
                expires_at = vps.get('expires_at') or ''
                if not expires_at:
                    continue
                try:
                    expires_dt = datetime.fromisoformat(expires_at)
                except Exception:
                    continue
                if now < expires_dt:
                    continue
                container = vps.get('container_name')
                user_id = vps.get('user_id')
                vps_id = vps.get('vps_id')
                node = node_get(vps.get('node_id'))
                if node:
                    try:
                        await node_client(node).freeze(container)
                    except Exception:
                        pass
                try:
                    hist = json.loads(vps.get('suspension_history') or '[]')
                except Exception:
                    hist = []
                hist.append({'time': datetime.now().isoformat(), 'reason': 'VPS timer expired', 'by': 'System'})
                node_vps_update(vps_id, status='suspended', timer_status='expired',
                                suspended_reason='VPS timer expired',
                                suspension_history=json.dumps(hist))
                log_suspension(container, user_id, 'auto_suspend', 'VPS timer expired', 'System')
                await send_log(EMOJI_UPTIME, "VPS Auto-Suspended",
                    f"{EMOJI_VPS} **Container:** `{container}`\n"
                    f"{EMOJI_USER} **User:** <@{user_id}>\n"
                    f"{EMOJI_INFO} **Reason:** VPS timer expired",
                    color=0xffaa00)
                try:
                    dm_embed = create_warning_embed(
                        f"{EMOJI_UPTIME} VPS Auto-Suspended - Timer Expired",
                        f"Your VPS **`{container}`** has been automatically suspended because its timer expired.\n"
                        f"Your data is **safe** and will be preserved.\n\n"
                        f"{EMOJI_WARNING} **Renew ASAP** to prevent permanent deletion!")
                    add_field(dm_embed, "Auto-Delete Warning",
                        f"This VPS will be **permanently deleted** after `{AUTO_SUSPENDED_VPS_DELETE_TIME}` if not renewed.",
                        False)
                    add_field(dm_embed, "What to do",
                        f"Contact an administrator to renew your VPS immediately.\n"
                        f"Use `{PREFIX}renew-vps {vps_id} 1month` to restore it.",
                        False)
                    await safe_dm(str(user_id), dm_embed)
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Error in node VPS timer check: {e}")
        await asyncio.sleep(30)

# ==================================================== AUTO-SUSPEND EXPIRED NODE VPS END =====================================================

# ==================================================== AUTO-DELETE SUSPENDED NODE VPS =====================================================

async def auto_delete_node_vps():
    """Permanently delete node VPS that stayed suspended past the grace period."""
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            now = datetime.utcnow()
            if not AUTO_SUSPENDED_VPS_DELETE_TIMEDELTA:
                await asyncio.sleep(60)
                continue
            for vps in node_vps_all():
                if not (vps.get('status') == 'suspended' and vps.get('timer_status') == 'expired'):
                    continue
                expires_at = vps.get('expires_at') or ''
                if not expires_at:
                    continue
                try:
                    expires_dt = datetime.fromisoformat(expires_at)
                except Exception:
                    continue
                container = vps.get('container_name')
                user_id = vps.get('user_id')
                vps_id = vps.get('vps_id')
                node = node_get(vps.get('node_id'))
                delete_at = expires_dt + AUTO_SUSPENDED_VPS_DELETE_TIMEDELTA
                if now >= delete_at:
                    if node:
                        try:
                            await node_client(node).delete(container)
                        except Exception:
                            pass
                    conn = get_db()
                    conn.execute('DELETE FROM node_vps WHERE vps_id=?', (int(vps_id),))
                    conn.commit()
                    conn.close()
                    log_suspension(container, user_id, 'auto_delete', 'Auto-deleted after suspension period', 'System')
                    await send_log(EMOJI_CROSS, "VPS Auto-Deleted",
                        f"{EMOJI_VPS} **Container:** `{container}`\n"
                        f"{EMOJI_USER} **User:** <@{user_id}>\n"
                        f"{EMOJI_INFO} **Reason:** Auto-deleted after {format_timedelta(AUTO_SUSPENDED_VPS_DELETE_TIMEDELTA)} suspension period",
                        color=0xff3366)
                    try:
                        dm_embed = create_warning_embed(
                            f"{EMOJI_CROSS} VPS Deleted - Not Renewed",
                            f"Your VPS **`{container}`** has been **permanently deleted** because it was not renewed after the suspension period.\n\n"
                            f"All data on this VPS has been lost.")
                        add_field(dm_embed, "Reason",
                            f"Suspended for {format_timedelta(AUTO_SUSPENDED_VPS_DELETE_TIMEDELTA)} without renewal.\n"
                            f"Contact an admin if you have any questions.", False)
                        await safe_dm(str(user_id), dm_embed)
                    except Exception:
                        pass
                elif AUTO_SUSPENDED_VPS_DELETE_WARN_TIMEDELTA:
                    warn_at = delete_at - AUTO_SUSPENDED_VPS_DELETE_WARN_TIMEDELTA
                    if now >= warn_at and not vps.get('auto_delete_warned'):
                        node_vps_update(vps_id, auto_delete_warned=1)
                        try:
                            remaining = delete_at - now
                            warn_embed = create_warning_embed(
                                f"{EMOJI_WARNING} FINAL WARNING - VPS Scheduled for Deletion",
                                f"Your VPS **`{container}`** is about to be **permanently deleted**!\n\n"
                                f"{EMOJI_WARNING} **Deletion in:** {format_timedelta(remaining)}\n\n"
                                f"**Renew immediately** or all data will be lost.")
                            add_field(warn_embed, "What to do",
                                f"Contact an admin to renew your VPS right now to prevent permanent deletion.\n"
                                f"Use `{PREFIX}renew-vps {vps_id} 1month` to restore it.", False)
                            await safe_dm(str(user_id), warn_embed)
                        except Exception:
                            pass
        except Exception as e:
            logger.error(f"Error in auto-delete node VPS check: {e}")
        await asyncio.sleep(60)

# ==================================================== AUTO-DELETE SUSPENDED NODE VPS END =====================================================

# ==================================================== VPS TIMER BACKGROUND TASK =====================================================

AUTO_SUSPENDED_VPS_DELETE_TIMEDELTA = parse_time_string(AUTO_SUSPENDED_VPS_DELETE_TIME)
AUTO_SUSPENDED_VPS_DELETE_WARN_TIMEDELTA = parse_time_string(AUTO_SUSPENDED_VPS_DELETE_WARN_TIME)

async def check_expired_vps():
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            now = datetime.now()
            for user_id, vps_list in list(vps_data.items()):
                for vps in vps_list:
                    if vps.get('timer_status') != 'running':
                        continue
                    expires_at = vps.get('expires_at', '')
                    if not expires_at:
                        continue
                    expires_dt = datetime.fromisoformat(expires_at)
                    if now >= expires_dt and not vps.get('suspended', False):
                        container = vps['container_name']
                        if vps.get('status') == 'running':
                            try:
                                await execute_lxc(f"lxc stop {shlex.quote(container)}")
                            except:
                                pass
                        vps['status'] = 'stopped'
                        vps['suspended'] = True
                        vps['suspended_reason'] = 'VPS timer expired'
                        vps['timer_status'] = 'expired'
                        if 'suspension_history' not in vps:
                            vps['suspension_history'] = []
                        vps['suspension_history'].append({
                            'time': now.isoformat(),
                            'reason': 'VPS timer expired',
                            'by': 'System'
                        })
                        save_vps_data()
                        log_suspension(container, user_id, 'auto_suspend', 'VPS timer expired', 'System')
                        await send_log(EMOJI_UPTIME, "VPS Auto-Suspended",
                            f"{EMOJI_VPS} **Container:** `{container}`\n"
                            f"{EMOJI_USER} **User:** <@{user_id}>\n"
                            f"{EMOJI_INFO} **Reason:** VPS timer expired",
                            color=0xffaa00)
                        try:
                            user_dm = await bot.fetch_user(int(user_id))
                            remaining_delete = AUTO_SUSPENDED_VPS_DELETE_TIMEDELTA
                            dm_embed = create_warning_embed(f"{EMOJI_UPTIME} VPS Auto-Suspended - Timer Expired",
                                f"Your VPS **`{container}`** has been automatically suspended because its timer expired.\n"
                                f"Your data is **safe** and will be preserved.\n\n"
                                f"{EMOJI_WARNING} **Renew ASAP** to prevent permanent deletion!")
                            add_field(dm_embed, "Auto-Delete Warning",
                                f"This VPS will be **permanently deleted** after `{AUTO_SUSPENDED_VPS_DELETE_TIME}` if not renewed.\n"
                                f"{EMOJI_UPTIME} **Time until delete:** {format_timedelta(remaining_delete)}",
                                False)
                            add_field(dm_embed, "What to do",
                                "Contact an administrator to renew your VPS immediately.\n"
                                f"Use `{PREFIX}renew-vps {container} 1month Renew` to restore it.",
                                False)
                            await user_dm.send(embed=dm_embed)
                        except:
                            pass
        except Exception as e:
            logger.error(f"Error in VPS timer check: {e}")
        await asyncio.sleep(30)

# ==================================================== VPS TIMER BACKGROUND TASK END =====================================================

# ==================================================== AUTO-DELETE SUSPENDED VPS BACKGROUND TASK =====================================================

async def auto_delete_suspended_vps():
    await bot.wait_until_ready()
    while not bot.is_closed():
        try:
            now = datetime.now()
            if not AUTO_SUSPENDED_VPS_DELETE_TIMEDELTA:
                await asyncio.sleep(60)
                continue

            for user_id, vps_list in list(vps_data.items()):
                for vps in vps_list:
                    if not (vps.get('suspended', False) and vps.get('timer_status') == 'expired'):
                        continue
                    expires_at = vps.get('expires_at', '')
                    if not expires_at:
                        continue
                    expires_dt = datetime.fromisoformat(expires_at)
                    delete_at = expires_dt + AUTO_SUSPENDED_VPS_DELETE_TIMEDELTA
                    container = vps['container_name']

                    if now >= delete_at:
                        try:
                            await execute_lxc(f"lxc delete {shlex.quote(container)} --force")
                        except Exception:
                            pass
                        try:
                            conn = get_db()
                            cur = conn.cursor()
                            cur.execute('DELETE FROM port_forwards WHERE vps_container = ?', (container,))
                            cur.execute('DELETE FROM vps WHERE container_name = ?', (container,))
                            conn.commit()
                            conn.close()
                        except Exception:
                            pass
                        if user_id in vps_data:
                            vps_data[user_id] = [v for v in vps_data[user_id] if v['container_name'] != container]
                            if not vps_data[user_id]:
                                del vps_data[user_id]
                        save_vps_data()
                        if vps.get('plan_name', '') != 'Custom':
                            update_user_stats(user_id, claimed_vps_count=-1)
                        try:
                            await stop_ipv4_tunnel(container)
                        except Exception:
                            pass
                        try:
                            await clear_filemanager(container)
                        except Exception:
                            pass
                        log_suspension(container, user_id, 'auto_delete', 'Auto-deleted after suspension period', 'System')
                        await send_log(EMOJI_CROSS, "VPS Auto-Deleted",
                            f"{EMOJI_VPS} **Container:** `{container}`\n"
                            f"{EMOJI_USER} **User:** <@{user_id}>\n"
                            f"{EMOJI_INFO} **Reason:** Auto-deleted after {format_timedelta(AUTO_SUSPENDED_VPS_DELETE_TIMEDELTA)} suspension period",
                            color=0xff3366)
                        try:
                            user_obj = await bot.fetch_user(int(user_id))
                            dm_embed = create_warning_embed(
                                f"{EMOJI_CROSS} VPS Deleted - Not Renewed",
                                f"Your VPS **`{container}`** has been **permanently deleted** because it was not renewed after the suspension period.\n\n"
                                f"All data on this VPS has been lost."
                            )
                            add_field(dm_embed, "Reason",
                                f"Suspended for {format_timedelta(AUTO_SUSPENDED_VPS_DELETE_TIMEDELTA)} without renewal.\n"
                                f"Contact an admin if you have any questions.",
                                False)
                            await user_obj.send(embed=dm_embed)
                        except (discord.Forbidden, discord.HTTPException, Exception):
                            pass
                    elif AUTO_SUSPENDED_VPS_DELETE_WARN_TIMEDELTA:
                        warn_at = delete_at - AUTO_SUSPENDED_VPS_DELETE_WARN_TIMEDELTA
                        if now >= warn_at and not vps.get('auto_delete_warned', False):
                            vps['auto_delete_warned'] = True
                            save_vps_data()
                            try:
                                user_obj = await bot.fetch_user(int(user_id))
                                remaining = delete_at - now
                                warn_embed = create_warning_embed(
                                    f"{EMOJI_WARNING} FINAL WARNING - VPS Scheduled for Deletion",
                                    f"Your VPS **`{container}`** is about to be **permanently deleted**!\n\n"
                                    f"{EMOJI_WARNING} **Deletion in:** {format_timedelta(remaining)}\n"
                                    f"{EMOJI_UPTIME} **Warning period:** `{AUTO_SUSPENDED_VPS_DELETE_WARN_TIME}`\n\n"
                                    f"**Renew immediately** or all data will be lost."
                                )
                                add_field(warn_embed, "What to do",
                                    "Contact an admin to renew your VPS right now to prevent permanent deletion.\n"
                                    f"Use `{PREFIX}renew-vps {container} 1month Renew` to restore it.",
                                    False)
                                await user_obj.send(embed=warn_embed)
                            except (discord.Forbidden, discord.HTTPException, Exception):
                                pass
        except Exception as e:
            logger.error(f"Error in auto-delete suspended VPS check: {e}")
        await asyncio.sleep(60)

# ==================================================== AUTO-DELETE SUSPENDED VPS BACKGROUND TASK END =====================================================

# ==================================================== NETWORK AND CONTAINER STARTUP HELPERS =====================================================

LXD_BRIDGE = "lxdbr0"
LXD_BRIDGE_IP = "10.111.49.1"
LXD_BRIDGE_NET = "10.111.49.0/24"
DNSMASQ_PID_FILE = "/run/dnsmasq-lxdbr0.pid"
DNSMASQ_LOG_FILE = "/var/log/dnsmasq-lxdbr0.log"

async def _bridge_exists(name):
    try:
        proc = await asyncio.create_subprocess_exec(
            "ip", "link", "show", name,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        return proc.returncode == 0
    except Exception:
        return False

async def _lxd_network_exists(name):
    try:
        proc = await asyncio.create_subprocess_exec(
            "lxc", "network", "show", name,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        return proc.returncode == 0
    except Exception:
        return False

async def _ensure_dnsmasq(subnet_ip=None, net=None):
    """Fallback DHCP/DNS server for an UNMANAGED bridge only.

    LXD-managed bridges already run their own dnsmasq; starting a second one
    causes competing DHCP leases and intermittent 'no internet'.
    """
    if subnet_ip is None:
        subnet_ip = LXD_BRIDGE_IP
    try:
        proc = await asyncio.create_subprocess_exec(
            "cat", DNSMASQ_PID_FILE,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        if proc.returncode == 0:
            pid = stdout.decode().strip()
            proc = await asyncio.create_subprocess_exec(
                "kill", "-0", pid,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            if proc.returncode == 0:
                return
    except Exception:
        pass

    try:
        proc = await asyncio.create_subprocess_exec(
            "dnsmasq",
            f"--interface={LXD_BRIDGE}",
            f"--dhcp-range={subnet_ip[:-1]}2,{subnet_ip[:-1]}254,1h",
            f"--dhcp-option=3,{subnet_ip}",
            "--dhcp-option=6,8.8.8.8,1.1.1.1",
            "--bind-interfaces",
            f"--log-facility={DNSMASQ_LOG_FILE}",
            f"--pid-file={DNSMASQ_PID_FILE}",
            "--conf-file=/dev/null",
            "-u", "root",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"Failed to start dnsmasq on {LXD_BRIDGE}: {e}")

async def ensure_lxdbr0():
    """Make sure lxdbr0 exists as an LXD-managed bridge with NAT + DHCP.

    Previously this added a *second* subnet (10.111.49.1/24) to the bridge and
    started a competing dnsmasq even when LXD already managed it, which caused
    flaky DHCP/DNS and the 'No Internet' reports. Now we only fall back to a
    manual bridge + dnsmasq when LXD itself cannot manage the network.
    """
    managed = await _lxd_network_exists(LXD_BRIDGE)

    if not managed:
        logger.info(f"{LXD_BRIDGE} is not LXD-managed, creating via LXD...")
        proc = await asyncio.create_subprocess_exec(
            "lxc", "network", "create", LXD_BRIDGE, "--type=bridge",
            "ipv4.address=10.111.49.1/24", "ipv4.nat=true", "ipv4.dhcp=true",
            "ipv6.address=none",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        managed = proc.returncode == 0

        if not managed and await _bridge_exists(LXD_BRIDGE):
            # A non-managed bridge with the same name blocks LXD. If nothing is
            # running on it, remove it and let LXD recreate a proper bridge.
            logger.warning(f"{LXD_BRIDGE} exists but is not managed by LXD — reclaiming")
            try:
                proc = await asyncio.create_subprocess_exec(
                    "lxc", "list", "--format", "csv", "-c", "ns",
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                out, _ = await proc.communicate()
                running = [l for l in out.decode().splitlines() if "RUNNING" in l]
            except Exception:
                running = ["unknown"]
            if not running:
                await _run_host_shell(f"ip link set {LXD_BRIDGE} down 2>/dev/null; ip link del {LXD_BRIDGE} 2>/dev/null || true")
                proc = await asyncio.create_subprocess_exec(
                    "lxc", "network", "create", LXD_BRIDGE, "--type=bridge",
                    "ipv4.address=10.111.49.1/24", "ipv4.nat=true", "ipv4.dhcp=true",
                    "ipv6.address=none",
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                await proc.communicate()
                managed = proc.returncode == 0

        if not managed:
            logger.warning("LXD could not manage lxdbr0 — falling back to manual bridge + dnsmasq")
            for _ in range(3):
                if await _bridge_exists(LXD_BRIDGE):
                    break
                await _run_host_shell(f"ip link add {LXD_BRIDGE} type bridge 2>/dev/null || true")
                await asyncio.sleep(1)
            await _run_host_shell(f"ip addr add {LXD_BRIDGE_IP}/24 dev {LXD_BRIDGE} 2>/dev/null || true")
            await _ensure_dnsmasq(LXD_BRIDGE_IP, LXD_BRIDGE_NET)

        await asyncio.sleep(2)
        managed = await _lxd_network_exists(LXD_BRIDGE)

    await _run_host_shell(f"ip link set {LXD_BRIDGE} up 2>/dev/null || true")

    if managed:
        # Keep LXD's own NAT/DHCP enabled; do NOT add extra IPs or dnsmasq.
        await _run_host_shell(
            "lxc network set lxdbr0 ipv4.nat=true 2>/dev/null; "
            "lxc network set lxdbr0 ipv4.dhcp=true 2>/dev/null"
        )

    await _host_nat_fix()
    logger.info(f"{LXD_BRIDGE} bridge verified (managed={managed})")

async def sync_container_states():
    logger.info("Syncing container states...")
    try:
        proc = await asyncio.create_subprocess_exec(
            "lxc", "list", "--format", "json",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=30)
        containers = json.loads(stdout)
        container_map = {}
        for c in containers:
            container_map[c["name"]] = c["status"].lower()

        started = 0
        for user_id, vps_list in list(vps_data.items()):
            for vps in vps_list:
                name = vps["container_name"]
                db_status = vps.get("status", "stopped")
                actual_status = container_map.get(name)
                
                if actual_status is None:
                    logger.warning(f"Container {name} exists in DB but not in LXC - removing from DB and memory")
                    conn = get_db()
                    cur = conn.cursor()
                    cur.execute('DELETE FROM vps WHERE container_name = ?', (name,))
                    cur.execute('DELETE FROM port_forwards WHERE vps_container = ?', (name,))
                    conn.commit()
                    conn.close()
                    vps_data[user_id] = [v for v in vps_data[user_id] if v['container_name'] != name]
                    if not vps_data[user_id]:
                        del vps_data[user_id]
                    continue

                if db_status == "running" and actual_status != "running" and not vps.get("suspended", False) and vps.get("timer_status") != "expired":
                    logger.info(f"Starting {name} (DB=running, LXC={actual_status})")
                    try:
                        proc = await asyncio.create_subprocess_exec(
                            "lxc", "start", name,
                            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                        )
                        await asyncio.wait_for(proc.communicate(), timeout=30)
                        started += 1
                    except Exception as e:
                        logger.error(f"Failed to start {name}: {e}")
                
                elif actual_status == "stopped" and db_status != "stopped":
                    vps["status"] = actual_status
                elif actual_status == "running" and db_status != "running":
                    vps["status"] = actual_status
                    if not vps.get("suspended", False) and vps.get("timer_status") != "expired":
                        vps["suspended"] = False

        save_vps_data()
        logger.info(f"Container state sync complete. Started {started} containers.")
    except Exception as e:
        logger.error(f"Failed to sync container states: {e}")

# ==================================================== NETWORK AND CONTAINER STARTUP HELPERS END =====================================================

# ==================================================== RUN THE BOT =====================================================

async def on_bot_startup():
    _Console.header("BOT STARTUP SEQUENCE")
    _Console.step("Phase 1/3: Emoji Management")
    await ensure_emojis_on_startup()
    _Console.step("Phase 2/3: Fetching Emoji IDs")
    try:
        await fetch_emoji_ids()
        _Console.ok("Emoji IDs loaded")
    except Exception as e:
        _Console.fail(f"Failed to fetch emoji IDs: {e}")
    _Console.step("Phase 3/3: Node-only mode")
    try:
        _Console.ok(f"Loaded {len(node_all())} connected node(s)")
    except Exception as e:
        _Console.warn(f"Could not read nodes: {e}")
    _console_free = free_vps_node()
    if FREE_VPS_STATUS.lower() in ('yes', 'true', '1'):
        if _console_free:
            _Console.ok(f"Free VPS enabled -> node {FREE_VPS_NODE[0]}")
        else:
            _Console.warn("Free VPS is ENABLED but FREE_VPS_NODE is not configured — claimfree will refuse until set.")
    _Console.header("BOT READY — CONNECTING TO DISCORD")
bot.setup_hook = on_bot_startup

if __name__ == "__main__":
    if DISCORD_TOKEN and DISCORD_TOKEN != 'BOT_TOKEN_HERE':
        bot.run(DISCORD_TOKEN)
    else:
        logger.error("No Discord token found. Please set DISCORD_TOKEN in the configuration.")

# ==================================================== RUN THE BOT END =====================================================
