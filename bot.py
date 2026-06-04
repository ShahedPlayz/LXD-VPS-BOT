# ╔══════════════════════════════════════════════════════════════════════════╗
# ║         MagnexHostSYS — Ultimate VPS Bot v6.1 (FIXED)                    ║
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
# ==================================================== IMPORTS END ===================================================== 

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

# Discord Bot Settings
DISCORD_TOKEN = 'BOT_TOKEN_HERE'  # Your bot token here
BOT_NAME = 'BOT_NAME_HERE'  # Bot name
PREFIX = 'BOT_PREFIX_HERE'  # Command prefix
MAIN_ADMIN_IDS = [ #===== MAIN ADMINS ======
                  '1340495739293274215',  
                  '1166200288030502933'
                 ]
# Role system removed - VPS user status tracked via database
DEFAULT_STORAGE_POOL = 'default'  # LXC storage pool name
YOUR_SERVER_IP = 'YOUR_SERVER_IP_HERE'  # Your server IP for port forwarding
AUTO_SUSPENDED_VPS_DELETE_TIME = '7d' # Time after which suspended VPS will be automatically deleted (e.g., '7d' for 7 days, '12h' for 12 hours)
AUTO_SUSPENDED_VPS_DELETE_WARN_TIME = '1h' # Time before deletion to warn users about their suspended VPS being deleted (e.g., '1h' for 1 hour, '30m' for 30 minutes)
FREE_PLANS_MAX_VPS = '3'  # Max VPS allowed for free plans use 0 for unlimited
PAID_PLANS_MAX_VPS = '5'  # Max VPS allowed for paid plans use 0 for unlimited
# Thumbnail URL (icon in top right and footer)
THUMBNAIL_URL = "URL_HERE" # SET HERE THUMBNAIL 
LOGGIN_CHANNEL = 0000000000 # Channel ID for logging important actions (suspensions, deletions, etc.)
TRACKING_CHANNEL = 0000000000 # Channel ID for tracking invite/boost activity

# Free VPS Plans based on invites/boosts
FREE_VPS_STATUS = 'No' # 'Yes' if you want to enable, 'No' If you want to disable 
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
    logger.error("LXC command not found. Please ensure LXC is installed.")
    raise SystemExit("LXC command not found. Please ensure LXC is installed.")

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
    for admin_id in MAIN_ADMIN_IDS:
        cur.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (str(admin_id),))
    
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
    
    # Initialize settings
    settings_init = [
        ('cpu_threshold', '90'),
        ('ram_threshold', '90'),
        ('maintenance_mode', 'false'),
        ('maintenance_started_by', ''),
        ('maintenance_started_at', ''),
        ('bot_version', '4.1.0'),
        ('bot_status', 'online'),
        ('bot_activity', 'watching'),
        ('bot_activity_name', f'{BOT_NAME} VPS Manager')
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
        data[user_id].append(vps)
    return data

def get_admins() -> List[str]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT user_id FROM admins')
    rows = cur.fetchall()
    conn.close()
    return [row['user_id'] for row in rows]

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
                
                if 'id' not in vps or vps['id'] is None:
                    cur.execute('''INSERT INTO vps (user_id, container_name, plan_name, ram, cpu, storage, config, os_version, status, suspended, whitelisted, purge_protected, suspended_reason, created_at, shared_with, suspension_history, expires_at, timer_paused_at, timer_status, auto_delete_warned)
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                (user_id, vps['container_name'], plan_name, vps['ram'], vps['cpu'], vps['storage'], vps['config'],
                                 os_ver, vps['status'], suspended_int, whitelisted_int, purge_protected_int, suspended_reason,
                                 created_at, shared_json, history_json, expires_at, timer_paused_at, timer_status, auto_delete_warned))
                    vps['id'] = cur.lastrowid
                else:
                    cur.execute('''UPDATE vps SET user_id = ?, plan_name = ?, ram = ?, cpu = ?, storage = ?, config = ?, os_version = ?, status = ?, suspended = ?, whitelisted = ?, purge_protected = ?, suspended_reason = ?, shared_with = ?, suspension_history = ?, expires_at = ?, timer_paused_at = ?, timer_status = ?, auto_delete_warned = ?
                                   WHERE id = ?''',
                                (user_id, plan_name, vps['ram'], vps['cpu'], vps['storage'], vps['config'],
                                 os_ver, vps['status'], suspended_int, whitelisted_int, purge_protected_int, suspended_reason,
                                 shared_json, history_json, expires_at, timer_paused_at, timer_status, auto_delete_warned, vps['id']))
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
CPU_THRESHOLD = int(get_setting('cpu_threshold', 90))
RAM_THRESHOLD = int(get_setting('ram_threshold', 90))
MAINTENANCE_MODE = get_setting('maintenance_mode', 'false').lower() == 'true'
MAINTENANCE_STARTED_BY = get_setting('maintenance_started_by', '')
MAINTENANCE_STARTED_AT = get_setting('maintenance_started_at', '')
BOT_STATUS = get_setting('bot_status', 'online')
BOT_ACTIVITY = get_setting('bot_activity', 'watching')
BOT_ACTIVITY_NAME = get_setting('bot_activity_name', f'{BOT_NAME} VPS Manager')

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

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

def create_ping_embed(ws_latency, db_latency):
    """Create the ping embed"""
    embed = discord.Embed(
        title=f"{EMOJI_STATS} System Latency Report",
        color=0x00ccff
    )
    
    # Websocket and Database latency
    latency_info = f"**Websocket**\n`{ws_latency:.2f}ms`"
    db_info = f"**Database**\n`{db_latency:.2f}ms`"
    
    embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Connection", value=latency_info, inline=True)
    embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Database", value=db_info, inline=True)
    
    # Status
    status = f"{EMOJI_GOOD_SIGNAL} All systems normal" if ws_latency < 100 else f"{EMOJI_MID_SIGNAL} Elevated latency" if ws_latency < 200 else f"{EMOJI_BAD_SIGNAL} High latency"
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
                allocated_cpu += int(vps['cpu'])
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
                allocated_ram_gb += int(vps['ram'].replace('GB', '').strip())
            except:
                pass
    
    result['ram'] = {
        'total_gb': total_ram_gb,
        'allocated_gb': allocated_ram_gb,
        'available_gb': max(0, total_ram_gb - allocated_ram_gb)
    }
    
    total_disk_gb = 0
    used_disk_gb = 0
    avail_disk_gb = 0
    try:
        usage = shutil.disk_usage('/')
        total_disk_gb = usage.total // (1024**3)
        used_disk_gb = usage.used // (1024**3)
        avail_disk_gb = usage.free // (1024**3)
    except:
        pass
    
    allocated_disk_gb = 0
    for uid, vps_list in vps_data.items():
        for vps in vps_list:
            try:
                allocated_disk_gb += int(vps['storage'].replace('GB', '').strip())
            except:
                pass

    result['disk'] = {
        'total_gb': total_disk_gb,
        'used_gb': used_disk_gb,
        'available_gb': avail_disk_gb,
        'allocated_gb': allocated_disk_gb
    }
    
    return result


async def check_resources(ram_gb, cpu_cores, disk_gb, bypass_cpu=False, bypass_ram=False, bypass_disk=False):
    resources = await get_available_resources()
    
    issues = []
    
    if not bypass_cpu and cpu_cores > resources['cpu']['available']:
        issues.append(
            f"{EMOJI_CPU} **CPU:** Requested {cpu_cores} cores, only {resources['cpu']['available']} available "
            f"(Total: {resources['cpu']['total']}, Used: {resources['cpu']['allocated']})"
        )
    
    if not bypass_ram and ram_gb > resources['ram']['available_gb']:
        issues.append(
            f"{EMOJI_RAM} **RAM:** Requested {ram_gb}GB, only {resources['ram']['available_gb']}GB available "
            f"(Total: {resources['ram']['total_gb']}GB, Used: {resources['ram']['allocated_gb']}GB)"
        )
    
    disk_available_gb = resources['disk']['total_gb'] - resources['disk']['allocated_gb']
    if not bypass_disk and disk_gb > disk_available_gb:
        issues.append(
            f"{EMOJI_DISK} **Disk:** Requested {disk_gb}GB, only {disk_available_gb}GB available "
            f"(Total: {resources['disk']['total_gb']}GB, Allocated: {resources['disk']['allocated_gb']}GB)"
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
            "which dhclient 2>/dev/null || apt-get install -y isc-dhcp-client 2>/dev/null || true",
            "grep -q 'dhclient eth0' /etc/rc.local 2>/dev/null || echo -e '#!/bin/bash\\ndhclient eth0 -r 2>/dev/null; dhclient eth0 2>/dev/null\\nexit 0' > /etc/rc.local && chmod +x /etc/rc.local 2>/dev/null || true"
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

async def check_container_internet(container_name):
    try:
        await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- curl -sS --connect-timeout 10 https://github.com -o /dev/null --max-time 15", timeout=25)
        return True
    except Exception:
        try:
            await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- curl -sS --connect-timeout 10 https://google.com -o /dev/null --max-time 15", timeout=25)
            return True
        except Exception:
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

        for rule_cmd in [
            f"iptables -t nat -C POSTROUTING -s 10.111.49.0/24 ! -d 10.111.49.0/24 -j MASQUERADE 2>/dev/null",
            f"iptables -t nat -A POSTROUTING -s 10.111.49.0/24 ! -d 10.111.49.0/24 -j MASQUERADE 2>/dev/null",
        ]:
            try:
                await execute_lxc(rule_cmd, timeout=10)
            except Exception:
                pass

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

        try:
            await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- bash -c \"dhclient eth0 -r 2>/dev/null; dhclient eth0 2>/dev/null\"", timeout=15)
        except Exception:
            pass
        try:
            await execute_lxc(f"lxc exec {shlex.quote(container_name)} -- bash -c \"ip link set eth0 down; ip link set eth0 up\"", timeout=10)
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

async def get_container_disk(container_name):
    try:
        proc = await asyncio.create_subprocess_exec(
            "lxc", "exec", container_name, "--", "df", "-h", "/",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        lines = stdout.decode().splitlines()
        for line in lines:
            if '/dev/' in line and ' /' in line:
                parts = line.split()
                if len(parts) >= 5:
                    used = parts[2]
                    size = parts[1]
                    perc = parts[4]
                    return f"{used}/{size} ({perc})"
        return "Unknown"
    except Exception:
        return "N/A"

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
            disk_parts = lines[2].split()
            if len(disk_parts) >= 5:
                disk_str = f"{disk_parts[2]}/{disk_parts[1]} ({disk_parts[4]})"

        if len(lines) > 3:
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
    
    if MAINTENANCE_MODE:
        await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="🔧 Maintenance Mode"))
    else:
        activity_types = {
            'playing': discord.ActivityType.playing,
            'watching': discord.ActivityType.watching,
            'listening': discord.ActivityType.listening,
        }
        
        status_types = {
            'online': discord.Status.online,
            'idle': discord.Status.idle,
            'dnd': discord.Status.dnd,
        }
        
        activity_type = activity_types.get(BOT_ACTIVITY, discord.ActivityType.watching)
        status = status_types.get(BOT_STATUS, discord.Status.online)
        
        await bot.change_presence(
            status=status,
            activity=discord.Activity(type=activity_type, name=BOT_ACTIVITY_NAME)
        )
    
    # Cache invites for all guilds to prevent race condition on member join
    for guild in bot.guilds:
        await cache_invites(guild)

    logger.info(f"{BOT_NAME} Bot is ready!")

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
        for code, after_inv in invites_after_dict.items():
            before_inv = cached.get(code)
            if before_inv and after_inv.uses > before_inv.uses:
                inviter_id = str(after_inv.inviter.id) if after_inv.inviter else None
                used_code = code
                break
        if not inviter_id:
            for code, after_inv in invites_after_dict.items():
                if code not in cached:
                    inviter_id = str(after_inv.inviter.id) if after_inv.inviter else None
                    used_code = code
                    break
        if not inviter_id:
            try:
                vanity = await guild.vanity_invite()
                if vanity and vanity.code in invites_after_dict:
                    inviter_id = 'vanity'
                    used_code = vanity.code
            except:
                pass
        _invite_cache[guild.id] = invites_after_dict
        if inviter_id and inviter_id != 'vanity':
            conn = get_db()
            try:
                cur = conn.cursor()
                cur.execute('''INSERT INTO invite_logs (code, inviter_id, user_id, user_name, action, created_at)
                               VALUES (?, ?, ?, ?, ?, ?)''',
                            (used_code, inviter_id, str(member.id), member.name, 'joined', datetime.now().isoformat()))
                conn.commit()
            finally:
                conn.close()
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
            conn = get_db()
            try:
                cur = conn.cursor()
                cur.execute('''INSERT INTO invite_logs (code, inviter_id, user_id, user_name, action, created_at)
                               VALUES (?, ?, ?, ?, ?, ?)''',
                            (used_code or 'unknown', 'unknown', str(member.id), member.name, 'joined', datetime.now().isoformat()))
                conn.commit()
            finally:
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

@bot.event
async def on_member_update(before, after):
    if before.premium_since != after.premium_since:
        conn = get_db()
        conn_closed = False
        try:
            cur = conn.cursor()
            if after.premium_since and not before.premium_since:
                cur.execute('''INSERT INTO boost_logs (user_id, user_name, action, created_at)
                               VALUES (?, ?, ?, ?)''',
                            (str(after.id), after.name, 'boosted', datetime.now().isoformat()))
                conn.commit()
                conn.close()
                conn_closed = True
                update_user_stats(str(after.id), boosts=1)
                await send_log(EMOJI_STAR, "Server Boosted!",
                    f"{EMOJI_USER} **User:** {after.mention} (`{after.id}`)\n"
                    f"{EMOJI_ARROW_RIGHT} **Action:** Started boosting!",
                    color=0xff73fa)
                await send_tracking(EMOJI_STAR, "Server Boosted!",
                    f"{EMOJI_USER} **User:** {after.mention} (`{after.id}`)\n"
                    f"{EMOJI_ARROW_RIGHT} **Action:** Started boosting!",
                    color=0xff73fa)
            elif before.premium_since and not after.premium_since:
                cur.execute('''INSERT INTO boost_logs (user_id, user_name, action, created_at)
                               VALUES (?, ?, ?, ?)''',
                            (str(after.id), after.name, 'unboosted', datetime.now().isoformat()))
                conn.commit()
                conn.close()
                conn_closed = True
                stats = get_user_stats(str(after.id))
                current_boosts = stats.get('boosts', 0)
                if current_boosts > 0:
                    update_user_stats(str(after.id), boosts=-1)
                await send_log(EMOJI_CROSS, "Boost Removed",
                    f"{EMOJI_USER} **User:** {after.mention} (`{after.id}`)\n"
                    f"{EMOJI_ARROW_RIGHT} **Action:** Stopped boosting!",
                    color=0xff3366)
                await send_tracking(EMOJI_CROSS, "Boost Removed",
                    f"{EMOJI_USER} **User:** {after.mention} (`{after.id}`)\n"
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
async def ping(ctx):
    """Check bot latency with detailed report"""
    if not await maintenance_check(ctx):
        return
    
    # Measure websocket latency
    ws_latency = bot.latency * 1000
    
    # Measure database latency
    start_time = time.time()
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT 1')
    cur.fetchone()
    conn.close()
    db_latency = (time.time() - start_time) * 1000
    
    embed = create_ping_embed(ws_latency, db_latency)
    await ctx.send(embed=embed)

@bot.command(name='uptime')
@commands.cooldown(1, 5, commands.BucketType.user)
async def uptime(ctx):
    """Show host uptime"""
    if not await maintenance_check(ctx):
        return
    
    up = await get_uptime()
    embed = create_info_embed("Host Uptime", f"```\n{up}\n```")
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
async def user_stats(ctx):
    """View your invite and boost stats"""
    if not await maintenance_check(ctx):
        return
    
    user_id = str(ctx.author.id)
    stats = get_user_stats(user_id)
    
    embed = create_info_embed(f"📊 {ctx.author.name}'s Stats", f"Your current statistics")
    
    add_field(embed, "📨 Invites", str(stats.get('invites', 0)), True)
    add_field(embed, "🚀 Boosts", str(stats.get('boosts', 0)), True)
    add_field(embed, "🖥️ VPS Owned", str(len(vps_data.get(user_id, []))), True)
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
    if user_id in vps_data and len(vps_data[user_id]) > 0:
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
    
    # Check resources before showing OS selection
    msg = await ctx.send(embed=create_info_embed("Checking Resources", f"{EMOJI_LOADING} Verifying available resources..."))
    can_create, error_msg = await check_resources(selected_plan['ram'], selected_plan['cpu'], selected_plan['disk'])
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
        
        can_create, error_msg = await check_resources(self.plan['ram'], self.plan['cpu'], self.plan['disk'])
        if not can_create:
            await interaction.edit_original_response(
                embed=create_error_embed("Insufficient Resources", error_msg), view=None)
            return
        
        creating_embed = create_info_embed("Creating VPS", f"{EMOJI_LOADING} Deploying {self.selected_os} VPS for {self.ctx.author.mention}...")
        await interaction.edit_original_response(embed=creating_embed, view=None)
        
        if user_id not in vps_data:
            vps_data[user_id] = []
        
        existing_nums = [get_vps_number(v['container_name']) for v in vps_data.get(user_id, [])]
        existing_nums = [n for n in existing_nums if n is not None]
        vps_count = max(existing_nums) + 1 if existing_nums else 1
        container_name = f"{BOT_NAME.lower()}-vps-{user_id}-{vps_count}"
        ram_mb = self.plan['ram'] * 1024
        
        try:
            await ensure_lxdbr0()

            # Create the VPS
            resolved_os = await ensure_image_available(self.selected_os)
            await ensure_container_name_available(container_name)
            await execute_lxc(f"lxc init {resolved_os} {shlex.quote(container_name)} -s {DEFAULT_STORAGE_POOL}", timeout=600)
            await execute_lxc(f"lxc config set {shlex.quote(container_name)} limits.memory {ram_mb}MB")
            await execute_lxc(f"lxc config set {shlex.quote(container_name)} limits.cpu {self.plan['cpu']}")
            await execute_lxc(f"lxc config device set {shlex.quote(container_name)} root size={self.plan['disk']}GB")
            await apply_lxc_config(container_name)
            await execute_lxc(f"lxc start {shlex.quote(container_name)}")
            await apply_internal_permissions(container_name)

            creating_embed.description = f"{EMOJI_GLOBAL} Fixing internet for `{container_name}`..."
            await interaction.edit_original_response(embed=creating_embed)
            progress_msg = await interaction.original_response()
            await fix_container_internet(container_name, msg=progress_msg)

            creating_embed.description = f"{EMOJI_LOADING} Finalizing..."
            await interaction.edit_original_response(embed=creating_embed)
            
            # Deduct the cost
            update_amount = -self.required
            if self.plan_category == 'invites':
                update_user_stats(user_id, invites=update_amount)
            else:  # boosts
                update_user_stats(user_id, boosts=update_amount)
            
            # Update claimed VPS count
            update_user_stats(user_id, claimed_vps_count=1)
            
            # Save VPS info
            plan_time = parse_time_string(self.plan.get('time', ''))
            expires_at = (datetime.now() + plan_time).isoformat() if plan_time else ''
            config_str = f"{self.plan['ram']}GB RAM / {self.plan['cpu']} CPU / {self.plan['disk']}GB Disk"
            vps_info = {
                "container_name": container_name,
                "plan_name": self.plan['name'],
                "ram": f"{self.plan['ram']}GB",
                "cpu": str(self.plan['cpu']),
                "storage": f"{self.plan['disk']}GB",
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
                "timer_status": "running" if expires_at else ""
            }
            vps_data[user_id].append(vps_info)
            save_vps_data()
            
            # Send success embed
            success_embed = create_success_embed("VPS Created Successfully")
            add_field(success_embed, "Owner", self.ctx.author.mention, True)
            add_field(success_embed, "Plan", self.plan['name'], True)
            add_field(success_embed, "Container", f"`{container_name}`", True)
            add_field(success_embed, "Resources", f"**RAM:** {self.plan['ram']}GB\n**CPU:** {self.plan['cpu']} Cores\n**Storage:** {self.plan['disk']}GB", False)
            add_field(success_embed, "OS", f"{get_os_emoji(self.selected_os)} {self.selected_os}", True)
            
            await interaction.followup.send(embed=success_embed)

            timer_display = f"{EMOJI_UPTIME} {format_timedelta(plan_time)}" if plan_time else ""
            await send_log(EMOJI_VPS, "Free VPS Claimed",
                f"{EMOJI_USER} **User:** {self.ctx.author.mention} (`{user_id}`)\n"
                f"{EMOJI_VPS} **Plan:** {self.plan['name']}\n"
                f"{EMOJI_RAM} **RAM:** {self.plan['ram']}GB | {EMOJI_CPU} **CPU:** {self.plan['cpu']} | {EMOJI_DISK} **Disk:** {self.plan['disk']}GB\n"
                f"**Container:** `{container_name}`\n"
                f"{get_os_emoji(self.selected_os)} **OS:** {self.selected_os}\n"
                f"{EMOJI_UPTIME} **Duration:** {timer_display}\n"
                f"{EMOJI_INFO} **Type:** {self.plan_category.title()} ({self.required} required)",
                color=0x00ff88)
            
            # Send DM to user
            try:
                dm_embed = create_success_embed("VPS Created!", f"Your VPS has been successfully created!")
                vps_details = f"**Plan:** {self.plan['name']}\n"
                vps_details += f"**Container Name:** `{container_name}`\n"
                vps_details += f"**Configuration:** {config_str}\n"
                vps_details += f"**Status:** Running\n"
                vps_details += f"**OS:** {get_os_emoji(self.selected_os)} {self.selected_os}\n"
                vps_details += f"**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
                add_field(dm_embed, "VPS Details", vps_details, False)
                add_field(dm_embed, "Management", 
                         f"• Use `{PREFIX}manage` to start/stop your VPS\n• Use `{PREFIX}manage` → SSH for terminal access\n• Use `{PREFIX}ports` for port forwarding", 
                         False)
                
                await self.ctx.author.send(embed=dm_embed)
            except:
                pass  # User has DMs disabled
        
        except Exception as e:
            error_embed = create_error_embed("Creation Failed", f"Error: {str(e)}")
            await interaction.followup.send(embed=error_embed)

@bot.command(name='myvps')
@commands.cooldown(1, 5, commands.BucketType.user)
async def my_vps(ctx):
    """List your VPS"""
    if not await maintenance_check(ctx):
        return
    
    user_id = str(ctx.author.id)
    vps_list = vps_data.get(user_id, [])
    
    if not vps_list:
        await ctx.send(embed=create_no_vps_embed())
        return
    
    embed = create_info_embed("My VPS", f"You have `{len(vps_list)}` VPS")
    
    for i, vps in enumerate(vps_list):
        status = vps.get('status', 'unknown').upper()
        if vps.get('suspended', False):
            status += " (SUSPENDED)"
        
        status_emoji = EMOJI_ONLINE if vps.get('status') == 'running' else EMOJI_OFFLINE if vps.get('status') == 'stopped' else EMOJI_OFFLINE
        vps_num = get_vps_number(vps['container_name']) or (i + 1)
        
        vps_info = f"{status_emoji} **VPS #{vps_num}:** `{vps['container_name']}`\n"
        vps_info += f"• **Status:** {status}\n"
        vps_info += f"• **Plan:** {vps.get('plan_name', 'Custom')}\n"
        vps_info += f"• **Resources:** {vps.get('config', 'Custom')}\n"
        vps_info += get_vps_timer_line(vps) + "\n"
        
        embed.add_field(name="", value=vps_info, inline=False)
    
    add_field(embed, "Management", f"Use `{PREFIX}manage` to control your VPS\nUse `{PREFIX}list` for detailed information", False)
    await ctx.send(embed=embed)

@bot.command(name='list')
@commands.cooldown(1, 5, commands.BucketType.user)
async def list_user_vps(ctx):
    """Detailed VPS list"""
    if not await maintenance_check(ctx):
        return
    
    user_id = str(ctx.author.id)
    vps_list = vps_data.get(user_id, [])
    
    if not vps_list:
        await ctx.send(embed=create_no_vps_embed())
        return
    
    embed = create_info_embed("Your VPS List", f"Showing `{len(vps_list)}` VPS for {ctx.author.mention}")
    
    for i, vps in enumerate(vps_list):
        container_name = vps['container_name']
        vps_num = get_vps_number(container_name) or (i + 1)
        
        status = await get_container_status(container_name)
        cpu_usage = await get_container_cpu(container_name)
        memory_usage = await get_container_memory(container_name)
        disk_usage = await get_container_disk(container_name)
        uptime_info = await get_container_uptime(container_name)
        
        status_emoji = EMOJI_ONLINE if status == 'running' else EMOJI_OFFLINE if status == 'stopped' else EMOJI_OFFLINE
        suspended_text = " (SUSPENDED)" if vps.get('suspended', False) else ""
        purge_text = f"{EMOJI_ADMIN} PROTECTED" if vps.get('purge_protected', False) else ""
        
        vps_info = f"**#{vps_num} | {status_emoji} {status.upper()}{suspended_text}{purge_text}**\n"
        vps_info += f"**Container:** `{container_name}`\n"
        vps_info += f"**Plan:** {vps.get('plan_name', 'Custom')}\n"
        vps_info += f"**Resources:** {vps['ram']} RAM | {vps['cpu']} CPU | {vps['storage']} Storage\n"
        vps_info += f"**OS:** {get_os_emoji(vps.get('os_version', 'ubuntu:22.04'))} {vps.get('os_version', 'ubuntu:22.04')}\n"
        vps_info += f"**Uptime:** {uptime_info}\n"
        vps_info += get_vps_timer_line(vps) + "\n"
        vps_info += f"**CPU Usage:** {cpu_usage}\n"
        vps_info += f"**Memory:** {memory_usage}\n"
        vps_info += f"**Disk:** {disk_usage}\n"
        vps_info += f"**Created:** {vps.get('created_at', 'Unknown')[:10]}\n"
        
        embed.add_field(name=f"VPS #{vps_num}", value=vps_info, inline=False)
    
    await ctx.send(embed=embed)

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
            ram_gb = int(self.vps_data_entry['ram'].replace('GB', ''))
            cpu = int(self.vps_data_entry['cpu'])
            storage_gb = int(self.vps_data_entry['storage'].replace('GB', ''))
            ram_mb = ram_gb * 1024
            
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
            await execute_lxc(f"lxc config set {shlex.quote(self.container_name)} limits.memory {ram_mb}MB")
            await execute_lxc(f"lxc config set {shlex.quote(self.container_name)} limits.cpu {cpu}")
            await execute_lxc(f"lxc config device set {shlex.quote(self.container_name)} root size={storage_gb}GB")
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
            config_str = f"{ram_gb}GB RAM / {cpu} CPU / {storage_gb}GB Disk"
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
            details += f"**Resources:** {ram_gb}GB RAM / {cpu} CPU / {storage_gb}GB Disk"
            
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
    def __init__(self, container_name, owner_id, interaction_user):
        super().__init__(timeout=300)
        self.container_name = container_name
        self.owner_id = owner_id
        self.interaction_user = interaction_user
        self.message = None

    def _status_embed(self, desc, color=0xffaa00):
        is_running = self.container_name in active_ipv4_tunnels
        embed = discord.Embed(
            title=f"{EMOJI_GLOBAL} IPv4 SSH Tunnel — `{self.container_name}`",
            description=desc,
            color=color
        )
        if is_running:
            host, port = _tunnel_connection_info.get(self.container_name, (None, None))
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
        if not await container_exists(self.container_name):
            await interaction.response.send_message(embed=create_error_embed(f"{EMOJI_CROSS} VPS Not Found", f"VPS `{self.container_name}` no longer exists on the host."), ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        progress_msg = await interaction.followup.send(embed=self._status_embed(f"{EMOJI_LOADING} Initializing..."), ephemeral=True, wait=True)
        success, result = await start_ipv4_tunnel(self.container_name, self.owner_id, progress_msg, triggered_by=interaction.user)
        if not success:
            await interaction.edit_original_response(embed=self._status_embed(f"{EMOJI_CROSS} {result}", 0xff3366), view=self)
        else:
            await interaction.edit_original_response(embed=self._status_embed(f"{EMOJI_SUCCESS} Tunnel active", 0x00ff88), view=self)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, emoji=EMOJI_CROSS)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.interaction_user.id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can control this."), ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        await stop_ipv4_tunnel(self.container_name)
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

    def __init__(self, container_name, owner_id, interaction_user, parent_view):
        super().__init__()
        self.container_name = container_name
        self.owner_id = owner_id
        self.interaction_user = interaction_user
        self.parent_view = parent_view

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

        await edit_progress(f"{EMOJI_LOADING} Checking installation...")
        fm_result = await check_install_filemanager(self.container_name)
        if fm_result != "ok":
            await edit_progress(f"{EMOJI_CROSS} **Filebrowser Setup Failed:** {fm_result}", 0xff3366)
            return

        await edit_progress(f"{EMOJI_LOADING} Stopping any running filebrowser...")
        pkill1 = await asyncio.create_subprocess_exec(
            "lxc", "exec", self.container_name, "--", "pkill", "-f", "filebrowser",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await pkill1.wait()
        await asyncio.sleep(1)

        await edit_progress(f"{EMOJI_LOADING} Configuring user...")
        user_result = await configure_filemanager_user(self.container_name, username, password)
        if user_result is not True:
            await edit_progress(f"{EMOJI_CROSS} **User Config Failed:** {user_result}", 0xff3366)
            return

        await edit_progress(
            f"{EMOJI_SUCCESS} Filebrowser installed + user configured\n"
            f"{EMOJI_LOADING} Starting service + tunnel..."
        )

        pkill = await asyncio.create_subprocess_exec(
            "lxc", "exec", self.container_name, "--", "pkill", "-f", "filebrowser",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await pkill.wait()

        sc = await asyncio.create_subprocess_exec(
            "lxc", "exec", self.container_name, "--", "bash", "-c",
            "nohup filebrowser --address=0.0.0.0 --port=8080 --root=/ > /dev/null 2>&1 &",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await sc.wait()
        await asyncio.sleep(2)

        dm_user_id = str(self.interaction_user.id)
        task = asyncio.create_task(run_filemanager_loop(
            self.container_name, self.owner_id, username, password, dm_user_id
        ))
        active_filemanager[self.container_name] = task
        _filemanager_credentials[self.container_name] = {"username": username, "password": password}
        save_fm_tunnel_db(self.container_name, self.owner_id, str(self.interaction_user.id), username, password)

        for _ in range(30):
            if self.container_name in _filemanager_connection_info:
                host, port = _filemanager_connection_info[self.container_name]
                fm_url = f"http://{host}:{port}"
                await edit_progress(
                    f"{EMOJI_SUCCESS} **Tunnel:** Connected!\n"
                    f"{EMOJI_FOLDER} **URL:** {fm_url}\n"
                    f"{EMOJI_USER} **Username:** `{username}`\n"
                    f"{EMOJI_LOCK} **Password:** `{'*' * len(password)}`\n"
                    f"{EMOJI_INFO} Details sent to your DMs",
                    0x00ff88
                )
                return
            await asyncio.sleep(1)

        await edit_progress(
            f"{EMOJI_ONLINE} Tunnel started, awaiting pinggy URL\n"
            f"{EMOJI_INFO} You'll receive a DM once connected",
            0x00ccff
        )


class FileManagerView(discord.ui.View):
    def __init__(self, container_name, owner_id, interaction_user):
        super().__init__(timeout=300)
        self.container_name = container_name
        self.owner_id = owner_id
        self.interaction_user = interaction_user

    def _status_embed(self, desc, color=0xffaa00):
        is_running = self.container_name in active_filemanager
        embed = discord.Embed(
            title=f"{EMOJI_FOLDER} File Manager — `{self.container_name}`",
            description=desc,
            color=color
        )
        if is_running:
            info = _filemanager_connection_info.get(self.container_name, None)
            creds = _filemanager_credentials.get(self.container_name, None)
            if info:
                host, port = info
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
        if not await container_exists(self.container_name):
            await interaction.response.send_message(embed=create_error_embed(f"{EMOJI_CROSS} VPS Not Found", f"VPS `{self.container_name}` no longer exists on the host."), ephemeral=True)
            return
        modal = FileManagerModal(self.container_name, self.owner_id, self.interaction_user, self)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Start", style=discord.ButtonStyle.success, emoji=EMOJI_START)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.interaction_user.id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can control this."), ephemeral=True)
            return
        if not await container_exists(self.container_name):
            await interaction.response.send_message(embed=create_error_embed(f"{EMOJI_CROSS} VPS Not Found", f"VPS `{self.container_name}` no longer exists on the host."), ephemeral=True)
            return
        if self.container_name in active_filemanager:
            await interaction.response.send_message(embed=create_warning_embed("Already Running", "File manager is already active."), ephemeral=True)
            return

        check = await asyncio.create_subprocess_exec(
            "lxc", "exec", self.container_name, "--", "which", "filebrowser",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await check.communicate()
        if check.returncode != 0:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"{EMOJI_CROSS} Not Installed",
                    description="Filebrowser is not installed. Use **Config-init** first to install and configure it.",
                    color=0xff3366
                ).set_footer(text=f"{BOT_NAME} | File Manager"),
                ephemeral=True
            )
            return

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

        await edit_progress(f"{EMOJI_LOADING} Starting filebrowser...")
        pkill = await asyncio.create_subprocess_exec(
            "lxc", "exec", self.container_name, "--", "pkill", "-f", "filebrowser",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await pkill.wait()

        sc = await asyncio.create_subprocess_exec(
            "lxc", "exec", self.container_name, "--", "bash", "-c",
            "nohup filebrowser --address=0.0.0.0 --port=8080 --root=/ > /dev/null 2>&1 &",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await sc.wait()
        await asyncio.sleep(2)

        creds = _load_fm_creds(self.container_name)
        if not creds:
            creds = _filemanager_credentials.get(self.container_name)
        username = creds["username"] if creds else "admin"
        password = creds["password"] if creds else "admin"

        await edit_progress(f"{EMOJI_LOADING} Connecting tunnel...")
        dm_user_id = str(self.interaction_user.id)
        task = asyncio.create_task(run_filemanager_loop(
            self.container_name, self.owner_id, username, password, dm_user_id
        ))
        active_filemanager[self.container_name] = task
        save_fm_tunnel_db(self.container_name, self.owner_id, dm_user_id, username, password)

        for _ in range(30):
            if self.container_name in _filemanager_connection_info:
                host, port = _filemanager_connection_info[self.container_name]
                fm_url = f"http://{host}:{port}"
                await edit_progress(
                    f"{EMOJI_SUCCESS} **Tunnel:** Connected!\n"
                    f"{EMOJI_FOLDER} **URL:** {fm_url}\n"
                    f"{EMOJI_USER} **Username:** `{username}`\n"
                    f"{EMOJI_LOCK} **Password:** `{'*' * len(password)}`\n"
                    f"{EMOJI_INFO} Details sent to your DMs",
                    0x00ff88
                )
                return
            await asyncio.sleep(1)

        await edit_progress(
            f"{EMOJI_ONLINE} Tunnel started, awaiting pinggy URL\n"
            f"{EMOJI_INFO} You'll receive a DM once connected",
            0x00ccff
        )

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, emoji=EMOJI_CROSS)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.interaction_user.id:
            await interaction.response.send_message(embed=create_error_embed("Access Denied", "Only the command author can control this."), ephemeral=True)
            return
        await stop_filemanager(self.container_name)
        await interaction.response.edit_message(
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
                    await clear_filemanager(self.parent.container_name)
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
                        f"Container has no internet. Run `{PREFIX}fix-internet`."))
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
                                f"Container has no internet access even after auto-fix.\nRun `{PREFIX}fix-internet` manually."))
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
                        f"Container has no internet. Run `{PREFIX}fix-internet`."))
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

@bot.command(name='manage')
@commands.cooldown(1, 5, commands.BucketType.user)
async def manage_vps(ctx, user: discord.Member = None):
    """Manage your VPS with modern controls"""
    if not await maintenance_check(ctx):
        return
    
    if user:
        user_id_check = str(ctx.author.id)
        if user_id_check not in MAIN_ADMIN_IDS and user_id_check not in admin_data.get("admins", []):
            await ctx.send(embed=create_error_embed("Access Denied", "Only admins can manage other users' VPS."))
            return
        
        user_id = str(user.id)
        vps_list = vps_data.get(user_id, [])
        if not vps_list:
            embed = create_no_vps_embed()
            embed.title = f"{EMOJI_STAR} {BOT_NAME} - No VPS Found"
            embed.description = f"{user.mention} doesn't have any VPS."
            await ctx.send(embed=embed)
            return
        
        view = ManageView(str(ctx.author.id), vps_list, is_admin=True, owner_id=user_id, ctx=ctx)
        embed = await view.create_vps_embed(0)
        msg = await ctx.send(embed=embed, view=view)
        view.message = msg
    
    else:
        user_id = str(ctx.author.id)
        vps_list = vps_data.get(user_id, [])
        
        if not vps_list:
            await ctx.send(embed=create_no_vps_embed())
            return
        
        view = ManageView(user_id, vps_list, ctx=ctx)
        embed = await view.create_vps_embed(0)
        msg = await ctx.send(embed=embed, view=view)
        view.message = msg

# ==================================================== VPS MANAGEMENT COMMANDS END =====================================================

# ==================================================== SHARE COMMANDS =====================================================

@bot.command(name='share-user')
@commands.cooldown(1, 3, commands.BucketType.user)
async def share_user(ctx, shared_user: discord.Member, vps_number: int):
    """Share VPS access with another user"""
    if not await maintenance_check(ctx):
        return
    
    user_id = str(ctx.author.id)
    shared_user_id = str(shared_user.id)
    
    vps = get_vps_by_number(user_id, vps_number)
    if not vps:
        await ctx.send(embed=create_error_embed("Invalid VPS", "Invalid VPS number or you don't have a VPS."))
        return
    if "shared_with" not in vps:
        vps["shared_with"] = []
    
    if shared_user_id in vps["shared_with"]:
        await ctx.send(embed=create_error_embed("Already Shared", f"{shared_user.mention} already has access to this VPS!"))
        return
    
    vps["shared_with"].append(shared_user_id)
    save_vps_data()
    
    embed = create_success_embed("VPS Shared", f"VPS #{vps_number} shared with {shared_user.mention}!")
    await ctx.send(embed=embed)

@bot.command(name='share-ruser')
@commands.cooldown(1, 3, commands.BucketType.user)
async def revoke_share(ctx, shared_user: discord.Member, vps_number: int):
    """Revoke VPS access from another user"""
    if not await maintenance_check(ctx):
        return
    
    user_id = str(ctx.author.id)
    shared_user_id = str(shared_user.id)
    
    vps = get_vps_by_number(user_id, vps_number)
    if not vps:
        await ctx.send(embed=create_error_embed("Invalid VPS", "Invalid VPS number or you don't have a VPS."))
        return
    if "shared_with" not in vps:
        vps["shared_with"] = []
    
    if shared_user_id not in vps["shared_with"]:
        await ctx.send(embed=create_error_embed("Not Shared", f"{shared_user.mention} doesn't have access to this VPS!"))
        return
    
    vps["shared_with"].remove(shared_user_id)
    save_vps_data()
    
    embed = create_success_embed("Access Revoked", f"Access to VPS #{vps_number} revoked from {shared_user.mention}!")
    await ctx.send(embed=embed)

@bot.command(name='manage-shared')
@commands.cooldown(1, 3, commands.BucketType.user)
async def manage_shared_vps(ctx, owner: discord.Member, vps_number: int):
    """Manage a VPS that has been shared with you"""
    if not await maintenance_check(ctx):
        return
    
    owner_id = str(owner.id)
    user_id = str(ctx.author.id)
    
    vps = get_vps_by_number(owner_id, vps_number)
    if not vps:
        await ctx.send(embed=create_error_embed("Invalid VPS", "Invalid VPS number or owner doesn't have a VPS."))
        return
    if user_id not in vps.get("shared_with", []):
        await ctx.send(embed=create_error_embed("Access Denied", "You do not have access to this VPS."))
        return
    
    actual_idx = get_vps_index_by_number(owner_id, vps_number)
    view = ManageView(user_id, [vps], is_shared=True, owner_id=owner_id, actual_index=actual_idx)
    embed = await view.create_vps_embed(0)
    msg = await ctx.send(embed=embed, view=view)
    view.message = msg
    view.ctx = ctx

# ==================================================== SHARE COMMANDS END =====================================================

# ==================================================== ADMIN INFO COMMANDS =====================================================

@bot.command(name='vpsinfo')
@is_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def vps_info(ctx, container_name: str):
    """VPS information"""
    if not container_name:
        await ctx.send(embed=create_error_embed("Usage", f"Usage: {PREFIX}vpsinfo <container_name>"))
        return
    
    found_vps = None
    found_user = None
    user_id = None
    
    for uid, vps_list in vps_data.items():
        for vps in vps_list:
            if vps['container_name'] == container_name:
                found_vps = vps
                user_id = uid
                try:
                    found_user = await bot.fetch_user(int(uid))
                except:
                    found_user = None
                break
        if found_vps:
            break
    
    if not found_vps:
        await ctx.send(embed=create_error_embed("VPS Not Found", f"No VPS found with container name: `{container_name}`"))
        return
    
    status = await get_container_status(container_name)
    cpu = await get_container_cpu(container_name)
    memory = await get_container_memory(container_name)
    disk = await get_container_disk(container_name)
    uptime = await get_container_uptime(container_name)
    
    # Find OS display name
    os_display = found_vps.get('os_version', 'ubuntu:22.04')
    os_display = get_os_display_name(os_display)
    
    embed = discord.Embed(
        title=f"{EMOJI_STAR} VPS Information - {container_name}",
        description=f"Details for VPS",
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
    
    embed.add_field(name="**Owner**", value=found_user.mention if found_user else f"ID: {user_id}", inline=True)
    embed.add_field(name="**Status**", value=status.upper(), inline=True)
    embed.add_field(name="**Plan**", value=found_vps.get('plan_name', 'Custom'), inline=True)
    embed.add_field(name="**Purge Protected**", value=f"{EMOJI_SUCCESS} Yes" if found_vps.get('purge_protected', False) else f"{EMOJI_CROSS} No", inline=True)
    
    resources = f"**RAM:** {found_vps['ram']}\n"
    resources += f"**CPU:** {found_vps['cpu']} Cores\n"
    resources += f"**Storage:** {found_vps['storage']}\n"
    resources += f"**OS:** {get_os_emoji(found_vps.get('os_version', 'ubuntu:22.04'))} {os_display}"
    embed.add_field(name="**Allocated Resources**", value=resources, inline=False)
    
    live_stats = f"**CPU Usage:** {cpu}\n"
    live_stats += f"**Memory:** {memory}\n"
    live_stats += f"**Disk:** {disk}\n"
    live_stats += f"**Uptime:** {uptime}"
    embed.add_field(name="**Live Statistics**", value=live_stats, inline=False)
    
    timer_line = get_vps_timer_line(found_vps)
    if timer_line:
        embed.add_field(name="**Timer**", value=timer_line.strip(), inline=False)
    
    if found_vps.get('suspended', False):
        embed.add_field(name="**Suspended**", value=f"Reason: {found_vps.get('suspended_reason', 'No reason')}", inline=False)
    
    if found_vps.get('whitelisted', False):
        embed.add_field(name="**Whitelisted**", value="Exempt from auto-suspension", inline=False)
    
    created = found_vps.get('created_at', 'Unknown')[:19].replace('T', ' ')
    embed.add_field(name="**Created**", value=created, inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='vps-stats')
@is_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def vps_stats(ctx, container_name: str):
    """VPS stats - live updating every 1 second"""
    target_vps = None
    for uid, lst in vps_data.items():
        for vps in lst:
            if vps['container_name'] == container_name:
                target_vps = vps
                break
        if target_vps:
            break

    msg = await ctx.send(embed=create_info_embed(f"{EMOJI_STATS} Live Statistics", f"{EMOJI_LOADING} Starting live stats..."))

    start = time.time()
    try:
        while (time.time() - start) < 3600:
            iter_start = time.time()
            cpu = await get_container_cpu(container_name)
            memory = await get_container_memory(container_name)
            disk = await get_container_disk(container_name)
            uptime = await get_container_uptime(container_name)
            lxc_status = await get_container_status(container_name)

            embed = create_info_embed(f"{EMOJI_STATS} Live Statistics - `{container_name}`", "Stats update every 1 second")
            add_field(embed, f"{EMOJI_STATUS} Status", f"`{lxc_status.upper()}`", True)
            add_field(embed, f"{EMOJI_CPU} CPU", cpu, True)
            add_field(embed, f"{EMOJI_RAM} Memory", memory, True)
            add_field(embed, f"{EMOJI_DISK} Disk", disk, True)
            add_field(embed, f"{EMOJI_UPTIME} Uptime", uptime, True)

            if target_vps:
                timer_status = target_vps.get('timer_status', '')
                timer_line = get_vps_timer_line(target_vps)
                if timer_line:
                    add_field(embed, f"{EMOJI_UPTIME} Auto-Suspend Timer", timer_line.replace("\n", ""), True)

            await msg.edit(embed=embed)
            elapsed = time.time() - iter_start
            await asyncio.sleep(max(0, 1 - elapsed))
    except Exception:
        pass

@bot.command(name='restart-vps')
@is_admin()
@commands.cooldown(1, 10, commands.BucketType.user)
async def restart_vps(ctx, container_name: str):
    """Restart VPS"""
    await ctx.send(embed=create_info_embed("Restarting VPS", f"Restarting VPS `{container_name}`..."))
    
    try:
        await execute_lxc(f"lxc restart {shlex.quote(container_name)}")
        
        for user_id, vps_list in vps_data.items():
            for vps in vps_list:
                if vps['container_name'] == container_name:
                    vps['status'] = 'running'
                    vps['suspended'] = False
                    save_vps_data()
                    break
        
        await apply_internal_permissions(container_name)
        
        embed = create_success_embed("VPS Restarted", f"VPS `{container_name}` has been restarted successfully!")
        await ctx.send(embed=embed)
    
    except Exception as e:
        await ctx.send(embed=create_error_embed("Restart Failed", f"Error: {str(e)}"))

@bot.command(name='renew-vps')
@is_admin()
@commands.cooldown(1, 10, commands.BucketType.user)
async def renew_vps(ctx, container_name: str, time_amount: str, *, reason: str = ""):
    """Renew a timer-expired VPS
    Usage: .renew-vps <container> <time> [reason] [--force]
    Time formats: 1s, 1m, 1h, 1d, 1month, 1year
    --force: Force renew any container regardless of timer state"""
    
    force = False
    clean_reason = reason
    if '--force' in reason.lower():
        force = True
        clean_reason = re.sub(r'\s*--force\s*', '', reason, flags=re.IGNORECASE).strip()
    
    time_delta = parse_time_string(time_amount)
    if not time_delta:
        await ctx.send(embed=create_error_embed("Invalid Time Format",
            "Use formats like: `1s`, `1m`, `1h`, `1d`, `1month`, `1year`"))
        return
    
    found = False
    for user_id, lst in vps_data.items():
        for vps in lst:
            if vps['container_name'] == container_name:
                if not force and vps.get('timer_status') != 'expired':
                    await ctx.send(embed=create_error_embed("Not Expired",
                        f"VPS `{container_name}` is not expired. Timer status: {vps.get('timer_status', 'none')}\n"
                        f"Use `--force` to renew any container."))
                    return

                progress = discord.Embed(
                    title=f"{EMOJI_UPTIME} Renewing VPS",
                    description=f"{EMOJI_LOADING} Processing `{container_name}`...",
                    color=0xffaa00
                )
                if THUMBNAIL_URL:
                    progress.set_thumbnail(url=THUMBNAIL_URL)
                progress.set_footer(text=f"{BOT_NAME} VPS Manager - Renewing...", icon_url=THUMBNAIL_URL)
                msg = await ctx.send(embed=progress)

                progress.description = f"{EMOJI_LOADING} Stopping container..."
                await msg.edit(embed=progress)
                try:
                    await execute_lxc(f"lxc stop {shlex.quote(container_name)} --force")
                except:
                    pass

                progress.description = f"{EMOJI_LOADING} Updating timer..."
                await msg.edit(embed=progress)

                vps['timer_status'] = 'running'
                vps['timer_paused_at'] = ''
                vps['expires_at'] = (datetime.now() + time_delta).isoformat()
                vps['suspended'] = False
                vps['suspended_reason'] = ''
                vps['status'] = 'running'
                vps['auto_delete_warned'] = False

                progress.description = f"{EMOJI_LOADING} Starting container..."
                await msg.edit(embed=progress)
                try:
                    await execute_lxc(f"lxc start {shlex.quote(container_name)}")
                    await apply_internal_permissions(container_name)
                except Exception as e:
                    save_vps_data()
                    await msg.edit(embed=create_error_embed("Start Failed", f"VPS renewed but failed to start: {str(e)}"))
                    return

                save_vps_data()
                log_suspension(container_name, user_id, 'renew', clean_reason or ('Force renew' if force else 'Renewed by admin'), str(ctx.author.id))

                await send_log(EMOJI_UPTIME, f"VPS Renewed{' (Force)' if force else ''}",
                    f"{EMOJI_VPS} **Container:** `{container_name}`\n"
                    f"{EMOJI_ADMIN} **Admin:** {ctx.author.mention}\n"
                    f"{EMOJI_USER} **User:** <@{user_id}>\n"
                    f"{EMOJI_UPTIME} **Duration:** {format_timedelta(time_delta)}\n"
                    f"{EMOJI_INFO} **Reason:** {clean_reason or ('Force renew' if force else 'No reason')}",
                    color=0x00ff88)

                progress.title = f"{EMOJI_SUCCESS} VPS Renewed"
                progress.description = (
                    f"{EMOJI_VPS} **Container:** `{container_name}`\n"
                    f"{EMOJI_UPTIME} **New Duration:** {format_timedelta(time_delta)}\n"
                    f"{EMOJI_INFO} **Reason:** {clean_reason or ('Force renew' if force else 'No reason')}"
                )
                progress.color = 0x00ff88
                progress.set_footer(text=f"{BOT_NAME} VPS Manager - Renewed", icon_url=THUMBNAIL_URL)
                await msg.edit(embed=progress)

                try:
                    user_obj = await bot.fetch_user(int(user_id))
                    dm_embed = create_success_embed(f"{EMOJI_UPTIME} VPS Renewed",
                        f"Your VPS **`{container_name}`** has been renewed by an admin!\n"
                        f"{EMOJI_UPTIME} **New Duration:** {format_timedelta(time_delta)}\n"
                        f"{EMOJI_INFO} **Reason:** {clean_reason or 'No reason'}")
                    await user_obj.send(embed=dm_embed)
                except:
                    pass

                found = True
                break
        if found:
            break

    if not found:
        await ctx.send(embed=create_error_embed("Not Found",
            f"VPS `{container_name}` was not found."))

@bot.command(name='clone-vps')
@is_admin()
@commands.cooldown(1, 30, commands.BucketType.user)
async def clone_vps(ctx, container_name: str, new_name: str = None):
    """Clone VPS"""
    if not new_name:
        new_name = f"{container_name}-clone-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    await ctx.send(embed=create_info_embed("Cloning VPS", f"Cloning `{container_name}` to `{new_name}`..."))
    
    try:
        await execute_lxc(f"lxc copy {shlex.quote(container_name)} {shlex.quote(new_name)}")
        embed = create_success_embed("VPS Cloned", f"VPS `{container_name}` cloned to `{new_name}`")
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(embed=create_error_embed("Clone Failed", f"Error: {str(e)}"))

@bot.command(name='snapshot')
@is_admin()
@commands.cooldown(1, 30, commands.BucketType.user)
async def create_snapshot(ctx, container_name: str, snap_name: str = None):
    """Create snapshot"""
    if not snap_name:
        snap_name = f"snap-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    await ctx.send(embed=create_info_embed("Creating Snapshot", f"Creating snapshot `{snap_name}` for `{container_name}`..."))
    
    try:
        await execute_lxc(f"lxc snapshot {shlex.quote(container_name)} {snap_name}")
        embed = create_success_embed("Snapshot Created", f"Snapshot `{snap_name}` created for `{container_name}`")
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(embed=create_error_embed("Snapshot Failed", f"Error: {str(e)}"))

@bot.command(name='restore-backup')
@is_admin()
@commands.cooldown(1, 30, commands.BucketType.user)
async def restore_backup(ctx, container_name: str, snap_name: str):
    """Restore VPS Data"""
    await ctx.send(embed=create_info_embed("Restoring Backup", f"Restoring `{container_name}` from snapshot `{snap_name}`..."))
    
    try:
        await execute_lxc(f"lxc restore {shlex.quote(container_name)} {snap_name}")
        embed = create_success_embed("Backup Restored", f"VPS `{container_name}` restored from snapshot `{snap_name}`")
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(embed=create_error_embed("Restore Failed", f"Error: {str(e)}"))

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
    add_field(embed, "🖥️ VPS Owned", str(len(vps_data.get(str(user.id), []))), True)
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
async def purge_protect(ctx, user: discord.Member, vps_number: int = None):
    """Protect a user's VPS from .purge-vm-all command
    Usage: .purge-prot @user <vps_number> - Protect specific VPS
           .purge-prot @user - Protect all VPS of that user
    """
    user_id = str(user.id)
    
    if user_id not in vps_data or not vps_data[user_id]:
        await ctx.send(embed=create_error_embed("No VPS Found", f"{user.mention} doesn't have any VPS."))
        return
    
    protected_count = 0
    
    if vps_number is None:
        # Protect all VPS of the user
        for vps in vps_data[user_id]:
            if not vps.get('purge_protected', False):
                vps['purge_protected'] = True
                log_purge_protection(vps['container_name'], user_id, 'protect', str(ctx.author.id))
                protected_count += 1
        
        save_vps_data()
        
        if protected_count == 0:
            embed = create_info_embed("Already Protected", f"All VPS of {user.mention} are already purge protected.")
        else:
            embed = create_success_embed("Purge Protection Enabled", 
                f"Protected **{protected_count}** VPS of {user.mention} from `{PREFIX}purge-vm-all`.")
        
        await ctx.send(embed=embed)
    
    else:
        # Protect specific VPS
        vps = get_vps_by_number(user_id, vps_number)
        if not vps:
            await ctx.send(embed=create_error_embed("Invalid VPS Number", 
                f"No VPS with number #{vps_number} found for {user.mention}."))
            return
        
        if vps.get('purge_protected', False):
            embed = create_info_embed("Already Protected", 
                f"VPS #{vps_number} of {user.mention} is already purge protected.")
        else:
            vps['purge_protected'] = True
            save_vps_data()
            log_purge_protection(vps['container_name'], user_id, 'protect', str(ctx.author.id))
            
            embed = create_success_embed("Purge Protection Enabled", 
                f"VPS #{vps_number} (`{vps['container_name']}`) of {user.mention} is now protected from `{PREFIX}purge-vm-all`.")
        
        await ctx.send(embed=embed)

@bot.command(name='purge-remove-prot')
@is_main_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def purge_remove_protect(ctx, user: discord.Member, vps_number: int = None):
    """Remove purge protection from a user's VPS
    Usage: .purge-remove-prot @user <vps_number> - Remove protection from specific VPS
           .purge-remove-prot @user - Remove protection from all VPS of that user
    """
    user_id = str(user.id)
    
    if user_id not in vps_data or not vps_data[user_id]:
        await ctx.send(embed=create_error_embed("No VPS Found", f"{user.mention} doesn't have any VPS."))
        return
    
    unprotected_count = 0
    
    if vps_number is None:
        # Remove protection from all VPS of the user
        for vps in vps_data[user_id]:
            if vps.get('purge_protected', False):
                vps['purge_protected'] = False
                log_purge_protection(vps['container_name'], user_id, 'remove_protect', str(ctx.author.id))
                unprotected_count += 1
        
        save_vps_data()
        
        if unprotected_count == 0:
            embed = create_info_embed("No Protection Found", f"No purge protected VPS found for {user.mention}.")
        else:
            embed = create_success_embed("Purge Protection Removed", 
                f"Removed protection from **{unprotected_count}** VPS of {user.mention}.")
        
        await ctx.send(embed=embed)
    
    else:
        # Remove protection from specific VPS
        vps = get_vps_by_number(user_id, vps_number)
        if not vps:
            await ctx.send(embed=create_error_embed("Invalid VPS Number", 
                f"No VPS with number #{vps_number} found for {user.mention}."))
            return
        
        if not vps.get('purge_protected', False):
            embed = create_info_embed("Not Protected", 
                f"VPS #{vps_number} of {user.mention} is not purge protected.")
        else:
            vps['purge_protected'] = False
            save_vps_data()
            log_purge_protection(vps['container_name'], user_id, 'remove_protect', str(ctx.author.id))
            
            embed = create_success_embed("Purge Protection Removed", 
                f"VPS #{vps_number} (`{vps['container_name']}`) of {user.mention} is no longer protected from `{PREFIX}purge-vm-all`.")
        
        await ctx.send(embed=embed)

@bot.command(name='purge-list-protected')
@is_main_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def purge_list_protected(ctx):
    """List all purge protected VPS"""
    
    protected_vps = []
    
    for user_id, vps_list in vps_data.items():
        for vps in vps_list:
            if vps.get('purge_protected', False):
                try:
                    user = await bot.fetch_user(int(user_id))
                    username = user.name
                except:
                    username = f"Unknown User ({user_id})"
                
                protected_vps.append(f"• **{username}** - `{vps['container_name']}` ({vps.get('plan_name', 'Custom')})")
    
    if not protected_vps:
        embed = create_info_embed("Purge Protected VPS", "No purge protected VPS found.")
    else:
        embed = create_info_embed("Purge Protected VPS", f"Found **{len(protected_vps)}** protected VPS")
        
        # Split into multiple fields if too many
        chunks = [protected_vps[i:i+10] for i in range(0, len(protected_vps), 10)]
        for i, chunk in enumerate(chunks):
            add_field(embed, f"Protected VPS {i+1}", "\n".join(chunk), False)
    
    await ctx.send(embed=embed)

# ==================================================== PURGE PROTECTION COMMANDS END =====================================================

# ==================================================== UPDATED ADMIN COMMANDS - SERVER STATS =====================================================

@bot.command(name='serverstats')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def server_stats(ctx):
    """Server statistics - Shows detailed server overview"""
    
    total_users = len(vps_data)
    total_admins = len(admin_data.get("admins", [])) + len(MAIN_ADMIN_IDS)  # + main admins
    
    total_vps = 0
    running_vps = 0
    suspended_vps = 0
    whitelisted_vps = 0
    stopped_vps = 0
    
    total_ram = 0
    total_cpu = 0
    total_storage = 0
    
    for user_id, vps_list in vps_data.items():
        for vps in vps_list:
            total_vps += 1
            
            # Parse resources (remove 'GB' and convert to int)
            try:
                ram_value = int(vps['ram'].replace('GB', '').strip())
                total_ram += ram_value
            except:
                pass
                
            try:
                cpu_value = int(vps['cpu'])
                total_cpu += cpu_value
            except:
                pass
                
            try:
                storage_value = int(vps['storage'].replace('GB', '').strip())
                total_storage += storage_value
            except:
                pass
            
            # Count status
            if vps.get('status') == 'running':
                running_vps += 1
            else:
                stopped_vps += 1
                
            if vps.get('suspended', False):
                suspended_vps += 1
            if vps.get('whitelisted', False):
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

@bot.command(name='list-all')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def list_all_vps(ctx):
    """List all VPS with detailed user and VPS information"""
    
    total_users = len(vps_data)
    total_vps = 0
    running_vps = 0
    stopped_vps = 0
    suspended_vps = 0
    whitelisted_vps = 0
    
    for user_id, vps_list in vps_data.items():
        for vps in vps_list:
            total_vps += 1
            if vps.get('status') == 'running':
                running_vps += 1
            else:
                stopped_vps += 1
            if vps.get('suspended', False):
                suspended_vps += 1
            if vps.get('whitelisted', False):
                whitelisted_vps += 1
    
    # First embed - System Overview
    embed1 = discord.Embed(
        title=f"{EMOJI_STAR} {BOT_NAME} - All VPS Information",
        description="Complete overview of all VPS deployments and user statistics",
        color=0x00ccff
    )
    
    # Set thumbnail if URL is provided
    if THUMBNAIL_URL:
        embed1.set_thumbnail(url=THUMBNAIL_URL)
    
    # Set footer with timestamp and icon
    embed1.set_footer(
        text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        icon_url=THUMBNAIL_URL
    )
    
    system_text = f"- **Total Users:** {total_users}\n- **Total VPS:** {total_vps}\n- **Running:** {running_vps}\n- **Stopped:** {stopped_vps}\n- **Suspended:** {suspended_vps}\n- **Whitelisted:** {whitelisted_vps}"
    embed1.add_field(name="**System Overview**", value=system_text, inline=False)
    
    await ctx.send(embed=embed1)
    
    # Second embed - User Summary
    embed2 = discord.Embed(
        title=f"{EMOJI_STAR} {BOT_NAME} - User Summary",
        description="Summary of all users and their VPS",
        color=0x00ccff
    )
    
    # Set thumbnail if URL is provided
    if THUMBNAIL_URL:
        embed2.set_thumbnail(url=THUMBNAIL_URL)
    
    # Set footer with timestamp and icon
    embed2.set_footer(
        text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        icon_url=THUMBNAIL_URL
    )
    
    user_summaries = []
    for user_id, vps_list in vps_data.items():
        try:
            user = await bot.fetch_user(int(user_id))
            username = f"{user.name} (@{user.name})"
        except:
            username = f"Unknown User ({user_id})"
        
        user_vps_count = len(vps_list)
        user_running = sum(1 for v in vps_list if v.get('status') == 'running')
        user_suspended = sum(1 for v in vps_list if v.get('suspended', False))
        user_whitelisted = sum(1 for v in vps_list if v.get('whitelisted', False))
        
        user_summaries.append(f"- **{username}** - {user_vps_count} VPS ({user_running} running, {user_suspended} suspended, {user_whitelisted} whitelisted)")
    
    # Split into multiple fields if too many users
    chunk_size = 8
    for i in range(0, len(user_summaries), chunk_size):
        chunk = user_summaries[i:i+chunk_size]
        embed2.add_field(name=f"**Users (Part {i//chunk_size + 1})**" if len(user_summaries) > chunk_size else "**Users**", 
                        value="\n".join(chunk), 
                        inline=False)
    
    await ctx.send(embed=embed2)
    
    # Third embed - VPS Details
    embed3 = discord.Embed(
        title=f"{EMOJI_STAR} {BOT_NAME} - VPS Details",
        description="List of all VPS deployments",
        color=0x00ccff
    )
    
    # Set thumbnail if URL is provided
    if THUMBNAIL_URL:
        embed3.set_thumbnail(url=THUMBNAIL_URL)
    
    # Set footer with timestamp and icon
    embed3.set_footer(
        text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        icon_url=THUMBNAIL_URL
    )
    
    vps_details = []
    for user_id, vps_list in vps_data.items():
        try:
            user = await bot.fetch_user(int(user_id))
            username = user.name
        except:
            username = f"Unknown-User"
        
        # Find OS display name
        for vps in vps_list:
            container_name = vps['container_name']
            config = vps.get('config', f"{vps['ram']} RAM / {vps['cpu']} CPU / {vps['storage']} Disk")
            status = vps.get('status', 'unknown').upper()
            
            vps_details.append(f"- **{username}** - VPS: `{container_name}` - {config} - {status}")
    
    # Split into multiple fields if too many VPS
    chunk_size = 8
    for i in range(0, len(vps_details), chunk_size):
        chunk = vps_details[i:i+chunk_size]
        embed3.add_field(name=f"**VPS List (Part {i//chunk_size + 1})**" if len(vps_details) > chunk_size else "**VPS List**", 
                        value="\n".join(chunk), 
                        inline=False)
    
    await ctx.send(embed=embed3)

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
async def create_vps(ctx, ram: int, cpu: int, disk: int, time: str, user: discord.Member, *, bypass_flags: str = None):
    """Create VPS with OS selection
    Usage: .create <ram> <cpu> <disk> <time> @user [--bypass_cpu] [--bypass_ram] [--bypass_disk] [--bypass_all]
    Multiple flags can be combined (e.g. --bypass_cpu --bypass_ram). --bypass_all overrides all others.
    Time formats: 1s, 1m, 1h, 1d, 1month, 1year"""
    if ram <= 0 or cpu <= 0 or disk <= 0:
        await ctx.send(embed=create_error_embed("Invalid Specs", "RAM, CPU, and Disk must be positive integers."))
        return
    
    bypasses = {'--bypass_cpu': False, '--bypass_ram': False, '--bypass_disk': False}
    if bypass_flags:
        flags = bypass_flags.strip().split()
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
    
    time_delta = parse_time_string(time)
    if not time_delta:
        await ctx.send(embed=create_error_embed("Invalid Time Format",
            "Use formats like: `1s`, `1m`, `1h`, `1d`, `1month`, `1year`"))
        return
    time_display = f"\n{EMOJI_UPTIME} **Timer:** {format_timedelta(time_delta)}"
    
    bypass_text = ""
    if bypass_flags:
        bypass_text = f"\n{EMOJI_WARNING} **Bypass:** `{bypass_flags.strip()}`"
    
    msg = await ctx.send(embed=create_info_embed("Checking Resources", f"{EMOJI_LOADING} Verifying available resources..."))
    can_create, error_msg = await check_resources(ram, cpu, disk, bypass_cpu=bypass_cpu, bypass_ram=bypass_ram, bypass_disk=bypass_disk)
    if not can_create:
        await msg.edit(embed=create_error_embed("Insufficient Resources", error_msg))
        return
    
    embed = create_info_embed("VPS Creation", 
        f"Creating VPS for {user.mention}\n"
        f"**RAM:** {ram}GB\n"
        f"**CPU:** {cpu} Cores\n"
        f"**Disk:** {disk}GB{time_display}{bypass_text}\n\n"
        f"Select OS below.")
    
    view = AdminOSSelectView(ram, cpu, disk, user, ctx, time, bypass_cpu=bypass_cpu, bypass_ram=bypass_ram, bypass_disk=bypass_disk)
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
            f"**RAM:** {self.ram}GB\n"
            f"**CPU:** {self.cpu} Cores\n"
            f"**Disk:** {self.disk}GB{time_confirm}{bypass_display}\n\n"
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
        ram_mb = self.ram * 1024
        
        try:
            await ensure_lxdbr0()

            resolved_os = await ensure_image_available(self.selected_os)
            await ensure_container_name_available(container_name)
            await execute_lxc(f"lxc init {resolved_os} {shlex.quote(container_name)} -s {DEFAULT_STORAGE_POOL}", timeout=600)
            await execute_lxc(f"lxc config set {shlex.quote(container_name)} limits.memory {ram_mb}MB")
            await execute_lxc(f"lxc config set {shlex.quote(container_name)} limits.cpu {self.cpu}")
            await execute_lxc(f"lxc config device set {shlex.quote(container_name)} root size={self.disk}GB")
            await apply_lxc_config(container_name)
            await execute_lxc(f"lxc start {shlex.quote(container_name)}")
            await apply_internal_permissions(container_name)

            creating_embed.description = f"{EMOJI_GLOBAL} Fixing internet for `{container_name}`..."
            await interaction.edit_original_response(embed=creating_embed)
            progress_msg = await interaction.original_response()
            await fix_container_internet(container_name, msg=progress_msg)

            creating_embed.description = f"{EMOJI_LOADING} Finalizing..."
            await interaction.edit_original_response(embed=creating_embed)

            config_str = f"{self.ram}GB RAM / {self.cpu} CPU / {self.disk}GB Disk"
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
                "ram": f"{self.ram}GB",
                "cpu": str(self.cpu),
                "storage": f"{self.disk}GB",
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
            add_field(success_embed, "Resources", f"**RAM:** {self.ram}GB\n**CPU:** {self.cpu} Cores\n**Storage:** {self.disk}GB{timer_success}", False)
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
                f"{EMOJI_RAM} **RAM:** {self.ram}GB | {EMOJI_CPU} **CPU:** {self.cpu} | {EMOJI_DISK} **Disk:** {self.disk}GB\n"
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

@bot.command(name='delete-vps')
@is_admin()
@commands.cooldown(1, 10, commands.BucketType.user)
async def delete_vps(ctx, user_identifier: str, vps_number: int, *, reason: str = "No reason provided"):
    """Delete user's VPS with confirmation
    Usage: .delete-vps @user <vps_number> [reason]
           .delete-vps <user_id> <vps_number> [reason]"""
    user = None
    user_id = None
    match = re.match(r'<@!?(\d+)>', user_identifier)
    clean = match.group(1) if match else user_identifier
    try:
        uid = int(clean)
        user_id = str(uid)
        try:
            user = await bot.fetch_user(uid)
        except Exception:
            user = None
    except ValueError:
        await ctx.send(embed=create_error_embed("Invalid User", "Please provide a valid user mention or Discord ID."))
        return

    user_display = user.mention if user else f"User `{user_id}`"

    if user_id not in vps_data:
        await ctx.send(embed=create_error_embed("No VPS Found", f"{user_display} doesn't have any VPS."))
        return

    vps = get_vps_by_number(user_id, vps_number)
    if not vps:
        await ctx.send(embed=create_error_embed("Invalid VPS Number",
            f"No VPS with number #{vps_number}.\nUse `{PREFIX}userinfo {user.mention if user else user_id}` to see their VPS."))
        return

    container_name = vps["container_name"]

    os_display = vps.get('os_version', 'ubuntu:22.04')
    os_display = get_os_display_name(os_display)

    embed = discord.Embed(
        title=f"{EMOJI_WARNING} Confirm VPS Deletion",
        description=f"Are you sure you want to delete this VPS?",
        color=0xffaa00
    )

    if THUMBNAIL_URL:
        embed.set_thumbnail(url=THUMBNAIL_URL)

    embed.set_footer(
        text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        icon_url=THUMBNAIL_URL
    )

    vps_details = f"**Owner:** {user_display}\n"
    vps_details += f"**VPS #{vps_number}:** `{container_name}`\n"
    vps_details += f"**Plan:** {vps.get('plan_name', 'Custom')}\n"
    vps_details += f"**Resources:** {vps['ram']} RAM | {vps['cpu']} CPU | {vps['storage']} Storage\n"
    vps_details += f"**OS:** {get_os_emoji(vps.get('os_version', 'ubuntu:22.04'))} {os_display}\n"
    vps_details += f"**Status:** {vps.get('status', 'unknown').upper()}\n"
    vps_details += f"**Purge Protected:** {f'{EMOJI_SUCCESS} Yes' if vps.get('purge_protected', False) else f'{EMOJI_CROSS} No'}\n"
    vps_details += f"**Created:** {vps.get('created_at', 'Unknown')[:10]}\n"
    vps_details += f"**Reason:** {reason}"

    add_field(embed, "VPS Details", vps_details, False)
    add_field(embed, f"{EMOJI_WARNING} Warning", "This action is **permanent** and cannot be undone!\nAll data on this VPS will be lost.", False)

    view = DeleteVPSView(ctx, user, user_id, vps_number, vps, container_name, reason)
    msg = await ctx.send(embed=embed, view=view)
    view.message = msg

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
                    f"Use `{PREFIX}purge-list-protected` to see protected VPS.")
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
            add_field(final_embed, "Note", f"{EMOJI_ADMIN} {skipped_count} protected VPS were skipped. Use `{PREFIX}purge-list-protected` to see them.", False)
        
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

@bot.command(name='purge-vm-all')
@is_main_admin()
@commands.cooldown(1, 300, commands.BucketType.user)  # 5 minute cooldown
async def purge_all_vms(ctx):
    """Purge ALL unprotected VPS from the bot (1 by 1 deletion to prevent high load)"""
    
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
                f"Use `{PREFIX}purge-list-protected` to see protected VPS.")
        else:
            embed = create_info_embed("No VPS Found", "There are no VPS to purge.")
        await ctx.send(embed=embed)
        return
    
    # Calculate estimated time
    estimated_time = total_vps * 3  # 3 seconds per VPS
    estimated_minutes = estimated_time // 60
    estimated_seconds = estimated_time % 60
    
    # Create confirmation embed
    embed = discord.Embed(
        title=f"{EMOJI_WARNING} PURGE ALL UNPROTECTED VPS {EMOJI_WARNING}",
        description=f"This will delete **ALL {total_vps} UNPROTECTED VPS** from the system!\n"
                   f"**{protected_vps} protected VPS will be skipped.**",
        color=0xff0000
    )
    
    # Set thumbnail if URL is provided
    if THUMBNAIL_URL:
        embed.set_thumbnail(url=THUMBNAIL_URL)
    
    # Set footer with timestamp and icon
    embed.set_footer(
        text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        icon_url=THUMBNAIL_URL
    )
    
    warning = f"**Unprotected VPS to delete:** {total_vps}\n"
    warning += f"**Protected VPS (skipped):** {protected_vps}\n"
    warning += f"**Deletion speed:** 1 VPS every 3 seconds\n"
    warning += f"**Estimated time:** {estimated_minutes} minutes and {estimated_seconds} seconds\n\n"
    warning += f"**{EMOJI_WARNING} THIS ACTION CANNOT BE UNDONE!**\n"
    warning += "• All unprotected VPS containers will be permanently deleted\n"
    warning += "• All port forwards will be removed\n"
    warning += "• All user data for deleted VPS will be cleared\n"
    warning += "• Protected VPS will remain untouched\n\n"
    warning += f"Type `{PREFIX}confirm-purge-all` to proceed with this destructive action."
    
    add_field(embed, "Warning", warning, False)
    
    await ctx.send(embed=embed)

@bot.command(name='confirm-purge-all')
@is_main_admin()
@commands.cooldown(1, 300, commands.BucketType.user)
async def confirm_purge_all(ctx):
    """Confirm and execute purge all unprotected VPS"""
    
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
                f"Use `{PREFIX}purge-list-protected` to see protected VPS.")
        else:
            embed = create_info_embed("No VPS Found", "There are no VPS to purge.")
        await ctx.send(embed=embed)
        return
    
    # Calculate estimated time
    estimated_time = total_vps * 3
    estimated_minutes = estimated_time // 60
    estimated_seconds = estimated_time % 60
    
    # Create final confirmation with buttons
    embed = discord.Embed(
        title=f"{EMOJI_WARNING} FINAL CONFIRMATION - PURGE ALL UNPROTECTED VPS",
        description=f"You are about to delete **{total_vps} unprotected VPS**",
        color=0xff0000
    )
    
    # Set thumbnail if URL is provided
    if THUMBNAIL_URL:
        embed.set_thumbnail(url=THUMBNAIL_URL)
    
    # Set footer with timestamp and icon
    embed.set_footer(
        text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        icon_url=THUMBNAIL_URL
    )
    
    details = f"**Unprotected VPS to delete:** {total_vps}\n"
    details += f"**Protected VPS (skipped):** {protected_vps}\n"
    details += f"**Estimated time:** {estimated_minutes} minutes and {estimated_seconds} seconds\n"
    details += f"**Deletion rate:** 1 VPS every 3 seconds\n\n"
    details += "This operation will:\n"
    details += "• Delete all unprotected VPS containers\n"
    details += "• Remove all port forwards\n"
    details += "• Clear user data for deleted VPS\n"
    details += "• Protected VPS will remain untouched\n\n"
    details += "**Are you absolutely sure?**"
    
    add_field(embed, "Details", details, False)
    
    view = PurgeAllVMSView(ctx)
    msg = await ctx.send(embed=embed, view=view)
    view.message = msg

# ==================================================== PURGE ALL VMS COMMAND (1 BY 1 DELETION) END =====================================================

# ==================================================== ADDITIONAL ADMIN COMMANDS =====================================================

@bot.command(name='add-resources')
@is_admin()
@commands.cooldown(1, 10, commands.BucketType.user)
async def add_resources(ctx, container_name: str, ram: int = None, cpu: int = None, disk: int = None):
    """Add resources to VPS"""
    if ram is None and cpu is None and disk is None:
        await ctx.send(embed=create_error_embed("Missing Parameters", "Please specify at least one resource to add"))
        return
    
    found_vps = None
    user_id = None
    vps_index = None
    
    for uid, vps_list in vps_data.items():
        for i, vps in enumerate(vps_list):
            if vps['container_name'] == container_name:
                found_vps = vps
                user_id = uid
                vps_index = i
                break
        if found_vps:
            break
    
    if not found_vps:
        await ctx.send(embed=create_error_embed("VPS Not Found", f"No VPS found with ID: `{container_name}`"))
        return
    
    was_running = found_vps.get('status') == 'running' and not found_vps.get('suspended', False)
    disk_changed = disk is not None
    
    if was_running:
        await ctx.send(embed=create_info_embed("Stopping VPS", f"Stopping VPS `{container_name}` to apply resource changes..."))
        try:
            await execute_lxc(f"lxc stop {shlex.quote(container_name)}")
            found_vps['status'] = 'stopped'
            save_vps_data()
        except Exception as e:
            await ctx.send(embed=create_error_embed("Stop Failed", f"Error stopping VPS: {str(e)}"))
            return
    
    if ram is not None or cpu is not None or disk is not None:
        current_ram_gb = int(found_vps['ram'].replace('GB', ''))
        current_cpu = int(found_vps['cpu'])
        current_disk_gb = int(found_vps['storage'].replace('GB', ''))
        
        resources = await get_available_resources()
        
        new_ram_total = current_ram_gb + (ram if ram and ram > 0 else 0)
        new_cpu_total = current_cpu + (cpu if cpu and cpu > 0 else 0)
        new_disk_total = current_disk_gb + (disk if disk and disk > 0 else 0)
        
        other_ram = resources['ram']['allocated_gb'] - current_ram_gb
        other_cpu = resources['cpu']['allocated'] - current_cpu
        
        issues = []
        if ram and ram > 0 and (other_ram + new_ram_total) > resources['ram']['total_gb']:
            issues.append(f"{EMOJI_RAM} Not enough RAM: total would be {other_ram + new_ram_total}GB, host has {resources['ram']['total_gb']}GB")
        if cpu and cpu > 0 and (other_cpu + new_cpu_total) > resources['cpu']['total']:
            issues.append(f"{EMOJI_CPU} Not enough CPU: total would be {other_cpu + new_cpu_total} cores, host has {resources['cpu']['total']}")
        if disk and disk > 0 and new_disk_total > resources['disk']['available_gb']:
            issues.append(f"{EMOJI_DISK} Not enough disk: need {new_disk_total}GB, only {resources['disk']['available_gb']}GB free")
        
        if issues:
            embed = create_error_embed("Resource Addition Failed", "\n\n".join(issues))
            await ctx.send(embed=embed)
            return
    
    changes = []
    try:
        current_ram_gb = int(found_vps['ram'].replace('GB', ''))
        current_cpu = int(found_vps['cpu'])
        current_disk_gb = int(found_vps['storage'].replace('GB', ''))
        
        new_ram_gb = current_ram_gb
        new_cpu = current_cpu
        new_disk_gb = current_disk_gb
        
        if ram is not None and ram > 0:
            new_ram_gb += ram
            ram_mb = new_ram_gb * 1024
            await execute_lxc(f"lxc config set {shlex.quote(container_name)} limits.memory {ram_mb}MB")
            changes.append(f"RAM: +{ram}GB (New total: {new_ram_gb}GB)")
        
        if cpu is not None and cpu > 0:
            new_cpu += cpu
            await execute_lxc(f"lxc config set {shlex.quote(container_name)} limits.cpu {new_cpu}")
            changes.append(f"CPU: +{cpu} cores (New total: {new_cpu} cores)")
        
        if disk is not None and disk > 0:
            new_disk_gb += disk
            await execute_lxc(f"lxc config device set {shlex.quote(container_name)} root size={new_disk_gb}GB")
            changes.append(f"Disk: +{disk}GB (New total: {new_disk_gb}GB)")
        
        found_vps['ram'] = f"{new_ram_gb}GB"
        found_vps['cpu'] = str(new_cpu)
        found_vps['storage'] = f"{new_disk_gb}GB"
        found_vps['config'] = f"{new_ram_gb}GB RAM / {new_cpu} CPU / {new_disk_gb}GB Disk"
        vps_data[user_id][vps_index] = found_vps
        save_vps_data()
        
        if was_running:
            await execute_lxc(f"lxc start {shlex.quote(container_name)}")
            found_vps['status'] = 'running'
            save_vps_data()
            await apply_internal_permissions(container_name)
        
        embed = create_success_embed("Resources Added", f"Successfully added resources to VPS `{container_name}`")
        add_field(embed, "Changes Applied", "\n".join(changes), False)
        if disk_changed:
            add_field(embed, "Disk Note", "Run `sudo resize2fs /` inside the VPS to expand the filesystem.", False)
        
        await ctx.send(embed=embed)
    
    except Exception as e:
        await ctx.send(embed=create_error_embed("Resource Addition Failed", f"Error: {str(e)}"))

@bot.command(name='resize-vps')
@is_admin()
@commands.cooldown(1, 10, commands.BucketType.user)
async def resize_vps(ctx, container_name: str, ram: int = None, cpu: int = None, disk: int = None):
    """Resize VPS resources"""
    await add_resources(ctx, container_name, ram, cpu, disk)

@bot.command(name='suspend-vps')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def suspend_vps(ctx, container_name: str, *, reason: str = "Admin action"):
    """Suspend VPS"""
    found = False
    for uid, lst in vps_data.items():
        for vps in lst:
            if vps['container_name'] == container_name:
                if vps.get('status') != 'running':
                    await ctx.send(embed=create_error_embed("Cannot Suspend", "VPS must be running to suspend."))
                    return
                try:
                    await execute_lxc(f"lxc stop {shlex.quote(container_name)}")
                    vps['status'] = 'stopped'
                    vps['suspended'] = True
                    vps['suspended_reason'] = reason
                    if 'suspension_history' not in vps:
                        vps['suspension_history'] = []
                    vps['suspension_history'].append({
                        'time': datetime.now().isoformat(),
                        'reason': reason,
                        'by': f"{ctx.author.name}"
                    })
                    timer_paused_msg = ""
                    if vps.get('timer_status') == 'running':
                        vps['timer_paused_at'] = datetime.now().isoformat()
                        vps['timer_status'] = 'paused'
                        timer_paused_msg = f"\n{EMOJI_UPTIME} **Timer:** Paused"
                    save_vps_data()
                    log_suspension(container_name, uid, 'suspend', reason, str(ctx.author.id))
                except Exception as e:
                    await ctx.send(embed=create_error_embed("Suspend Failed", str(e)))
                    return
                
                embed = create_warning_embed("VPS Suspended", f"VPS `{container_name}` suspended.")
                add_field(embed, "Reason", reason, False)
                await ctx.send(embed=embed)

                await send_log(EMOJI_WARNING, "VPS Suspended",
                    f"{EMOJI_VPS} **Container:** `{container_name}`\n"
                    f"{EMOJI_ADMIN} **By:** {ctx.author.mention}\n"
                    f"{EMOJI_USER} **User:** <@{uid}>\n"
                    f"{EMOJI_INFO} **Reason:** {reason}"
                    f"{timer_paused_msg}",
                    color=0xffaa00)

                found = True
                break
        if found:
            break
    
    if not found:
        await ctx.send(embed=create_error_embed("Not Found", f"VPS `{container_name}` not found."))

@bot.command(name='unsuspend-vps')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def unsuspend_vps(ctx, container_name: str):
    """Unsuspend VPS"""
    found = False
    for uid, lst in vps_data.items():
        for vps in lst:
            if vps['container_name'] == container_name:
                if not vps.get('suspended', False):
                    await ctx.send(embed=create_error_embed("Not Suspended", "VPS is not suspended."))
                    return
                
                if vps.get('timer_status') == 'expired':
                    await ctx.send(embed=create_error_embed("Cannot Unsuspend",
                        f"VPS `{container_name}` was suspended by timer expiration.\n"
                        f"Use `{PREFIX}renew-vps {container_name} <time> [reason]` to renew it."))
                    return
                
                try:
                    vps['suspended'] = False
                    vps['suspended_reason'] = ''
                    vps['status'] = 'running'
                    
                    timer_resumed_msg = ""
                    if vps.get('timer_status') == 'paused':
                        expires_at = vps.get('expires_at', '')
                        timer_paused_at = vps.get('timer_paused_at', '')
                        if expires_at and timer_paused_at:
                            remaining = datetime.fromisoformat(expires_at) - datetime.fromisoformat(timer_paused_at)
                            vps['expires_at'] = (datetime.now() + remaining).isoformat()
                        vps['timer_status'] = 'running'
                        vps['timer_paused_at'] = ''
                        timer_resumed_msg = f"\n{EMOJI_UPTIME} **Timer:** Resumed"
                    
                    await execute_lxc(f"lxc start {shlex.quote(container_name)}")
                    await apply_internal_permissions(container_name)
                    save_vps_data()
                    log_suspension(container_name, uid, 'unsuspend', '', str(ctx.author.id))
                    
                    embed = create_success_embed("VPS Unsuspended", f"VPS `{container_name}` unsuspended and started.")
                    await ctx.send(embed=embed)

                    await send_log(EMOJI_SUCCESS, "VPS Unsuspended",
                        f"{EMOJI_VPS} **Container:** `{container_name}`\n"
                        f"{EMOJI_ADMIN} **By:** {ctx.author.mention}\n"
                        f"{EMOJI_USER} **User:** <@{uid}>"
                        f"{timer_resumed_msg}",
                        color=0x00ff88)

                    found = True
                except Exception as e:
                    await ctx.send(embed=create_error_embed("Start Failed", str(e)))
                break
        if found:
            break
    
    if not found:
        await ctx.send(embed=create_error_embed("Not Found", f"VPS `{container_name}` not found."))

@bot.command(name='suspension-logs')
@is_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def suspension_logs(ctx, container_name: str = None):
    """View suspension logs"""
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
    
    embed = create_info_embed("Suspension Logs", log_text)
    await ctx.send(embed=embed)

@bot.command(name='whitelist-vps')
@is_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def whitelist_vps(ctx, container_name: str, action: str):
    """Whitelist VPS from auto-suspend"""
    action = action.lower()
    if action not in ['add', 'remove']:
        await ctx.send(embed=create_error_embed("Invalid Action", "Use `add` or `remove`."))
        return
    
    found = False
    for user_id, vps_list in vps_data.items():
        for vps in vps_list:
            if vps['container_name'] == container_name:
                if action == 'add':
                    vps['whitelisted'] = True
                    msg = "added to whitelist (exempt from auto-suspension)"
                else:
                    vps['whitelisted'] = False
                    msg = "removed from whitelist"
                save_vps_data()
                
                embed = create_success_embed("Whitelist Updated", f"VPS `{container_name}` {msg}.")
                await ctx.send(embed=embed)
                found = True
                break
        if found:
            break
    
    if not found:
        await ctx.send(embed=create_error_embed("Not Found", f"VPS `{container_name}` not found."))

@bot.command(name='userinfo')
@is_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def user_info(ctx, user: discord.Member):
    """User information with VPS numbers"""
    user_id = str(user.id)
    vps_list = vps_data.get(user_id, [])
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
    stats_info = f"**📨 Invites:** {stats.get('invites', 0)}\n"
    stats_info += f"**🚀 Boosts:** {stats.get('boosts', 0)}\n"
    add_field(embed, "User Stats", stats_info, True)
    
    if vps_list:
        vps_info = []
        for i, vps in enumerate(vps_list, 1):
            status_emoji = EMOJI_ONLINE if vps.get('status') == 'running' and not vps.get('suspended', False) else EMOJI_OFFLINE if vps.get('suspended', False) else EMOJI_OFFLINE
            status_text = vps.get('status', 'unknown').upper()
            if vps.get('suspended', False):
                status_text += " (SUSPENDED)"
            purge_text = " 🛡️" if vps.get('purge_protected', False) else ""
            vps_num = get_vps_number(vps['container_name']) or (i)
            timer_line = get_vps_timer_line(vps)
            vps_info.append(f"{status_emoji} **VPS #{vps_num}:** `{vps['container_name']}` - {status_text}{purge_text}{timer_line}")
        
        vps_nums = sorted([n for n in (get_vps_number(v['container_name']) for v in vps_list) if n is not None])
        range_str = f"<{'>, <'.join(map(str, vps_nums))}>" if vps_nums else "<1>"
        add_field(embed, f"VPS List ({len(vps_list)})", "\n".join(vps_info), False)
        add_field(embed, "Delete Command", f"`{PREFIX}delete-vps {user.id} {range_str} [reason]`\nor `{PREFIX}delete-vps {user.mention} {range_str} [reason]`", False)
        add_field(embed, "Purge Protection", f"Use `{PREFIX}purge-prot {user.mention} <num>` to protect", False)
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

@bot.command(name='exec')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def execute_command(ctx, container_name: str, *, command: str):
    """Execute command in VPS"""
    await ctx.send(embed=create_info_embed("Executing Command", f"Running command in VPS `{container_name}`..."))
    
    try:
        proc = await asyncio.create_subprocess_exec(
            "lxc", "exec", container_name, "--", "bash", "-c", command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        output = stdout.decode() if stdout else "No output"
        error = stderr.decode() if stderr else ""
        
        embed = discord.Embed(
            title=f"Command Output - {container_name}",
            description=f"Command: `{command}`",
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
        
        if output.strip():
            if len(output) > 1000:
                output = output[:1000] + "\n... (truncated)"
            embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Output", value=f"```\n{output}\n```", inline=False)
        
        if error.strip():
            if len(error) > 1000:
                error = error[:1000] + "\n... (truncated)"
            embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Error", value=f"```\n{error}\n```", inline=False)
        
        await ctx.send(embed=embed)
    
    except Exception as e:
        await ctx.send(embed=create_error_embed("Execution Failed", f"Error: {str(e)}"))

@bot.command(name='stop-vps-all')
@is_admin()
@commands.cooldown(1, 30, commands.BucketType.user)
async def stop_all_vps(ctx):
    """Stop all VPS"""
    embed = discord.Embed(
        title=f"{EMOJI_WARNING} Stopping All VPS",
        description="This will stop ALL running VPS on the server.\n\nThis action cannot be undone. Continue?",
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
    
    class ConfirmView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=60)
        
        @discord.ui.button(label="Stop All VPS", style=discord.ButtonStyle.danger)
        async def confirm(self, interaction: discord.Interaction, item: discord.ui.Button):
            await interaction.response.defer()
            try:
                await execute_lxc("lxc stop --all --force")
                
                stopped_count = 0
                for user_id, vps_list in vps_data.items():
                    for vps in vps_list:
                        if vps.get('status') == 'running':
                            vps['status'] = 'stopped'
                            stopped_count += 1
                
                save_vps_data()
                embed = create_success_embed(f"{EMOJI_SUCCESS} All VPS Stopped", f"Successfully stopped {stopped_count} VPS")
                await interaction.followup.send(embed=embed)
            except Exception as e:
                embed = create_error_embed("Stop Failed", str(e))
                await interaction.followup.send(embed=embed)
        
        @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
        async def cancel(self, interaction: discord.Interaction, item: discord.ui.Button):
            embed = create_info_embed("Operation Cancelled", "The stop all VPS operation has been cancelled.")
            await interaction.response.edit_message(embed=embed, view=None)
    
    await ctx.send(embed=embed, view=ConfirmView())

@bot.command(name='migrate-vps')
@is_admin()
@commands.cooldown(1, 30, commands.BucketType.user)
async def migrate_vps(ctx, container_name: str, pool: str):
    """Migrate VPS to another storage pool"""
    await ctx.send(embed=create_info_embed("Migrating VPS", f"Migrating `{container_name}` to pool `{pool}`..."))
    
    try:
        await execute_lxc(f"lxc move {shlex.quote(container_name)} -s {pool}")
        embed = create_success_embed("VPS Migrated", f"VPS `{container_name}` migrated to pool `{pool}`")
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(embed=create_error_embed("Migration Failed", f"Error: {str(e)}"))

@bot.command(name='vps-network')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def vps_network(ctx, container_name: str, action: str, value: str = None):
    """Network management for VPS"""
    actions = ['list', 'limit', 'add', 'remove']
    
    if action not in actions:
        await ctx.send(embed=create_error_embed("Invalid Action", f"Use: {', '.join(actions)}"))
        return
    
    try:
        if action == 'list':
            proc = await asyncio.create_subprocess_exec(
                "lxc", "exec", container_name, "--", "ip", "addr",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                output = stdout.decode()
                if len(output) > 1900:
                    output = output[:1900] + "..."
                embed = create_info_embed(f"Network - {container_name}", f"```\n{output}\n```")
            else:
                embed = create_error_embed("Error", f"Failed to list network interfaces")
        elif action == 'limit' and value:
            await execute_lxc(f"lxc config device set {shlex.quote(container_name)} eth0 limits.egress {value}")
            await execute_lxc(f"lxc config device set {shlex.quote(container_name)} eth0 limits.ingress {value}")
            embed = create_success_embed("Network Limit Set", f"Set network limit to {value} for `{container_name}`")
        else:
            embed = create_error_embed("Invalid Command", "Usage: .vps-network <container> <list|limit> [value]")
        
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(embed=create_error_embed("Network Operation Failed", str(e)))

@bot.command(name='apply-permissions')
@is_admin()
@commands.cooldown(1, 10, commands.BucketType.user)
async def apply_permissions(ctx, container_name: str):
    """Apply Docker-ready permissions to VPS"""
    await ctx.send(embed=create_info_embed("Applying Permissions", f"Applying Docker-ready permissions to `{container_name}`..."))
    
    try:
        await apply_lxc_config(container_name)
        await apply_internal_permissions(container_name)
        embed = create_success_embed("Permissions Applied", f"Docker-ready permissions applied to `{container_name}`")
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(embed=create_error_embed("Failed", f"Error: {str(e)}"))

@bot.command(name='fix-internet')
@is_admin()
@commands.cooldown(1, 60, commands.BucketType.user)
async def fix_internet_command(ctx):
    """Force fix internet for ALL containers — retries until each verifies connectivity"""
    embed = create_info_embed(f"{EMOJI_GLOBAL} Fixing Internet", f"{EMOJI_LOADING} Setting up host networking...")
    msg = await ctx.send(embed=embed)

    try:
        await ensure_lxdbr0()
    except Exception as e:
        logger.error(f"ensure_lxdbr0 failed in fix-internet: {e}")

    try:
        await execute_lxc("lxc profile device add default eth0 nic nictype=bridged parent=lxdbr0", timeout=30)
    except Exception:
        pass

    total = 0
    fixed_ok = 0
    fixed_no_verify = 0
    failed = 0
    results = []

    for user_id, vps_list in list(vps_data.items()):
        for vps in vps_list:
            total += 1
            container = vps['container_name']
            await msg.edit(embed=create_info_embed(
                f"{EMOJI_GLOBAL} Fixing Internet",
                f"{EMOJI_LOADING} Processing `{container}` ({fixed_ok + fixed_no_verify + failed + 1}/{total})..."))
            try:
                ok = await ensure_container_internet(container, max_retries=3)
                if ok and await check_container_internet(container):
                    fixed_ok += 1
                    results.append(f"{EMOJI_ONLINE} `{container}` — fixed")
                elif ok:
                    fixed_no_verify += 1
                    results.append(f"{EMOJI_MID_SIGNAL} `{container}` — applied (unverified)")
                else:
                    failed += 1
                    results.append(f"{EMOJI_CROSS} `{container}` — failed")
            except Exception:
                failed += 1
                results.append(f"{EMOJI_CROSS} `{container}` — error")

    result_text = "\n".join(results[-20:])
    if len(results) > 20:
        result_text = f"... and {len(results) - 20} more\n" + result_text

    await msg.edit(embed=create_success_embed(
        f"{EMOJI_GLOBAL} Internet Fix Complete",
        f"{EMOJI_ONLINE} **Verified working:** {fixed_ok}/{total}\n"
        f"{EMOJI_MID_SIGNAL} **Applied (unverified):** {fixed_no_verify}/{total}\n"
        f"{EMOJI_CROSS} **Failed:** {failed}/{total}\n\n"
        f"**Per-container:**\n{result_text}"
    ))

    await send_log(EMOJI_GLOBAL, "Internet Fix Applied",
        f"{EMOJI_ADMIN} **Admin:** {ctx.author.mention}\n"
        f"{EMOJI_ONLINE} **Verified:** {fixed_ok}/{total}\n"
        f"{EMOJI_MID_SIGNAL} **Unverified:** {fixed_no_verify}/{total}\n"
        f"{EMOJI_CROSS} **Failed:** {failed}",
        color=0x00ff88)

# ==================================================== OTHER COMMANDS END =====================================================

# ==================================================== SYSTEM COMMANDS =====================================================

@bot.command(name='thresholds')
@is_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def thresholds(ctx):
    """Show current resource thresholds"""
    embed = create_info_embed("Resource Thresholds", f"**CPU:** {CPU_THRESHOLD}%\n**RAM:** {RAM_THRESHOLD}%")
    await ctx.send(embed=embed)

@bot.command(name='set-threshold')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def set_threshold(ctx, cpu: int, ram: int):
    """Set resource thresholds"""
    global CPU_THRESHOLD, RAM_THRESHOLD
    
    if cpu < 0 or ram < 0:
        await ctx.send(embed=create_error_embed("Invalid Thresholds", "Thresholds must be non-negative."))
        return
    
    CPU_THRESHOLD = cpu
    RAM_THRESHOLD = ram
    set_setting('cpu_threshold', str(cpu))
    set_setting('ram_threshold', str(ram))
    
    embed = create_success_embed("Thresholds Updated", f"**CPU:** {cpu}%\n**RAM:** {ram}%")
    await ctx.send(embed=embed)

@bot.command(name='check-resources')
@is_admin()
@commands.cooldown(1, 10, commands.BucketType.user)
async def check_resources_command(ctx):
    """Check available host resources (RAM, CPU, Disk)"""
    msg = await ctx.send(embed=create_info_embed("Checking Resources", f"{EMOJI_LOADING} Gathering resource information..."))
    
    resources = await get_available_resources()
    
    embed = discord.Embed(
        title=f"{EMOJI_STATS} Host Resource Overview",
        description="Current resource availability on the host machine",
        color=0x00ccff
    )
    
    if THUMBNAIL_URL:
        embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_footer(
        text=f"{BOT_NAME} VPS Manager • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        icon_url=THUMBNAIL_URL
    )
    
    cpu_val = (
        f"**Total:** {resources['cpu']['total']} cores\n"
        f"**Allocated to VPS:** {resources['cpu']['allocated']} cores\n"
        f"**Available:** {resources['cpu']['available']} cores\n"
        f"{EMOJI_GOOD_SIGNAL if resources['cpu']['available'] > 0 else EMOJI_BAD_SIGNAL} "
        f"{'Resources available' if resources['cpu']['available'] > 0 else 'Fully allocated'}"
    )
    embed.add_field(name=f"{EMOJI_CPU} CPU", value=cpu_val, inline=True)
    
    ram_val = (
        f"**Total:** {resources['ram']['total_gb']}GB\n"
        f"**Allocated to VPS:** {resources['ram']['allocated_gb']}GB\n"
        f"**Available:** {resources['ram']['available_gb']}GB\n"
        f"{EMOJI_GOOD_SIGNAL if resources['ram']['available_gb'] > 0 else EMOJI_BAD_SIGNAL} "
        f"{'Resources available' if resources['ram']['available_gb'] > 0 else 'Fully allocated'}"
    )
    embed.add_field(name=f"{EMOJI_RAM} RAM", value=ram_val, inline=True)
    
    disk_val = (
        f"**Total:** {resources['disk']['total_gb']}GB\n"
        f"**Allocated to VPS:** {resources['disk']['allocated_gb']}GB\n"
        f"**Used:** {resources['disk']['used_gb']}GB\n"
        f"**Free:** {resources['disk']['available_gb']}GB\n"
        f"{EMOJI_GOOD_SIGNAL if resources['disk']['available_gb'] > 0 else EMOJI_BAD_SIGNAL} "
        f"{'Space available' if resources['disk']['available_gb'] > 0 else 'Disk full'}"
    )
    embed.add_field(name=f"{EMOJI_DISK} Storage", value=disk_val, inline=True)
    
    await msg.edit(embed=embed)

@bot.command(name='lxc-list')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def lxc_list(ctx):
    """List all LXC containers"""
    try:
        result = await execute_lxc("lxc list")
        embed = create_info_embed("LXC Containers List", f"```\n{result}\n```")
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(embed=create_error_embed("Error", str(e)))

@bot.command(name='set-status')
@is_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def set_status(ctx, activity_type: str, *, name: str):
    """Set bot status"""
    types = {
        'playing': discord.ActivityType.playing,
        'watching': discord.ActivityType.watching,
        'listening': discord.ActivityType.listening,
    }
    
    if activity_type.lower() not in types:
        await ctx.send(embed=create_error_embed("Invalid Type", "Valid types: playing, watching, listening"))
        return
    
    await bot.change_presence(activity=discord.Activity(type=types[activity_type.lower()], name=name))
    set_setting('bot_activity', activity_type.lower())
    set_setting('bot_activity_name', name)
    
    embed = create_success_embed("Status Updated", f"Set to {activity_type}: {name}")
    await ctx.send(embed=embed)

@bot.command(name='change-mode')
@is_main_admin()
@commands.cooldown(1, 5, commands.BucketType.user)
async def change_mode(ctx, mode: str):
    """Change bot mode"""
    modes = {
        'online': discord.Status.online,
        'idle': discord.Status.idle,
        'dnd': discord.Status.dnd,
    }
    
    if mode.lower() not in modes:
        await ctx.send(embed=create_error_embed("Invalid Mode", "Valid modes: online, idle, dnd"))
        return
    
    await bot.change_presence(status=modes[mode.lower()])
    set_setting('bot_status', mode.lower())
    
    embed = create_success_embed("Mode Changed", f"Bot mode set to {mode}")
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

@bot.command(name='purge-data')
@is_main_admin()
@commands.cooldown(1, 60, commands.BucketType.user)
async def purge_data(ctx, user: discord.Member):
    """Purge all data for a user"""
    user_id = str(user.id)
    
    if user_id not in vps_data:
        await ctx.send(embed=create_error_embed("No Data", f"{user.mention} has no VPS data."))
        return
    
    embed = discord.Embed(
        title=f"{EMOJI_WARNING} Purge Data",
        description=f"This will permanently delete ALL VPS data for {user.mention}.\n"
                    f"This action CANNOT be undone!\n\n"
                    f"**VPS Count:** {len(vps_data[user_id])}\n\n"
                    f"Type `{PREFIX}confirm-purge {user.id}` to proceed.",
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
    
    await ctx.send(embed=embed)

@bot.command(name='confirm-purge')
@is_main_admin()
@commands.cooldown(1, 60, commands.BucketType.user)
async def confirm_purge(ctx, user_id: str):
    """Confirm purge of user data"""
    try:
        user = await bot.fetch_user(int(user_id))
    except:
        user = None
    
    if user_id not in vps_data:
        await ctx.send(embed=create_error_embed("No Data", f"User ID {user_id} has no VPS data."))
        return
    
    deleted_count = 0
    for vps in vps_data[user_id][:]:
        try:
            # Delete the container (tolerate "already gone")
            try:
                await execute_lxc(f"lxc delete {shlex.quote(vps['container_name'])} --force")
            except Exception as e:
                if "not found" not in str(e).lower():
                    raise
                logger.warning(f"Container {vps['container_name']} already gone, cleaning up DB")
            
            # Delete port forwards and vps record
            conn = get_db()
            cur = conn.cursor()
            cur.execute('DELETE FROM port_forwards WHERE vps_container = ?', (vps['container_name'],))
            cur.execute('DELETE FROM vps WHERE container_name = ?', (vps['container_name'],))
            conn.commit()
            conn.close()
            
            deleted_count += 1
            await asyncio.sleep(1)  # Small delay to prevent overload
        except Exception as e:
            logger.error(f"Failed to delete {vps['container_name']}: {e}")
    
    del vps_data[user_id]
    save_vps_data()
    
    embed = create_success_embed("Data Purged", 
        f"Successfully purged data for {user.mention if user else f'User {user_id}'}\n"
        f"Deleted {deleted_count} VPS containers.")
    await ctx.send(embed=embed)

# ==================================================== SYSTEM COMMANDS END =====================================================

# ==================================================== PORT FORWARDING COMMANDS =====================================================

@bot.command(name='ports')
@commands.cooldown(1, 2, commands.BucketType.user)
async def ports_command(ctx, subcmd: str = None, *args):
    """Manage port forwarding"""
    if not await maintenance_check(ctx):
        return
    
    user_id = str(ctx.author.id)
    allocated = get_user_allocation(user_id)
    used = get_user_used_ports(user_id)
    available = allocated - used
    
    if subcmd is None:
        embed = create_info_embed("Port Forwarding Help", f"**Your Quota:** Allocated: {allocated}, Used: {used}, Available: {available}")
        add_field(embed, "Commands", 
                 f"{PREFIX}ports add <vps_num> <vps_port>\n{PREFIX}ports list\n{PREFIX}ports remove <id>", 
                 False)
        await ctx.send(embed=embed)
        return
    
    if subcmd == 'add':
        if len(args) < 2:
            await ctx.send(embed=create_error_embed("Usage", f"Usage: {PREFIX}ports add <vps_number> <vps_port>"))
            return
        
        try:
            vps_num = int(args[0])
            vps_port = int(args[1])
            if vps_port < 1 or vps_port > 65535:
                raise ValueError
        except ValueError:
            await ctx.send(embed=create_error_embed("Invalid Input", "VPS number and port must be positive integers (port: 1-65535)."))
            return
        
        vps = get_vps_by_number(user_id, vps_num)
        if not vps:
            await ctx.send(embed=create_error_embed("Invalid VPS", f"No VPS with number #{vps_num}. Use {PREFIX}myvps to list."))
            return
        container = vps['container_name']
        
        if used >= allocated:
            await ctx.send(embed=create_error_embed("Quota Exceeded", f"No available slots. Allocated: {allocated}, Used: {used}. Contact admin for more."))
            return
        
        host_port = await create_port_forward(user_id, container, vps_port)
        if host_port:
            embed = create_success_embed("Port Forward Created", 
                f"VPS #{vps_num} port {vps_port} (TCP/UDP) forwarded to host port {host_port}.")
            add_field(embed, "Access", f"External: {YOUR_SERVER_IP}:{host_port} → VPS:{vps_port} (TCP & UDP)", False)
            add_field(embed, "Quota Update", f"Used: {used + 1}/{allocated}", False)
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=create_error_embed("Failed", "Could not assign host port. Try again later."))
    
    elif subcmd == 'list':
        forwards = get_user_forwards(user_id)
        embed = create_info_embed("Your Port Forwards", f"**Quota:** Allocated: {allocated}, Used: {used}, Available: {available}")
        
        if not forwards:
            add_field(embed, "Forwards", "No active port forwards.", False)
        else:
            text = []
            for f in forwards:
                vps_num = get_vps_number(f['vps_container']) or 'Unknown'
                created = datetime.fromisoformat(f['created_at']).strftime('%Y-%m-%d %H:%M')
                text.append(f"**ID {f['id']}** - VPS #{vps_num}: {f['vps_port']} (TCP/UDP) → {f['host_port']} (Created: {created})")
            
            add_field(embed, "Active Forwards", "\n".join(text[:10]), False)
            if len(forwards) > 10:
                add_field(embed, "Note", f"Showing 10 of {len(forwards)}. Remove unused with {PREFIX}ports remove <id>.", False)
        
        await ctx.send(embed=embed)
    
    elif subcmd == 'remove':
        if len(args) < 1:
            await ctx.send(embed=create_error_embed("Usage", f"Usage: {PREFIX}ports remove <forward_id>"))
            return
        
        try:
            fid = int(args[0])
        except ValueError:
            await ctx.send(embed=create_error_embed("Invalid ID", "Forward ID must be an integer."))
            return
        
        success, _ = await remove_port_forward(fid)
        if success:
            embed = create_success_embed("Removed", f"Port forward {fid} removed (TCP & UDP).")
            add_field(embed, "Quota Update", f"Used: {used - 1}/{allocated}", False)
            await ctx.send(embed=embed)
        else:
            await ctx.send(embed=create_error_embed("Not Found", "Forward ID not found. Use .ports list."))
    
    else:
        await ctx.send(embed=create_error_embed("Invalid Subcommand", f"Use: add <vps_num> <port>, list, remove <id>"))

@bot.command(name='ports-add-user')
@is_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def ports_add_user(ctx, amount: int, user: discord.Member):
    """Allocate port slots to a user"""
    if amount <= 0:
        await ctx.send(embed=create_error_embed("Invalid Amount", "Amount must be a positive integer."))
        return
    
    user_id = str(user.id)
    allocate_ports(user_id, amount)
    
    embed = create_success_embed("Ports Allocated", f"Allocated {amount} port slots to {user.mention}.")
    add_field(embed, "Quota", f"Total: {get_user_allocation(user_id)} slots", False)
    await ctx.send(embed=embed)
    await send_log(EMOJI_PORTS, "Port Slots Allocated", f"User: {user.mention} | Amount: {amount} | Admin: {ctx.author.mention}", color=0x00ff88)
    
    try:
        dm_embed = create_info_embed("Port Slots Allocated", 
            f"You have been granted {amount} additional port forwarding slots by an admin.\nUse `{PREFIX}ports list` to view your quota and active forwards.")
        await user.send(embed=dm_embed)
    except discord.Forbidden:
        await ctx.send(embed=create_info_embed("DM Failed", f"Could not notify {user.mention} via DM."))

@bot.command(name='ports-remove-user')
@is_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def ports_remove_user(ctx, amount: int, user: discord.Member):
    """Deallocate port slots from a user"""
    if amount <= 0:
        await ctx.send(embed=create_error_embed("Invalid Amount", "Amount must be a positive integer."))
        return
    
    user_id = str(user.id)
    current = get_user_allocation(user_id)
    if amount > current:
        amount = current
    
    deallocate_ports(user_id, amount)
    remaining = get_user_allocation(user_id)
    
    embed = create_success_embed("Ports Deallocated", f"Removed {amount} port slots from {user.mention}.")
    add_field(embed, "Remaining Quota", f"{remaining} slots", False)
    await ctx.send(embed=embed)
    await send_log(EMOJI_PORTS, "Port Slots Deallocated", f"User: {user.mention} | Amount: {amount} | Admin: {ctx.author.mention}", color=0xffaa00)
    
    try:
        dm_embed = create_warning_embed("Port Slots Reduced", 
            f"Your port forwarding quota has been reduced by {amount} slots by an admin.\nRemaining: {remaining} slots.")
        await user.send(embed=dm_embed)
    except discord.Forbidden:
        await ctx.send(embed=create_info_embed("DM Failed", f"Could not notify {user.mention} via DM."))

@bot.command(name='ports-revoke')
@is_admin()
@commands.cooldown(1, 3, commands.BucketType.user)
async def ports_revoke(ctx, forward_id: int):
    """Revoke a port forward"""
    success, user_id = await remove_port_forward(forward_id, is_admin=True)
    if success and user_id:
        try:
            user = await bot.fetch_user(int(user_id))
            dm_embed = create_warning_embed("Port Forward Revoked", 
                f"One of your port forwards (ID: {forward_id}) has been revoked by an admin.")
            await user.send(embed=dm_embed)
        except:
            pass
        embed = create_success_embed("Revoked", f"Port forward ID {forward_id} revoked.")
        await ctx.send(embed=embed)
        await send_log(EMOJI_PORTS, "Port Forward Revoked", f"Forward ID: `{forward_id}` | Admin: {ctx.author.mention} | User: <@{user_id}>", color=0xff3366)
    else:
        await ctx.send(embed=create_error_embed("Failed", "Port forward ID not found or removal failed."))

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


@bot.command(name='machine-status')
@is_admin()
async def machine_status(ctx, *, flag: str = None):
    """Show real-time machine status updating every 1s. Use '24-7' for 24/7 mode."""
    is_24_7 = flag and flag.lower().replace('-', '').replace('_', '').replace(' ', '') in ['247', '24 7']

    initial_embed = create_info_embed(
        f"{EMOJI_STATS} Machine Status",
        f"{EMOJI_LOADING} Gathering system information..."
    )
    msg = await ctx.send(embed=initial_embed)

    mode_label = f"{EMOJI_GLOBAL} 24/7" if is_24_7 else f"{EMOJI_UPTIME} 1 Hour"
    start_time = time.time()
    max_elapsed = None if is_24_7 else 3600

    while True:
        elapsed = time.time() - start_time
        if max_elapsed and elapsed > max_elapsed:
            break

        info = await _gather_machine_info()

        cpu_usage = float(info.get('cpu_usage', '0'))
        mem_pct = float(info.get('mem_pct', '0'))

        embed = discord.Embed(
            title=f"{EMOJI_STATS} Machine Status",
            description=f"{EMOJI_ONLINE} **Real-time system monitoring**\n"
                        f"{EMOJI_INFO} **Mode:** {mode_label} | "
                        f"{EMOJI_UPTIME} **Elapsed:** {format_uptime_str(str(int(elapsed)))}",
            color=0x00ccff
        )

        if THUMBNAIL_URL:
            embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.set_footer(
            text=f"{BOT_NAME} VPS Manager • Updates every 1s",
            icon_url=THUMBNAIL_URL
        )

        sys_val = (
            f"**OS:** {info.get('os', 'Unknown')}\n"
            f"**Kernel:** {info.get('kernel', 'Unknown')}\n"
            f"**Hostname:** {info.get('hostname', 'Unknown')}\n"
            f"**Arch:** {info.get('arch', 'Unknown')}"
        )
        embed.add_field(name=f"{EMOJI_ARROW_RIGHT} System", value=sys_val, inline=False)

        cpu_val = (
            f"**Model:** {info.get('cpu_model', 'Unknown')}\n"
            f"**Cores:** {info.get('cpu_cores', '0')}\n"
            f"**Usage:** {cpu_usage:.1f}%\n"
            f"**Load:** {info.get('load_avg', '0 0 0')}"
        )
        embed.add_field(name=f"{EMOJI_ARROW_RIGHT} CPU", value=cpu_val, inline=True)

        gpu_val = info.get('gpu', 'No GPU detected')
        embed.add_field(name=f"{EMOJI_ARROW_RIGHT} GPU", value=gpu_val, inline=True)

        mem_val = (
            f"**Total:** {info.get('mem_total', '0')}\n"
            f"**Used:** {info.get('mem_used', '0')}\n"
            f"**Available:** {info.get('mem_avail', '0')}\n"
            f"**Usage:** {mem_pct:.1f}%"
        )
        embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Memory", value=mem_val, inline=True)

        disk_val = (
            f"**Total:** {info.get('disk_total', '0')}\n"
            f"**Used:** {info.get('disk_used', '0')}\n"
            f"**Available:** {info.get('disk_avail', '0')}\n"
            f"**Usage:** {info.get('disk_pct', '0%')}"
        )
        embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Storage", value=disk_val, inline=True)

        embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Uptime", value=info.get('uptime', 'Unknown'), inline=True)
        embed.add_field(name=f"{EMOJI_ARROW_RIGHT} Network", value=f"**Public IP:** {info.get('public_ip', 'Unknown')}", inline=True)

        try:
            await msg.edit(embed=embed)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            break

        await asyncio.sleep(1)

# ==================================================== MACHINE STATUS COMMAND END =====================================================

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
                f"**`{PREFIX}ping`** - Check bot latency with detailed report",
                f"**`{PREFIX}uptime`** - Show host uptime",
                f"**`{PREFIX}plans`** - View free VPS plans with emojis",
                f"**`{PREFIX}freeplans`** - Free plans list",
                f"**`{PREFIX}stats`** - View your invite/boost stats",
                f"**`{PREFIX}myvps`** - List your VPS",
                f"**`{PREFIX}list`** - Detailed VPS list",
                f"**`{PREFIX}manage`** - Manage your VPS (with modern reinstall)",
                f"**`{PREFIX}claimfree inv <1-6>`** - Claim invite VPS",
                f"**`{PREFIX}claimfree boost <1-5>`** - Claim boost VPS",
                f"**`{PREFIX}share-user @user <vps_number>`** - Share VPS access",
                f"**`{PREFIX}share-ruser @user <vps_number>`** - Revoke VPS access",
                f"**`{PREFIX}manage-shared @owner <vps_number>`** - Manage shared VPS"
            ]
            total = 13
            
        elif self.current_category == "vps":
            embed = discord.Embed(
                title=f"{EMOJI_HELP} {BOT_NAME} Help - {EMOJI_VPS} VPS Management",
                description="Commands for managing your VPS",
                color=color
            )
            commands = [
                f"**`{PREFIX}myvps`** - List your VPS",
                f"**`{PREFIX}list`** - Detailed VPS list",
                f"**`{PREFIX}manage`** - Manage your VPS (with modern reinstall)",
                f"**`{PREFIX}manage @user`** - Manage another user's VPS (Admin)",
                f"**`{PREFIX}vpsinfo [container]`** - VPS information (Admin)",
                f"**`{PREFIX}vps-stats <container>`** - VPS stats (Admin)",
                f"**`{PREFIX}restart-vps <container>`** - Restart VPS (Admin)",
                f"**`{PREFIX}clone-vps <container> [new_name]`** - Clone VPS (Admin)",
                f"**`{PREFIX}snapshot <container> [snap_name]`** - Create snapshot (Admin)",
                f"**`{PREFIX}restore-backup <container> <snap_name>`** - Restore VPS (Admin)"
            ]
            total = 10
            
        elif self.current_category == "ports":
            embed = discord.Embed(
                title=f"{EMOJI_HELP} {BOT_NAME} Help - {EMOJI_PORTS} Port Forwarding",
                description="Manage port forwarding for your VPS",
                color=color
            )
            commands = [
                f"**`{PREFIX}ports`** - Port forwarding help",
                f"**`{PREFIX}ports add <vps_num> <port>`** - Add port forward",
                f"**`{PREFIX}ports list`** - List your port forwards",
                f"**`{PREFIX}ports remove <id>`** - Remove port forward",
                f"**`{PREFIX}ports-add-user <amount> @user`** - Allocate ports (Admin)",
                f"**`{PREFIX}ports-remove-user <amount> @user`** - Deallocate ports (Admin)",
                f"**`{PREFIX}ports-revoke <id>`** - Revoke port forward (Admin)"
            ]
            total = 7
            
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
                f"**`{PREFIX}ping`** - Check bot latency with detailed report",
                f"**`{PREFIX}uptime`** - Show host uptime",
                f"**`{PREFIX}serverstats`** - Server statistics (Admin)",
                f"**`{PREFIX}thresholds`** - View resource thresholds",
                f"**`{PREFIX}set-threshold <cpu> <ram>`** - Set thresholds (Admin)",
                f"**`{PREFIX}set-status <type> <name>`** - Set bot status (Admin)",
                f"**`{PREFIX}change-mode <mode>`** - Change bot mode (Main Admin)",
                f"**`{PREFIX}maintenance <on/off>`** - Maintenance mode (Main Admin)",
                f"**`{PREFIX}lxc-list`** - List all LXC containers (Admin)"
            ]
            total = 9
            
        elif self.current_category == "admin":
            embed = discord.Embed(
                title=f"{EMOJI_HELP} {BOT_NAME} Help - {EMOJI_ADMIN} Admin Commands",
                description="Commands for server administrators",
                color=color
            )
            commands = [
                f"**`{PREFIX}create <ram> <cpu> <disk> <time> @user [flags]`** - Create VPS (flags: `--bypass_cpu`, `--bypass_ram`, `--bypass_disk`, `--bypass_all`; multiple can be combined)",
                f"**`{PREFIX}renew-vps <container> <time> [reason] [--force]`** - Renew/force-renew VPS timer",
                f"**`{PREFIX}delete-vps @user/<id> <vps_number> [reason]`** - Delete VPS (with confirmation)",
                f"**`{PREFIX}add-resources <container> [ram] [cpu] [disk]`** - Add resources",
                f"**`{PREFIX}resize-vps <container> [ram] [cpu] [disk]`** - Resize VPS",
                f"**`{PREFIX}suspend-vps <container> [reason]`** - Suspend VPS",
                f"**`{PREFIX}unsuspend-vps <container>`** - Unsuspend VPS",
                f"**`{PREFIX}suspension-logs [container]`** - View suspension logs",
                f"**`{PREFIX}whitelist-vps <container> <add|remove>`** - Whitelist VPS",
                f"**`{PREFIX}userinfo @user`** - User information",
                f"**`{PREFIX}list-all`** - List all VPS (detailed)",
                f"**`{PREFIX}exec <container> <command>`** - Execute command",
                f"**`{PREFIX}stop-vps-all`** - Stop all VPS",
                f"**`{PREFIX}restart-vps <container>`** - Restart VPS",
                f"**`{PREFIX}clone-vps <container> [new_name]`** - Clone VPS",
                f"**`{PREFIX}snapshot <container> [snap_name]`** - Create snapshot",
                f"**`{PREFIX}restore-backup <container> <snap_name>`** - Restore backup",
                f"**`{PREFIX}vpsinfo [container]`** - VPS information",
                f"**`{PREFIX}vps-stats <container>`** - VPS stats",
                f"**`{PREFIX}apply-permissions <container>`** - Apply Docker permissions",
                f"**`{PREFIX}check-resources`** - Check available host resources (RAM/CPU/Disk)",
                f"**`{PREFIX}machine-status [24-7]`** - Live machine status (updates every 1s, 1hr max or 24/7)",
                f"**`{PREFIX}fix-internet`** - Fix internet for all containers (NAT/DHCP/DNS)",
                f"**`{PREFIX}invite-logs [@user]`** - View invite tracking logs",
                f"**`{PREFIX}boost-logs [@user]`** - View boost tracking logs"
            ]
            total = 25
            
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
                f"**`{PREFIX}set-status <type> <name>`** - Set bot status",
                f"**`{PREFIX}change-mode <mode>`** - Change bot mode",
                f"**`{PREFIX}purge-data @user`** - Purge user data",
                f"**`{PREFIX}confirm-purge <user_id>`** - Confirm purge",
                f"**`{PREFIX}purge-prot @user [vps_num]`** - Protect VPS from purge",
                f"**`{PREFIX}purge-remove-prot @user [vps_num]`** - Remove purge protection",
                f"**`{PREFIX}purge-list-protected`** - List protected VPS",
                f"**`{PREFIX}purge-vm-all`** - Purge ALL unprotected VPS (1 by 1)",
                f"**`{PREFIX}confirm-purge-all`** - Confirm purge all unprotected VPS"
            ]
            total = 13
            
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

@bot.command(name='commands')
@commands.cooldown(1, 3, commands.BucketType.user)
async def commands_alias(ctx):
    """Alias for help command"""
    await help_command(ctx)

# ==================================================== HELP SYSTEM END =====================================================

# ==================================================== TYPO HANDLING =====================================================

@bot.command(name='mangage')
async def manage_typo(ctx):
    """Handle typo for manage command"""
    embed = create_info_embed("Command Correction", f"Did you mean `{PREFIX}manage`? Use the correct command.")
    await ctx.send(embed=embed)

# ==================================================== TYPO HANDLING END =====================================================

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

async def _ensure_dnsmasq():
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
            f"--dhcp-range={LXD_BRIDGE_IP[:-1]}2,{LXD_BRIDGE_IP[:-1]}254,1h",
            f"--dhcp-option=3,{LXD_BRIDGE_IP}",
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
    if not await _bridge_exists(LXD_BRIDGE):
        logger.info(f"{LXD_BRIDGE} not found, creating...")
        try:
            proc = await asyncio.create_subprocess_exec(
                "lxc", "network", "create", LXD_BRIDGE, "--type=bridge",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            if proc.returncode == 0:
                await asyncio.sleep(2)
            else:
                logger.warning("lxc network create lxdbr0 failed, falling back to manual bridge")
                raise Exception("lxc network create failed")
        except Exception:
            for attempt in range(3):
                try:
                    proc = await asyncio.create_subprocess_exec(
                        "ip", "link", "add", LXD_BRIDGE, "type", "bridge",
                        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                    )
                    await proc.communicate()
                    if proc.returncode == 0:
                        break
                except Exception:
                    pass
                await asyncio.sleep(1)

    try:
        proc = await asyncio.create_subprocess_exec(
            "ip", "addr", "add", f"{LXD_BRIDGE_IP}/24", "dev", LXD_BRIDGE,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
    except Exception:
        pass

    try:
        proc = await asyncio.create_subprocess_exec(
            "ip", "link", "set", LXD_BRIDGE, "up",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
    except Exception:
        pass

    await _ensure_dnsmasq()

    try:
        proc = await asyncio.create_subprocess_exec(
            "sysctl", "-w", "net.ipv4.ip_forward=1",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
    except Exception:
        pass

    for table, rule in [
        ("nat", f"-C POSTROUTING -s {LXD_BRIDGE_NET} ! -d {LXD_BRIDGE_NET} -j MASQUERADE"),
        ("nat", f"-A POSTROUTING -s {LXD_BRIDGE_NET} ! -d {LXD_BRIDGE_NET} -j MASQUERADE"),
        ("filter", f"-C FORWARD -i {LXD_BRIDGE} -j ACCEPT"),
        ("filter", f"-A FORWARD -i {LXD_BRIDGE} -j ACCEPT"),
        ("filter", f"-C FORWARD -o {LXD_BRIDGE} -j ACCEPT"),
        ("filter", f"-A FORWARD -o {LXD_BRIDGE} -j ACCEPT"),
    ]:
        try:
            proc = await asyncio.create_subprocess_exec(
                "iptables", "-t", table, *rule.split(),
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
        except Exception:
            pass

    logger.info(f"{LXD_BRIDGE} bridge verified/created")

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
    try:
        await get_available_os_options()
    except Exception as e:
        logger.error(f"Failed to check available OS images: {e}")
    await ensure_lxdbr0()
    await sync_container_states()
    bot.loop.create_task(check_expired_vps())
    bot.loop.create_task(auto_delete_suspended_vps())
    bot.loop.create_task(restore_ipv4_tunnels())
    bot.loop.create_task(restore_fm_tunnels())
bot.setup_hook = on_bot_startup

if __name__ == "__main__":
    if DISCORD_TOKEN:
        import asyncio
        try:
            asyncio.run(fetch_emoji_ids())
        except Exception as e:
            logger.error(f"Failed to fetch emoji IDs: {e}")
        bot.run(DISCORD_TOKEN)
    else:
        logger.error("No Discord token found. Please set DISCORD_TOKEN in the configuration.")

# ==================================================== RUN THE BOT END =====================================================
