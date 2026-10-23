#!/usr/bin/env python3
# ╔══════════════════════════════════════════════════════════════════════════╗
# ║          SGM NODE API  —  Remote LXD control plane for SGM-ORG-LTD-V     ║
# ║   One port • many endpoints • API-key auth • no bot, no bloat            ║
# ╚══════════════════════════════════════════════════════════════════════════╝
#
# Every operation runs locally through the `lxc` CLI and is exposed over HTTP
# so the central Discord bot can drive this host remotely.
#
# Auth: send header   X-API-Key: <key>      (or)   Authorization: Bearer <key>
#
import os
import re
import json
import time
import shlex
import socket
import asyncio
import shutil
import platform
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Depends, Header, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────────────────────────────────────
NODE_DIR   = os.environ.get("SGM_NODE_DIR", "/opt/SGM-NODE")
BIND_HOST  = os.environ.get("SGM_BIND_HOST", "0.0.0.0")
PORT       = int(os.environ.get("SGM_NODE_PORT", "6342"))
STORAGE_POOL = os.environ.get("SGM_STORAGE_POOL", "quota")
FALLBACK_POOL = "default"
VERSION    = "1.0.0"
PORT_RANGE_START = int(os.environ.get("SGM_PORT_RANGE_START", "20000"))
PORT_RANGE_END   = int(os.environ.get("SGM_PORT_RANGE_END", "50000"))


def _read(path: str, default: str = "") -> str:
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except Exception:
        return default


API_KEY   = os.environ.get("SGM_API_KEY") or _read(os.path.join(NODE_DIR, "api-key"))
NODE_ID   = os.environ.get("SGM_NODE_ID") or _read(os.path.join(NODE_DIR, "node-id")) or "node"
NODE_NAME = os.environ.get("SGM_NODE_NAME") or _read(os.path.join(NODE_DIR, "node-name")) \
            or socket.gethostname()

app = FastAPI(title="SGM Node API", version=VERSION, docs_url=None, redoc_url=None)


# ─────────────────────────────────────────────────────────────────────────────
#  AUTH
# ─────────────────────────────────────────────────────────────────────────────
async def require_key(
    x_api_key: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
):
    provided = x_api_key
    if not provided and authorization and authorization.lower().startswith("bearer "):
        provided = authorization[7:].strip()
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Node API key not configured")
    if not provided or provided != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True


# ─────────────────────────────────────────────────────────────────────────────
#  LOW-LEVEL EXEC
# ─────────────────────────────────────────────────────────────────────────────
async def _run(*args: str, timeout: int = 120, input_data: Optional[bytes] = None):
    proc = await asyncio.create_subprocess_exec(
        *args,
        stdin=asyncio.subprocess.PIPE if input_data is not None else None,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        out, err = await asyncio.wait_for(proc.communicate(input=input_data), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise RuntimeError(f"Command timed out after {timeout}s: {' '.join(args)}")
    return proc.returncode, out.decode(errors="replace").strip(), err.decode(errors="replace").strip()


async def _lxc(*args: str, timeout: int = 120) -> str:
    rc, out, err = await _run("lxc", *args, timeout=timeout)
    if rc != 0:
        raise RuntimeError(err or out or f"lxc {' '.join(args)} failed")
    return out


async def _lxc_ok(*args: str, timeout: int = 120) -> bool:
    rc, _, _ = await _run("lxc", *args, timeout=timeout)
    return rc == 0


async def _host(script: str, timeout: int = 60):
    return await _run("bash", "-c", script, timeout=timeout)


# ─────────────────────────────────────────────────────────────────────────────
#  RESOURCE HELPERS (decimals supported, matches the bot)
# ─────────────────────────────────────────────────────────────────────────────
def _to_num(value) -> float:
    if value is None:
        return 0.0
    s = str(value).strip().lower()
    factor = 1.0
    if s.endswith("gib"):
        s = s[:-3]
    elif s.endswith("gb"):
        s = s[:-2]
    elif s.endswith("mib"):
        s = s[:-3]; factor = 1.0 / 1024.0
    elif s.endswith("mb"):
        s = s[:-2]; factor = 1.0 / 1024.0
    elif s.endswith("kib"):
        s = s[:-3]; factor = 1.0 / (1024.0 * 1024.0)
    elif s.endswith("kb"):
        s = s[:-2]; factor = 1.0 / (1024.0 * 1024.0)
    try:
        return float(s.strip()) * factor
    except ValueError:
        return 0.0


def _fmt_num(value) -> str:
    try:
        f = float(value)
    except (TypeError, ValueError):
        return str(value)
    if f == int(f):
        return str(int(f))
    return "%g" % f


def _mem_mb(ram_gb) -> int:
    return max(1, int(round(float(ram_gb) * 1024)))


def _disk_mb(disk_gb) -> int:
    return max(1, int(round(float(disk_gb) * 1024)))


def _cpu_limits(cpu_cores):
    c = float(cpu_cores)
    if c <= 0:
        c = 1.0
    whole = int(c)
    if float(whole) == c:
        return str(whole), None
    return str(whole + 1), f"{int(round(c * 100))}ms/100ms"


def _fmt_bytes(num) -> str:
    try:
        num = float(num)
    except (TypeError, ValueError):
        return "0B"
    for unit in ("B", "K", "M", "G", "T", "P"):
        if abs(num) < 1024.0:
            return f"{num:.0f}{unit}" if unit == "B" else f"{num:.1f}{unit}"
        num /= 1024.0
    return f"{num:.1f}E"


def _fmt_uptime(seconds) -> str:
    try:
        seconds = int(float(seconds))
    except (TypeError, ValueError):
        return "Unknown"
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if secs or not parts:
        parts.append(f"{secs}s")
    return " ".join(parts)


_UNIT_TO_GIB = {"B": 1 / (1024 ** 3), "KiB": 1 / (1024 ** 2), "MiB": 1 / 1024,
                "GiB": 1.0, "TiB": 1024.0}


def _size_to_gib(value, unit) -> int:
    if unit in ("GB", "MB", "KB", "B"):
        factor = {"B": 1 / (1024 ** 3), "KB": 1 / (1024 ** 2), "MB": 1 / 1024, "GB": 1.0}[unit]
        return int(float(value) * factor)
    return int(float(value) * _UNIT_TO_GIB.get(unit, 1.0))


# ─────────────────────────────────────────────────────────────────────────────
#  CONTAINER HELPERS
# ─────────────────────────────────────────────────────────────────────────────
async def container_exists(name: str) -> bool:
    return await _lxc_ok("info", name, timeout=15)


async def container_status(name: str) -> str:
    rc, out, _ = await _run("lxc", "info", name, timeout=15)
    if rc != 0:
        return "unknown"
    for line in out.splitlines():
        if line.startswith("Status: "):
            return line.split(": ", 1)[1].strip().lower()
    return "unknown"


async def container_ip(name: str) -> Optional[str]:
    try:
        data = json.loads(await _lxc("query", f"/1.0/instances/{name}/state", timeout=20))
    except Exception:
        return None
    for dev, info in (data.get("network") or {}).items():
        if dev == "lo":
            continue
        for addr in info.get("addresses", []):
            if addr.get("family") == "inet" and addr.get("scope") == "global":
                return addr.get("address")
    return None


async def apply_resource_limits(name: str, ram_gb=None, cpu_cores=None, disk_gb=None):
    qn = shlex.quote(name)
    if ram_gb is not None:
        await _lxc("config", "set", name, "limits.memory", f"{_mem_mb(ram_gb)}MB")
    if disk_gb is not None:
        await _lxc("config", "device", "set", name, "root", f"size={_disk_mb(disk_gb)}MB")
    if cpu_cores is not None:
        cpu_val, allowance = _cpu_limits(cpu_cores)
        await _lxc("config", "set", name, "limits.cpu", cpu_val)
        if allowance is None:
            await _lxc_ok("config", "unset", name, "limits.cpu.allowance")
        else:
            await _lxc("config", "set", name, "limits.cpu.allowance", allowance)


async def apply_lxc_config(name: str):
    """Nesting-friendly config so Docker/systemd work inside the container."""
    pairs = [
        ("security.nesting", "true"),
        ("security.privileged", "true"),
        ("security.syscalls.intercept.mknod", "true"),
        ("security.syscalls.intercept.setxattr", "true"),
        ("linux.kernel_modules", "overlay,loop,nf_nat,ip_tables,ip6_tables,netlink_diag,br_netfilter"),
    ]
    for k, v in pairs:
        try:
            await _lxc("config", "set", name, k, v)
        except Exception:
            pass
    try:
        await _lxc("config", "device", "add", name, "fuse", "unix-char", "path=/dev/fuse")
    except Exception:
        pass
    raw = "\nlxc.apparmor.profile = unconfined\nlxc.cgroup2.devices.allow = a\nlxc.cap.drop =\nlxc.mount.auto = proc:rw sys:rw cgroup:rw\n"
    try:
        await _lxc("config", "set", name, "raw.lxc", raw)
    except Exception:
        pass


async def apply_bandwidth(name: str, ingress: Optional[str] = None, egress: Optional[str] = None):
    """Set per-container network limits on eth0 (override the profile device if needed).

    ingress = download limit, egress = upload limit. Values are LXD bit strings
    such as '900000bit' or '1kbit'. Creates a container-level eth0 override the
    first time; updates it afterwards."""
    pairs = []
    if ingress:
        pairs.append(("limits.ingress", ingress))
    if egress:
        pairs.append(("limits.egress", egress))
    if not pairs:
        return
    # Does the container already own an eth0 override? If so, `set` works.
    rc, _, _ = await _run("lxc", "config", "device", "set", name, "eth0",
                          f"{pairs[0][0]}={pairs[0][1]}", timeout=30)
    if rc == 0:
        for key, val in pairs[1:]:
            await _lxc_ok("config", "device", "set", name, "eth0", f"{key}={val}", timeout=30)
    else:
        args = [f"{k}={v}" for k, v in pairs]
        await _lxc("config", "device", "override", name, "eth0", *args, timeout=30)


async def read_bandwidth(name: str):
    """Return {'ingress': <download>, 'egress': <upload>} limits for a container, or None."""
    try:
        data = json.loads(await _lxc("query", f"/1.0/instances/{name}", timeout=15))
    except Exception:
        return {"ingress": None, "egress": None}
    eth0 = (data.get("expanded_devices") or {}).get("eth0") or {}
    return {"ingress": eth0.get("limits.ingress"), "egress": eth0.get("limits.egress")}


async def ensure_image(image_alias: str):
    """Make sure an image is usable; LXD auto-downloads remote aliases on init."""
    if await _lxc_ok("image", "info", image_alias, timeout=15):
        return
    # Not local and not a remote alias -> try pulling from the images remote.
    if ":" not in image_alias:
        try:
            await _lxc("image", "copy", f"images:{image_alias}", "local:", timeout=600)
        except Exception:
            pass


async def get_storage_pool_info_gb(pool: str):
    rc, out, _ = await _run("lxc", "storage", "info", pool, timeout=20)
    total_gb = used_gb = 0
    if rc == 0:
        m = re.search(r"total space:\s*([\d.]+)\s*([KMGT]?i?B)", out)
        if m:
            total_gb = _size_to_gib(m.group(1), m.group(2))
        m = re.search(r"space used:\s*([\d.]+)\s*([KMGT]?i?B)", out)
        if m:
            used_gb = _size_to_gib(m.group(1), m.group(2))
    if not total_gb:
        # Pool missing/unavailable (e.g. ZFS dataset gone) -> fall back to host root disk
        # so the controller still reports a sane total instead of 0.
        try:
            du = shutil.disk_usage("/")
            total_gb = round(du.total / (1024 ** 3), 2)
            used_gb = round(du.used / (1024 ** 3), 2)
        except Exception:
            pass
    return total_gb, used_gb


async def list_raw() -> List[Dict[str, Any]]:
    try:
        out = await _lxc("list", "--format", "json", timeout=30)
        return json.loads(out) if out else []
    except Exception:
        return []


def _root_size_gb(inst: Dict[str, Any]) -> float:
    dev = (inst.get("devices") or {}).get("root") or {}
    size = dev.get("size")
    if size:
        return _to_num(size)
    return 0.0


# ─────────────────────────────────────────────────────────────────────────────
#  PUBLIC IP
# ─────────────────────────────────────────────────────────────────────────────
_public_ip_cache = {"ip": None, "ts": 0}
_location_cache = {"data": None, "ts": 0}


async def detect_public_ip() -> Optional[str]:
    if _public_ip_cache["ip"] and time.time() - _public_ip_cache["ts"] < 300:
        return _public_ip_cache["ip"]
    stored = _read(os.path.join(NODE_DIR, "public-ip"))
    if stored:
        _public_ip_cache.update(ip=stored, ts=time.time())
        return stored
    for url in ("https://api.ipify.org", "https://ifconfig.me/ip", "https://icanhazip.com"):
        rc, out, _ = await _run("curl", "-sS", "--connect-timeout", "4", "--max-time", "6", url, timeout=10)
        if rc == 0 and out:
            _public_ip_cache.update(ip=out.strip(), ts=time.time())
            return out.strip()
    return None


async def detect_location() -> dict:
    """Country / state (region) / city of this node, via IP geolocation (cached 1h).

    A manual override can be set in the node's ``location`` file.
    """
    if _location_cache["data"] and time.time() - _location_cache["ts"] < 3600:
        return _location_cache["data"]
    stored = _read(os.path.join(NODE_DIR, "location"))
    if stored:
        loc = {"country": stored, "region": "", "city": "", "display": stored}
        _location_cache.update(data=loc, ts=time.time())
        return loc
    loc = {"country": "", "region": "", "city": "", "display": ""}
    for url, kind in (
        ("http://ip-api.com/json/?fields=status,country,regionName,city", "ipapi"),
        ("https://ipinfo.io/json", "ipinfo"),
    ):
        rc, out, _ = await _run("curl", "-sS", "--connect-timeout", "4", "--max-time", "6", url, timeout=10)
        if rc != 0 or not out:
            continue
        try:
            j = json.loads(out)
        except (ValueError, TypeError):
            continue
        if kind == "ipapi" and j.get("status") != "success":
            continue
        country = (j.get("country") or "").strip()
        region = ((j.get("regionName") if kind == "ipapi" else j.get("region")) or "").strip()
        city = (j.get("city") or "").strip()
        parts = [p for p in (country, region) if p]
        if not parts:
            continue
        loc = {"country": country, "region": region, "city": city, "display": ", ".join(parts)}
        _location_cache.update(data=loc, ts=time.time())
        return loc
    _location_cache.update(data=loc, ts=time.time())
    return loc


async def used_host_ports() -> set:
    """Host ports currently bound by LXD proxy devices on this node."""
    ports = set()
    for inst in await list_raw():
        for dname, dev in (inst.get("devices") or {}).items():
            if dev.get("type") == "proxy" and dev.get("listen"):
                listen = dev["listen"]
                if ":" in listen:
                    try:
                        ports.add(int(listen.rsplit(":", 1)[1]))
                    except ValueError:
                        pass
    return ports


# ─────────────────────────────────────────────────────────────────────────────
#  REQUEST MODELS
# ─────────────────────────────────────────────────────────────────────────────
class CreateReq(BaseModel):
    name: str
    image: str = "ubuntu:22.04"
    ram: float = 1
    cpu: float = 1
    disk: float = 10
    storage_pool: Optional[str] = None
    start: bool = True
    ingress: Optional[str] = None   # download limit (LXD bit string, e.g. 900000bit)
    egress: Optional[str] = None    # upload limit   (LXD bit string, e.g. 100000bit)


class NameReq(BaseModel):
    name: str


class ResizeReq(BaseModel):
    name: str
    ram: Optional[float] = None
    cpu: Optional[float] = None
    disk: Optional[float] = None


class ReinstallReq(BaseModel):
    name: str
    image: str


class ExecReq(BaseModel):
    name: str
    command: str
    timeout: int = 60


class PortCreateReq(BaseModel):
    container: str
    vps_port: int


class PortRemoveReq(BaseModel):
    container: str
    host_port: int


class MoveReq(BaseModel):
    name: str
    pool: str


class BandwidthReq(BaseModel):
    name: str
    ingress: Optional[str] = None   # download (LXD bit string)
    egress: Optional[str] = None    # upload   (LXD bit string)


class ConsoleReq(BaseModel):
    name: str
    kind: str = "sshx"   # sshx | tmate


class Ipv4TunnelReq(BaseModel):
    name: str
    action: str = "start"   # start | stop


class FileManagerReq(BaseModel):
    name: str
    action: str = "start"   # start | stop
    username: str = "admin"
    password: str = "admin"


# ─────────────────────────────────────────────────────────────────────────────
#  ENDPOINTS — info
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health(_: bool = Depends(require_key)):
    return {"ok": True, "node_id": NODE_ID, "node_name": NODE_NAME, "version": VERSION, "time": datetime.now().isoformat()}


@app.get("/info-vps")
async def info_vps(_: bool = Depends(require_key)):
    # CPU
    total_cpu = os.cpu_count() or 1

    # RAM
    total_ram_gb = 0.0
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    total_ram_gb = round(int(line.split()[1]) / 1048576.0, 2)
                    break
    except Exception:
        pass

    # Load / uptime
    try:
        with open("/proc/uptime") as f:
            uptime_seconds = int(float(f.read().split()[0]))
    except Exception:
        uptime_seconds = 0
    load1 = load5 = load15 = 0.0
    try:
        with open("/proc/loadavg") as f:
            p = f.read().split()
            load1, load5, load15 = float(p[0]), float(p[1]), float(p[2])
    except Exception:
        pass

    # Disk (host root)
    try:
        du = shutil.disk_usage("/")
        host_total = du.total / (1024 ** 3)
        host_used = du.used / (1024 ** 3)
        host_free = du.free / (1024 ** 3)
    except Exception:
        host_total = host_used = host_free = 0.0

    pool_total, pool_used = await get_storage_pool_info_gb(STORAGE_POOL)

    # Container counts
    insts = await list_raw()
    running = sum(1 for i in insts if (i.get("status") or "").lower() == "running")

    # LXD version
    lxd_version = "unknown"
    rc, out, _ = await _run("lxc", "version", timeout=15)
    if rc == 0:
        for line in out.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                if k.strip().lower().startswith("server"):
                    lxd_version = v.strip()
                    break

    # OS
    os_pretty = "unknown"
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("PRETTY_NAME="):
                    os_pretty = line.split("=", 1)[1].strip().strip('"')
                    break
    except Exception:
        pass

    return {
        "ok": True,
        "node_id": NODE_ID,
        "node_name": NODE_NAME,
        "hostname": socket.gethostname(),
        "os": os_pretty,
        "kernel": platform.release(),
        "arch": platform.machine(),
        "lxd_version": lxd_version,
        "uptime_seconds": uptime_seconds,
        "uptime": _fmt_uptime(uptime_seconds),
        "public_ip": await detect_public_ip(),
        "location": await detect_location(),
        "cpu": {"total": total_cpu, "load1": load1, "load5": load5, "load15": load15},
        "ram": {"total_gb": total_ram_gb},
        "disk": {"host_total_gb": round(host_total, 2), "host_used_gb": round(host_used, 2),
                 "host_free_gb": round(host_free, 2)},
        "storage_pool": {"name": STORAGE_POOL, "total_gb": pool_total, "used_gb": pool_used,
                         "enforced": STORAGE_POOL != FALLBACK_POOL},
        "containers": {"total": len(insts), "running": running, "stopped": len(insts) - running},
        "port_range": {"start": PORT_RANGE_START, "end": PORT_RANGE_END},
    }


@app.get("/check-resources-data")
async def check_resources_data(_: bool = Depends(require_key)):
    total_cpu = os.cpu_count() or 1
    total_ram_gb = 0.0
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    total_ram_gb = int(line.split()[1]) / 1048576.0
                    break
    except Exception:
        pass

    insts = await list_raw()
    alloc_cpu = 0.0
    alloc_ram = 0.0
    alloc_disk = 0.0
    for inst in insts:
        cfg = inst.get("config") or {}
        alloc_cpu += _to_num(cfg.get("limits.cpu"))
        alloc_ram += _to_num(cfg.get("limits.memory"))
        alloc_disk += _root_size_gb(inst)

    pool_total, pool_used = await get_storage_pool_info_gb(STORAGE_POOL)
    pool_avail_from_alloc = max(0.0, pool_total - alloc_disk)

    return {
        "ok": True,
        "cpu": {"total": total_cpu, "allocated": round(alloc_cpu, 2),
                "available": max(0.0, round(total_cpu - alloc_cpu, 2))},
        "ram": {"total_gb": round(total_ram_gb, 2), "allocated_gb": round(alloc_ram, 2),
                "available_gb": max(0.0, round(total_ram_gb - alloc_ram, 2))},
        "disk": {"total_gb": pool_total, "used_gb": pool_used, "allocated_gb": round(alloc_disk, 2),
                 "pool_total_gb": pool_total, "pool_available_gb": pool_avail_from_alloc,
                 "available_gb": pool_avail_from_alloc},
    }


@app.get("/list-containers")
async def list_containers(_: bool = Depends(require_key)):
    out = []
    for inst in await list_raw():
        cfg = inst.get("config") or {}
        name = inst.get("name")
        out.append({
            "name": name,
            "status": (inst.get("status") or "unknown").lower(),
            "ram": _fmt_num(_to_num(cfg.get("limits.memory"))),
            "cpu": _fmt_num(_to_num(cfg.get("limits.cpu"))),
            "disk": _fmt_num(_root_size_gb(inst)),
            "os": (inst.get("config") or {}).get("image.os", ""),
            "ip": await container_ip(name) if (inst.get("status") or "").lower() == "running" else None,
        })
    return {"ok": True, "count": len(out), "containers": out}


@app.get("/disks")
async def disks(_: bool = Depends(require_key)):
    """Return raw root-disk usage/limit (bytes) for every running container.

    One `lxc list` call covers all containers so the bot can poll cheaply.
    """
    out: List[Dict[str, Any]] = []
    for inst in await list_raw():
        name = inst.get("name")
        status = (inst.get("status") or "").lower()
        if not name or status != "running":
            continue
        usage = total = 0
        root = ((inst.get("state") or {}).get("disk") or {}).get("root") or {}
        total = int(root.get("total") or 0)
        usage = int(root.get("usage") or 0)
        if not total:
            try:
                data = json.loads(await _lxc("query", f"/1.0/instances/{name}/state", timeout=15))
                root = (data.get("disk") or {}).get("root") or {}
                total = int(root.get("total") or 0)
                usage = int(root.get("usage") or 0)
            except Exception:
                pass
        if total:
            out.append({"name": name, "usage": usage, "total": total})
    return {"ok": True, "disks": out}


@app.get("/images")
async def images(_: bool = Depends(require_key)):
    candidates = [
        ("Ubuntu 20.04 LTS", "ubuntu:20.04"),
        ("Ubuntu 22.04 LTS", "ubuntu:22.04"),
        ("Ubuntu 24.04 LTS", "ubuntu:24.04"),
        ("Debian 11", "images:debian/11"),
        ("Debian 12", "images:debian/12"),
        ("Debian 13", "images:debian/13"),
        ("Rocky Linux 8", "images:rockylinux/8"),
        ("Rocky Linux 9", "images:rockylinux/9"),
        ("AlmaLinux 9", "images:almalinux/9"),
        ("Fedora 44", "images:fedora/44"),
    ]
    result = []
    for label, value in candidates:
        available = await _lxc_ok("image", "info", value, timeout=10)
        result.append({"label": label, "value": value, "available": available})
    return {"ok": True, "images": result}


# ─────────────────────────────────────────────────────────────────────────────
#  ENDPOINTS — container lifecycle
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/create-container")
async def create_container(body: CreateReq, _: bool = Depends(require_key)):
    name = body.name.strip()
    if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9-]{0,62}$", name):
        raise HTTPException(status_code=400, detail="Invalid container name")
    if await container_exists(name):
        raise HTTPException(status_code=409, detail=f"Container '{name}' already exists")

    pool = body.storage_pool or STORAGE_POOL
    if not await _lxc_ok("storage", "show", pool, timeout=15):
        pool = FALLBACK_POOL

    await ensure_image(body.image)
    try:
        await _lxc("init", body.image, name, "-s", pool, timeout=900)
    except Exception as e:
        # retry once with explicit local alias resolution
        try:
            await _lxc("init", body.image, name, "-s", pool, timeout=900)
        except Exception:
            raise HTTPException(status_code=500, detail=f"init failed: {e}")

    await apply_resource_limits(name, ram_gb=body.ram, cpu_cores=body.cpu, disk_gb=body.disk)
    await apply_lxc_config(name)
    if body.ingress or body.egress:
        await apply_bandwidth(name, ingress=body.ingress, egress=body.egress)

    if body.start:
        await _lxc("start", name, timeout=180)

    return {"ok": True, "name": name, "pool": pool, "status": await container_status(name)}


@app.post("/set-bandwidth")
async def set_bandwidth(body: BandwidthReq, _: bool = Depends(require_key)):
    if not await container_exists(body.name):
        raise HTTPException(status_code=404, detail="Container not found")
    await apply_bandwidth(body.name, ingress=body.ingress, egress=body.egress)
    return {"ok": True, "name": body.name, "bandwidth": await read_bandwidth(body.name)}


@app.post("/start-container")
async def start_container(body: NameReq, _: bool = Depends(require_key)):
    if not await container_exists(body.name):
        raise HTTPException(status_code=404, detail="Container not found")
    status = await container_status(body.name)
    if status != "running":
        await _lxc("start", body.name, timeout=180)
    return {"ok": True, "name": body.name, "status": await container_status(body.name)}


@app.post("/stop-container")
async def stop_container(body: NameReq, _: bool = Depends(require_key)):
    if not await container_exists(body.name):
        raise HTTPException(status_code=404, detail="Container not found")
    status = await container_status(body.name)
    if status in ("running", "frozen"):
        await _lxc("stop", body.name, "--force", timeout=180)
    return {"ok": True, "name": body.name, "status": await container_status(body.name)}


@app.post("/restart-container")
async def restart_container(body: NameReq, _: bool = Depends(require_key)):
    if not await container_exists(body.name):
        raise HTTPException(status_code=404, detail="Container not found")
    await _lxc("restart", body.name, timeout=240)
    return {"ok": True, "name": body.name, "status": await container_status(body.name)}


@app.post("/delete-container")
async def delete_container(body: NameReq, _: bool = Depends(require_key)):
    if await container_exists(body.name):
        await _lxc("delete", body.name, "--force", timeout=180)
    return {"ok": True, "name": body.name}


@app.post("/reinstall-container")
async def reinstall_container(body: ReinstallReq, _: bool = Depends(require_key)):
    if not await container_exists(body.name):
        raise HTTPException(status_code=404, detail="Container not found")
    # capture current limits
    inst = None
    for i in await list_raw():
        if i.get("name") == body.name:
            inst = i
            break
    cfg = (inst or {}).get("config") or {}
    ram = _to_num(cfg.get("limits.memory"))
    cpu = _to_num(cfg.get("limits.cpu"))
    disk = _root_size_gb(inst) if inst else 0
    pool = ((inst or {}).get("devices", {}).get("root", {}) or {}).get("pool") or STORAGE_POOL

    await _lxc("delete", body.name, "--force", timeout=180)
    await ensure_image(body.image)
    await _lxc("init", body.image, body.name, "-s", pool, timeout=900)
    await apply_resource_limits(body.name, ram_gb=ram or None, cpu_cores=cpu or None, disk_gb=disk or None)
    await apply_lxc_config(body.name)
    await _lxc("start", body.name, timeout=180)
    return {"ok": True, "name": body.name, "status": await container_status(body.name)}


@app.post("/resize-container")
async def resize_container(body: ResizeReq, _: bool = Depends(require_key)):
    if not await container_exists(body.name):
        raise HTTPException(status_code=404, detail="Container not found")
    await apply_resource_limits(body.name, ram_gb=body.ram, cpu_cores=body.cpu, disk_gb=body.disk)
    return {"ok": True, "name": body.name}


@app.get("/container-info")
async def container_info(name: str = Query(...), _: bool = Depends(require_key)):
    inst = None
    for i in await list_raw():
        if i.get("name") == name:
            inst = i
            break
    if not inst:
        raise HTTPException(status_code=404, detail="Container not found")
    cfg = inst.get("config") or {}
    status = (inst.get("status") or "unknown").lower()
    uptime = "Unknown"
    if status == "running":
        rc, out, _ = await _run("lxc", "exec", name, "--", "cat", "/proc/uptime", timeout=15)
        if rc == 0 and out:
            uptime = _fmt_uptime(out.split()[0])
    return {
        "ok": True,
        "name": name,
        "status": status,
        "ip": await container_ip(name) if status == "running" else None,
        "uptime": uptime,
        "ram": _fmt_num(_to_num(cfg.get("limits.memory"))),
        "cpu": _fmt_num(_to_num(cfg.get("limits.cpu"))),
        "disk": _fmt_num(_root_size_gb(inst)),
        "os": cfg.get("image.os", ""),
        "created_at": inst.get("created_at", ""),
        "bandwidth": await read_bandwidth(name),
    }


async def container_cpu(name: str, interval: float = 0.5) -> str:
    try:
        rc, out1, _ = await _run("lxc", "info", name, timeout=20)
        if rc != 0:
            return "N/A"
        cpu1 = None
        for line in out1.splitlines():
            if "CPU usage (in seconds)" in line:
                cpu1 = float(line.split(":", 1)[1].strip())
                break
        await asyncio.sleep(interval)
        rc, out2, _ = await _run("lxc", "info", name, timeout=20)
        if rc != 0:
            return "N/A"
        cpu2 = None
        for line in out2.splitlines():
            if "CPU usage (in seconds)" in line:
                cpu2 = float(line.split(":", 1)[1].strip())
                break
        if cpu1 is not None and cpu2 is not None:
            delta = cpu2 - cpu1
            if delta < 0:
                delta = 0
            pct = (delta / interval) * 100.0
            if pct > 100.0:
                pct = 100.0
            return f"{pct:.1f}%"
    except Exception:
        return "N/A"

@app.get("/container-stats")
async def container_stats(name: str = Query(...), _: bool = Depends(require_key)):
    if not await container_exists(name):
        raise HTTPException(status_code=404, detail="Container not found")
    status = await container_status(name)

    cpu = "N/A"
    mem = "N/A"
    disk = "N/A"
    uptime = "Unknown"
    processes = 0

    if status == "running":
        cpu = await container_cpu(name)

        rc, out, _ = await _run("lxc", "exec", name, "--", "free", "-m", timeout=15)
        if rc == 0 and out:
            lines = out.splitlines()
            if len(lines) > 1:
                parts = lines[1].split()
                total = int(parts[1]); used = int(parts[2])
                pct = (used / total * 100) if total else 0
                mem = f"{used}/{total} MB ({pct:.1f}%)"

        rc, out, _ = await _run("lxc", "exec", name, "--", "cat", "/proc/uptime", timeout=15)
        if rc == 0 and out:
            uptime = _fmt_uptime(out.split()[0])

        # State API for processes + disk
        try:
            data = json.loads(await _lxc("query", f"/1.0/instances/{name}/state", timeout=20))
            processes = int(data.get("processes") or 0)
            root = (data.get("disk") or {}).get("root") or {}
            total = int(root.get("total") or 0); usage = int(root.get("usage") or 0)
            if total:
                disk = f"{_fmt_bytes(usage)}/{_fmt_bytes(total)} ({usage / total * 100:.1f}%)"
        except Exception:
            pass

    return {"ok": True, "name": name, "status": status, "cpu": cpu, "memory": mem,
            "disk": disk, "uptime": uptime, "processes": processes}


@app.post("/container-exec")
async def container_exec(body: ExecReq, _: bool = Depends(require_key)):
    if not await container_exists(body.name):
        raise HTTPException(status_code=404, detail="Container not found")
    rc, out, err = await _run("lxc", "exec", body.name, "--", "sh", "-c", body.command,
                              timeout=max(5, min(body.timeout, 600)))
    return {"ok": True, "returncode": rc, "stdout": out, "stderr": err}


@app.get("/container-logs")
async def container_logs(name: str = Query(...), lines: int = 50, _: bool = Depends(require_key)):
    if not await container_exists(name):
        raise HTTPException(status_code=404, detail="Container not found")
    rc, out, err = await _run("lxc", "exec", name, "--", "journalctl", "-n", str(lines), "--no-pager", timeout=30)
    return {"ok": True, "logs": out if rc == 0 else (err or "No logs available")}


# ─────────────────────────────────────────────────────────────────────────────
#  ENDPOINTS — snapshots / clone / suspend / maintenance
# ─────────────────────────────────────────────────────────────────────────────
class SnapshotReq(BaseModel):
    name: str
    snap: Optional[str] = None


class SnapshotNameReq(BaseModel):
    name: str
    snap: str


class CloneReq(BaseModel):
    name: str
    new_name: str


@app.post("/freeze-container")
async def freeze_container(body: NameReq, _: bool = Depends(require_key)):
    if not await container_exists(body.name):
        raise HTTPException(status_code=404, detail="Container not found")
    await _lxc("pause", body.name, timeout=60)
    return {"ok": True, "name": body.name, "status": await container_status(body.name)}


@app.post("/unfreeze-container")
async def unfreeze_container(body: NameReq, _: bool = Depends(require_key)):
    if not await container_exists(body.name):
        raise HTTPException(status_code=404, detail="Container not found")
    await _lxc("start", body.name, timeout=180)
    return {"ok": True, "name": body.name, "status": await container_status(body.name)}


@app.post("/fix-network")
async def fix_network(_: bool = Depends(require_key)):
    """Re-assert bridge, DHCP, DNS and NAT on the node host."""
    await _host(
        "lxc network set lxdbr0 ipv4.dhcp=true ipv4.nat=true 2>/dev/null || true; "
        "lxc network set lxdbr0 dns.mode=managed 2>/dev/null || true; "
        "systemctl restart snap.lxd.daemon 2>/dev/null || true"
    )
    rc, out, _ = await _run("lxc", "network", "get", "lxdbr0", "ipv4.address", timeout=10)
    subnet = "10.111.49.0/24"
    if rc == 0 and "/" in out:
        octets = out.split("/")[0].split(".")
        subnet = f"{octets[0]}.{octets[1]}.{octets[2]}.0/{out.split('/')[1]}"
    await _host(
        "IPT=iptables; command -v iptables-nft >/dev/null 2>&1 && IPT=iptables-nft; "
        f"$IPT -t nat -C POSTROUTING -s {subnet} ! -d {subnet} -j MASQUERADE 2>/dev/null || "
        f"$IPT -t nat -A POSTROUTING -s {subnet} ! -d {subnet} -j MASQUERADE; "
        "$IPT -C FORWARD -i lxdbr0 -j ACCEPT 2>/dev/null || $IPT -A FORWARD -i lxdbr0 -j ACCEPT; "
        "$IPT -C FORWARD -o lxdbr0 -j ACCEPT 2>/dev/null || $IPT -A FORWARD -o lxdbr0 -j ACCEPT"
    )
    return {"ok": True, "subnet": subnet}


@app.post("/console")
async def console(body: ConsoleReq, _: bool = Depends(require_key)):
    """Start a shareable console (sshx or tmate) inside a container and return its URL."""
    if not await container_exists(body.name):
        raise HTTPException(status_code=404, detail="Container not found")
    kind = (body.kind or "sshx").lower()
    nm = body.name

    if kind == "tmate":
        setup = (
            "command -v tmate >/dev/null 2>&1 || { apt-get update -y >/dev/null 2>&1; "
            "apt-get install -y wget tar openssh-client >/dev/null 2>&1; "
            "wget -q --timeout=60 https://github.com/tmate-io/tmate/releases/download/2.4.0/"
            "tmate-2.4.0-static-linux-amd64.tar.gz -O /tmp/tmate.tar.gz >/dev/null 2>&1; "
            "tar xzf /tmp/tmate.tar.gz -C /tmp >/dev/null 2>&1; "
            "cp /tmp/tmate-2.4.0-static-linux-amd64/tmate /usr/local/bin/tmate; "
            "chmod +x /usr/local/bin/tmate; }; "
            "pkill -9 tmate 2>/dev/null; rm -f /tmp/sgm_tmate.sock /tmp/sgm_tmate.out; "
            "nohup tmate -S /tmp/sgm_tmate.sock new-session -d >/dev/null 2>&1; "
            "sleep 4; tmate -S /tmp/sgm_tmate.sock display -p '#{tmate_ssh}' 2>/dev/null"
        )
    else:
        setup = (
            "command -v sshx >/dev/null 2>&1 || { "
            "curl -sL --connect-timeout 20 --max-time 120 https://sshx.io/get | sh -s -- install >/dev/null 2>&1; }; "
            "pkill -9 sshx 2>/dev/null; rm -f /tmp/sgm_sshx.out; "
            "nohup /usr/local/bin/sshx >/tmp/sgm_sshx.out 2>&1 & "
            "sleep 8; grep -Eo 'https://sshx.io/s/[A-Za-z0-9#]+' /tmp/sgm_sshx.out | head -n1"
        )

    rc, out, err = await _run("lxc", "exec", nm, "--", "bash", "-c", setup, timeout=420)
    clean = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", out or "")
    url = ""
    m = re.search(r"https?://\S+", clean)
    if m:
        url = m.group(0).strip()
    elif clean.strip():
        url = clean.strip().splitlines()[-1].strip()
    return {"ok": True, "name": nm, "kind": kind, "url": url, "raw": clean, "stderr": err}


async def _await_pinggy(out_file: str, timeout: int = 45):
    """Poll a pinggy output file for the assigned tcp://host:port."""
    for _ in range(timeout):
        rc, txt, _ = await _host(f"grep -Eo 'tcp://[^ :]+:[0-9]+' {out_file} 2>/dev/null | tail -n1", timeout=10)
        m = re.search(r"tcp://([^:\s]+):(\d+)", txt or "")
        if m:
            return m.group(1), m.group(2)
        await asyncio.sleep(1)
    return None, None


async def _stop_pinggy_tunnel(tag: str, out: str):
    """Stop a detached pinggy tunnel via its PID file (process-group kill)."""
    pidfile = f"/tmp/{tag}.pid"
    script_path = f"/tmp/{tag}.sh"
    await _host(
        f"if [ -f {shlex.quote(pidfile)} ]; then kill -TERM -\"$(cat {shlex.quote(pidfile)})\" 2>/dev/null; fi; "
        f"rm -f {shlex.quote(pidfile)} {shlex.quote(out)} {shlex.quote(script_path)}",
        timeout=20)


async def _launch_pinggy_tunnel(tag: str, out: str, tunnel_cmd: str, timeout: int = 45):
    """Start a detached auto-restarting pinggy tunnel and return (host, port)."""
    script_path = f"/tmp/{tag}.sh"
    pidfile = f"/tmp/{tag}.pid"
    script = (
        f"if [ -f {shlex.quote(pidfile)} ]; then kill -TERM -\"$(cat {shlex.quote(pidfile)})\" 2>/dev/null; fi\n"
        f"cat > {shlex.quote(script_path)} <<'SGM_PINGGY_EOF'\n"
        f"#!/bin/bash\n"
        f"while true; do\n"
        f"  {tunnel_cmd} >> {out} 2>&1\n"
        f"  sleep 3\n"
        f"done\n"
        f"SGM_PINGGY_EOF\n"
        f"chmod +x {shlex.quote(script_path)}\n"
        f"rm -f {out}\n"
        f"setsid {shlex.quote(script_path)} >/dev/null 2>&1 < /dev/null &\n"
        f"echo $! > {shlex.quote(pidfile)}\n"
    )
    proc = await asyncio.create_subprocess_exec(
        "bash", "-c", script,
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    try:
        await asyncio.wait_for(proc.wait(), timeout=20)
    except asyncio.TimeoutError:
        proc.kill()
    return await _await_pinggy(out, timeout=timeout)



@app.post("/ipv4-tunnel")
async def ipv4_tunnel(body: Ipv4TunnelReq, _: bool = Depends(require_key)):
    """Start/stop a persistent pinggy IPv4 SSH tunnel from this node into a container's SSH port."""
    if not await container_exists(body.name):
        raise HTTPException(status_code=404, detail="Container not found")
    nm = body.name
    tag = f"sgm_pinggy_{nm}"
    out = f"/tmp/{tag}.out"
    if (body.action or "start").lower() == "stop":
        await _stop_pinggy_tunnel(tag, out)
        return {"ok": True, "name": nm, "running": False, "host": None, "port": None}

    # Ensure openssh-server is present and running in the container
    await _run("lxc", "exec", nm, "--", "bash", "-c",
               "command -v sshd >/dev/null 2>&1 || { apt-get update -y >/dev/null 2>&1; "
               "DEBIAN_FRONTEND=noninteractive apt-get install -y openssh-server >/dev/null 2>&1; }; "
               "sed -i 's/^#\\?PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config; "
               "mkdir -p /run/sshd; systemctl enable --now ssh >/dev/null 2>&1 || service ssh start >/dev/null 2>&1; "
               "service ssh status >/dev/null 2>&1 || /usr/sbin/sshd 2>/dev/null || true", timeout=240)

    ip = await container_ip(nm)
    if not ip:
        raise HTTPException(status_code=502, detail="Could not determine container IP (is it running?)")

    tunnel = (
        f"ssh -p 443 -R 0:{ip}:22 tcp@free.pinggy.io "
        f"-o ServerAliveInterval=30 -o ServerAliveCountMax=3 -o StrictHostKeyChecking=no "
        f"-o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
    )
    host, port = await _launch_pinggy_tunnel(tag, out, tunnel)
    return {"ok": True, "name": nm, "running": True, "host": host, "port": port}


@app.post("/file-manager")
async def file_manager(body: FileManagerReq, _: bool = Depends(require_key)):
    """Install/configure/start filebrowser in a container and expose it via a pinggy tunnel."""
    if not await container_exists(body.name):
        raise HTTPException(status_code=404, detail="Container not found")
    nm = body.name
    tag = f"sgm_fm_{nm}"
    out = f"/tmp/{tag}.out"
    if (body.action or "start").lower() == "stop":
        await _run("lxc", "exec", nm, "--", "pkill", "-x", "filebrowser", timeout=20)
        await _stop_pinggy_tunnel(tag, out)
        return {"ok": True, "name": nm, "running": False, "host": None, "port": None,
                "username": body.username}

    # Install filebrowser if missing
    await _run("lxc", "exec", nm, "--", "bash", "-c",
               "command -v filebrowser >/dev/null 2>&1 || "
               "( command -v curl >/dev/null 2>&1 || { apt-get update -y >/dev/null 2>&1; "
               "DEBIAN_FRONTEND=noninteractive apt-get install -y curl >/dev/null 2>&1; }; "
               "curl -fsSL https://raw.githubusercontent.com/filebrowser/get/master/get.sh | bash )",
               timeout=300)
    # Configure admin user
    uname = shlex.quote(body.username or "admin")
    pwd = shlex.quote(body.password or "admin")
    await _run("lxc", "exec", nm, "--", "bash", "-c",
               f"filebrowser config init >/dev/null 2>&1; "
               f"filebrowser users add {uname} {pwd} --perm.admin >/dev/null 2>&1 || "
               f"filebrowser users update {uname} --password {pwd} --perm.admin >/dev/null 2>&1",
               timeout=60)
    # (Re)start the filebrowser service (detached so it survives the exec session)
    await _run("lxc", "exec", nm, "--", "bash", "-c",
               "pkill -x filebrowser 2>/dev/null; sleep 1; "
               "setsid nohup filebrowser --address=0.0.0.0 --port=8080 --root=/ "
               ">/dev/null 2>&1 < /dev/null & sleep 2", timeout=30)

    ip = await container_ip(nm)
    if not ip:
        raise HTTPException(status_code=502, detail="Could not determine container IP (is it running?)")

    tunnel = (
        f"ssh -p 443 -R 0:{ip}:8080 tcp@free.pinggy.io "
        f"-o ServerAliveInterval=30 -o ServerAliveCountMax=3 -o StrictHostKeyChecking=no "
        f"-o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
    )
    host, port = await _launch_pinggy_tunnel(tag, out, tunnel)
    return {"ok": True, "name": nm, "running": True, "host": host, "port": port,
            "username": body.username}


@app.post("/stop-all")
async def stop_all(_: bool = Depends(require_key)):
    stopped = []
    failed = []
    for inst in await list_raw():
        if (inst.get("status") or "").lower() == "running":
            nm = inst.get("name")
            if await _lxc_ok("stop", nm, timeout=120):
                stopped.append(nm)
            else:
                failed.append(nm)
    return {"ok": True, "stopped": stopped, "failed": failed}


@app.post("/start-all")
async def start_all(_: bool = Depends(require_key)):
    started = []
    failed = []
    for inst in await list_raw():
        st = (inst.get("status") or "").lower()
        if st in ("stopped", "frozen"):
            nm = inst.get("name")
            if await _lxc_ok("start", nm, timeout=180):
                started.append(nm)
            else:
                failed.append(nm)
    return {"ok": True, "started": started, "failed": failed}


# ─────────────────────────────────────────────────────────────────────────────
#  ENDPOINTS — port forwarding
# ─────────────────────────────────────────────────────────────────────────────
async def _pick_port() -> Optional[int]:
    used = await used_host_ports()
    # also avoid ports already bound on the host
    import random
    for _ in range(200):
        p = random.randint(PORT_RANGE_START, PORT_RANGE_END)
        if p in used:
            continue
        # quick socket probe
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("0.0.0.0", p))
            s.close()
            return p
        except OSError:
            s.close()
            continue
    return None


@app.post("/port-forward/create")
async def port_forward_create(body: PortCreateReq, _: bool = Depends(require_key)):
    if not await container_exists(body.container):
        raise HTTPException(status_code=404, detail="Container not found")
    if not (1 <= body.vps_port <= 65535):
        raise HTTPException(status_code=400, detail="Invalid vps_port")
    host_port = await _pick_port()
    if not host_port:
        raise HTTPException(status_code=503, detail="No free host port available")
    await _lxc("config", "device", "add", body.container, f"tcp_proxy_{host_port}", "proxy",
               f"listen=tcp:0.0.0.0:{host_port}", f"connect=tcp:127.0.0.1:{body.vps_port}")
    await _lxc("config", "device", "add", body.container, f"udp_proxy_{host_port}", "proxy",
               f"listen=udp:0.0.0.0:{host_port}", f"connect=udp:127.0.0.1:{body.vps_port}")
    return {"ok": True, "host_port": host_port, "vps_port": body.vps_port,
            "public_ip": await detect_public_ip()}


@app.post("/port-forward/remove")
async def port_forward_remove(body: PortRemoveReq, _: bool = Depends(require_key)):
    await _lxc_ok("config", "device", "remove", body.container, f"tcp_proxy_{body.host_port}")
    await _lxc_ok("config", "device", "remove", body.container, f"udp_proxy_{body.host_port}")
    return {"ok": True}


@app.get("/port-forward/list")
async def port_forward_list(container: Optional[str] = None, _: bool = Depends(require_key)):
    out = []
    for inst in await list_raw():
        if container and inst.get("name") != container:
            continue
        for dname, dev in (inst.get("devices") or {}).items():
            if dev.get("type") == "proxy" and dname.startswith("tcp_proxy_"):
                try:
                    hp = int(dname.replace("tcp_proxy_", ""))
                except ValueError:
                    continue
                local_port = None
                connect = dev.get("connect") or ""
                if ":" in connect:
                    try:
                        local_port = int(connect.rsplit(":", 1)[1])
                    except ValueError:
                        local_port = None
                out.append({"container": inst.get("name"), "host_port": hp, "local_port": local_port})
    return {"ok": True, "forwards": out, "public_ip": await detect_public_ip()}


@app.get("/public-port-range")
async def public_port_range(_: bool = Depends(require_key)):
    return {"ok": True, "start": PORT_RANGE_START, "end": PORT_RANGE_END,
            "public_ip": await detect_public_ip()}


# ─────────────────────────────────────────────────────────────────────────────
#  ENDPOINTS — host maintenance
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/host/setup")
async def host_setup(_: bool = Depends(require_key)):
    """Idempotently (re)assert bridge + NAT. Safe to call anytime."""
    await _host("lxc network create lxdbr0 ipv4.address=10.111.49.1/24 ipv4.nat=true 2>/dev/null || true")
    subnet = "10.111.49.0/24"
    rc, out, _ = await _run("lxc", "network", "get", "lxdbr0", "ipv4.address", timeout=10)
    if rc == 0 and "/" in out:
        octets = out.split("/")[0].split(".")
        subnet = f"{octets[0]}.{octets[1]}.{octets[2]}.0/{out.split('/')[1]}"
    await _host(
        "IPT=iptables; command -v iptables-nft >/dev/null 2>&1 && IPT=iptables-nft; "
        f"$IPT -t nat -C POSTROUTING -s {subnet} ! -d {subnet} -j MASQUERADE 2>/dev/null || "
        f"$IPT -t nat -A POSTROUTING -s {subnet} ! -d {subnet} -j MASQUERADE; "
        "$IPT -C FORWARD -i lxdbr0 -j ACCEPT 2>/dev/null || $IPT -A FORWARD -i lxdbr0 -j ACCEPT; "
        "$IPT -C FORWARD -o lxdbr0 -j ACCEPT 2>/dev/null || $IPT -A FORWARD -o lxdbr0 -j ACCEPT"
    )
    return {"ok": True, "subnet": subnet}


@app.post("/reboot-node")
async def reboot_node(_: bool = Depends(require_key)):
    """Reboot the node VPS."""
    try:
        async def _reboot():
            await asyncio.sleep(2)
            try:
                os.system("reboot >/dev/null 2>&1 &")
            except Exception:
                pass
        asyncio.create_task(_reboot())
    except Exception:
        pass
    return {"ok": True, "message": "Reboot request received. Node will reboot shortly."}

@app.post("/host/exec")
async def host_exec(body: ExecReq, _: bool = Depends(require_key)):
    """Run a host shell command (power user). Use with care."""
    rc, out, err = await _run("bash", "-c", body.command, timeout=max(5, min(body.timeout, 600)))
    return {"ok": True, "returncode": rc, "stdout": out, "stderr": err}


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"ok": False, "detail": str(exc)})


if __name__ == "__main__":
    print(f"[SGM-NODE] starting API on {BIND_HOST}:{PORT}  node={NODE_ID} ({NODE_NAME})", flush=True)
    uvicorn.run(app, host=BIND_HOST, port=PORT, log_level="info", access_log=False)
