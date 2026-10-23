#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════╗
# ║   SGM NODE INSTALLER  —  LXD VPS host + SGM Node API (port 6342)          ║
# ║   Installs LXD, downloads node-api-code.py from GitHub, creates the       ║
# ║   systemd service, and prints the generated API key.                      ║
# ╚══════════════════════════════════════════════════════════════════════════╝
#
#   Usage:   sudo bash node-install.sh
#            sudo bash node-install.sh install   (install directly, skip menu)
#   Env:     SGM_NODE_PORT      (default 6342)
#            SGM_NODE_NAME      (default hostname)
#            SGM_NODE_API_URL   (override the GitHub raw URL)
#            FORCE_CLEAN=1      (skip safety prompt, wipe + reinstall)
#
#   API code lives in node-api-code.py on GitHub. Option [2] updates only
#   that file and keeps the node identity, API key, config and containers.
export DEBIAN_FRONTEND=noninteractive
export PATH=$PATH:/snap/bin:/usr/local/sbin:/usr/sbin:/sbin

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  COLORS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RED='\033[0;31m'; LRED='\033[1;31m'; GREEN='\033[0;32m'; LGREEN='\033[1;32m'
YELLOW='\033[1;33m'; CYAN='\033[0;36m'; LCYAN='\033[1;36m'; BLUE='\033[0;34m'
LBLUE='\033[1;34m'; MAGENTA='\033[0;35m'; WHITE='\033[1;37m'; GRAY='\033[0;37m'
BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'
UI_BORDER='\033[38;5;39m'; UI_ACCENT='\033[38;5;45m'; UI_ACCENT2='\033[38;5;213m'
UI_MUTED='\033[38;5;244m'; UI_TEXT='\033[1;97m'

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GLOBAL STATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NODE_DIR="/opt/SGM-NODE"
NODE_PORT="${SGM_NODE_PORT:-6342}"
NODE_BIND="${SGM_BIND_HOST:-0.0.0.0}"
GITHUB_OWNER="${SGM_GITHUB_OWNER:-ShahedPlayz}"
GITHUB_REPO="${SGM_GITHUB_REPO:-LXD-VPS-BOT}"
GITHUB_BRANCH="${SGM_GITHUB_BRANCH:-main}"
NODE_API_FILE="${SGM_NODE_API_FILE:-node-api-code.py}"
NODE_API_URL="${SGM_NODE_API_URL:-https://raw.githubusercontent.com/${GITHUB_OWNER}/${GITHUB_REPO}/${GITHUB_BRANCH}/${NODE_API_FILE}}"
QUOTA_POOL_RESERVE_GB=6
INSTALL_LOG="/var/log/sgm-node-install.log"
API_PYTHON="/usr/bin/python3"
ENV_TYPE="unknown"
SNAP_AVAILABLE=false
LXD_METHOD="snap"
CURRENT_STEP=0
TOTAL_STEPS=9
ACTIVE_POOL="default"
PUBLIC_IP=""
MAIN_IFACE=""
HOST_PRIVATE_IP=""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LOGGING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
mkdir -p "$(dirname "$INSTALL_LOG")"
# Remember whether a previous run had already created the log (this run creates it below).
if [ -f "$INSTALL_LOG" ]; then LOG_PREEXISTED=true; else LOG_PREEXISTED=false; fi
exec > >(tee -a "$INSTALL_LOG") 2>&1

log()  { echo -e "${DIM}[$(date '+%H:%M:%S')]${NC} $*"; }
info() { echo -e "${LCYAN}  ➤${NC} $*"; }
ok()   { echo -e "${LGREEN}  ✔${NC} $*"; }
warn() { echo -e "${YELLOW}  ⚠${NC} $*"; }
fail() { echo -e "${LRED}  ✘${NC} $*"; }
die()  {
    echo ""
    echo -e "${LRED}╔══ FATAL ERROR ══════════════════════════════╗${NC}"
    echo -e "${LRED}║  $*${NC}"
    echo -e "${LRED}╚═════════════════════════════════════════════╝${NC}"
    echo ""
    exit 1
}

section() { echo -e "\n${BOLD}${MAGENTA}  ◆ $*${NC}"; }

ui_cols() {
    local c="${COLUMNS:-}"
    if [ -z "$c" ] && [ -t 0 ]; then c="$(tput cols </dev/tty 2>/dev/null || true)"; fi
    [ -z "$c" ] && c="$(tput cols 2>/dev/null || true)"
    case "$c" in ''|*[!0-9]*) c=80;; esac
    [ "$c" -gt 100 ] && c=100
    [ "$c" -lt 46 ] && c=46
    printf '%s' "$c"
}

ui_repeat() {
    local n="$1" ch="${2:-─}" s
    [ "$n" -lt 0 ] && n=0
    s="$(printf '%*s' "$n" '')"
    printf '%s' "${s// /$ch}"
}

ui_trim() {
    local val="$1" max="$2"
    if [ "${#val}" -le "$max" ]; then printf '%s' "$val"; else printf '%s…' "${val:0:$((max-1))}"; fi
}

ui_section() {
    local label="$1" w inner avail l r
    w="$(ui_cols)"; inner=$((w-2)); avail=$((inner-${#label}-2))
    [ "$avail" -lt 4 ] && avail=4
    l=$((avail/2)); r=$((avail-l))
    printf '\n  %b%s%b %s %b%s%b\n' "$UI_BORDER" "$(ui_repeat "$l")" "$UI_TEXT" "$label" "$UI_BORDER" "$(ui_repeat "$r")" "$NC" >&2
}

ui_kv() {
    local k="$1" v="$2" w max
    w="$(ui_cols)"; max=$((w-20)); [ "$max" -lt 10 ] && max=10
    printf '  %b%-16s%b %s\n' "$UI_MUTED" "$k" "$NC" "$(ui_trim "$v" "$max")" >&2
}

print_rule() { printf "  %b─────────────────────────────────────────────────────────────%b\n" "$UI_BORDER" "$NC"; }

info_row() {
    local label="$1" value="${2:--}" color="${3:-$UI_TEXT}"
    printf "  %b▌%b %b%-14s%b %b%s%b\n" "$UI_ACCENT" "$NC" "$UI_MUTED" "$label" "$NC" "$color" "$value" "$NC"
}

fmt_dur() {
    local t="${1:-0}" out=""
    [ "$t" -lt 0 ] 2>/dev/null && t=0
    local d=$((t/86400)) h=$(((t%86400)/3600)) m=$(((t%3600)/60)) s=$((t%60))
    [ "$d" -gt 0 ] && out="${out}${d}d "
    [ "$h" -gt 0 ] && out="${out}${h}h "
    [ "$m" -gt 0 ] && out="${out}${m}m "
    out="${out}${s}s"
    echo "$out"
}

press_enter() {
    printf "  %b❯%b Press Enter to return to menu..." "$UI_ACCENT" "$NC"
    read -r _ || true
}

make_bar() {
    local filled=$1 empty=$2 bar="" i=0
    while [ $i -lt $filled ]; do bar="${bar}█"; i=$((i+1)); done
    i=0
    while [ $i -lt $empty ]; do bar="${bar}░"; i=$((i+1)); done
    echo "$bar"
}

step_header() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    local pct=$(( CURRENT_STEP * 100 / TOTAL_STEPS ))
    local filled=$(( pct / 5 )) empty=$(( 20 - filled )) bar
    bar=$(make_bar "$filled" "$empty")
    echo ""
    echo -e "${BOLD}${LBLUE}┌─[${NC}${WHITE}${CURRENT_STEP}/${TOTAL_STEPS}${NC}${BOLD}${LBLUE}]────────────────────────────────────────────┐${NC}"
    echo -e "${BOLD}${LBLUE}│${NC}  ${BOLD}${WHITE}$1${NC}"
    echo -e "${BOLD}${LBLUE}│${NC}  ${LGREEN}${bar}${NC} ${DIM}${pct}%${NC}"
    echo -e "${BOLD}${LBLUE}└──────────────────────────────────────────────┘${NC}"
}

# Interactive y/n. 0 = yes, 1 = no. Defaults to NO on EOF / no TTY.
prompt_yes_no() {
    local prompt="$1" answer=""
    if { : < /dev/tty; } 2>/dev/null; then
        printf "  ${YELLOW}%s [y/N]: ${NC}" "$prompt" > /dev/tty 2>/dev/null
        read -r answer < /dev/tty 2>/dev/null || answer=""
    elif [ -t 0 ]; then
        printf "  ${YELLOW}%s [y/N]: ${NC}" "$prompt"
        read -r answer || answer=""
    else
        return 1
    fi
    case "$answer" in
        [Yy]|[Yy][Ee][Ss]) return 0 ;;
        *) return 1 ;;
    esac
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ZFS / STORAGE-LIMIT HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
zfs_module_available() {
    [ -e /sys/module/zfs ] && return 0
    modprobe zfs >/dev/null 2>&1 && return 0
    return 1
}

zfs_usable() {
    zfs_module_available || return 1
    local t="lxd-zfstest-$$"
    if lxc storage create "$t" zfs size=1GiB >/dev/null 2>&1; then
        lxc storage delete "$t" >/dev/null 2>&1 || true
        return 0
    fi
    lxc storage delete "$t" >/dev/null 2>&1 || true
    return 1
}

install_zfs_support() {
    local kver; kver="$(uname -r)"
    case "$ENV_TYPE" in
        proxmox|debian|ubuntu)
            pkg_try zfsutils-linux; pkg_try "linux-modules-extra-${kver}"
            pkg_try "linux-headers-${kver}"; pkg_try zfs-dkms ;;
        centos|fedora) pkg_try zfs ;;
        arch) pkg_try zfs-linux ;;
        alpine) pkg_try zfs ;;
        *) pkg_try zfsutils-linux ;;
    esac
    depmod -a >/dev/null 2>&1 || true
    modprobe zfs >/dev/null 2>&1 || true
    zfs_module_available
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PACKAGE MANAGER ABSTRACTION (multi-distro)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
pkg_install() {
    case "$ENV_TYPE" in
        proxmox|debian|ubuntu)
            DEBIAN_FRONTEND=noninteractive apt-get install -y \
                -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" "$@" ;;
        centos) dnf install -y "$@" 2>/dev/null || yum install -y "$@" ;;
        fedora) dnf install -y "$@" ;;
        arch)   pacman -Sy --noconfirm "$@" ;;
        alpine) apk add --no-cache "$@" ;;
        *)      DEBIAN_FRONTEND=noninteractive apt-get install -y \
                    -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" "$@" 2>/dev/null || true ;;
    esac
}

# Non-fatal install (never aborts the script).
pkg_try() {
    case "$ENV_TYPE" in
        proxmox|debian|ubuntu)
            DEBIAN_FRONTEND=noninteractive apt-get install -y \
                -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" "$@" >/dev/null 2>&1 ;;
        centos|fedora) dnf install -y "$@" >/dev/null 2>&1 ;;
        arch)   pacman -Sy --noconfirm "$@" >/dev/null 2>&1 ;;
        alpine) apk add --no-cache "$@" >/dev/null 2>&1 ;;
        *)      DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "$@" >/dev/null 2>&1 ;;
    esac
}

pkg_update() {
    case "$ENV_TYPE" in
        proxmox|debian|ubuntu) apt-get update -y >/dev/null 2>&1 || true ;;
        centos) dnf update -y >/dev/null 2>&1 || true ;;
        fedora) dnf upgrade -y >/dev/null 2>&1 || true ;;
        arch)   pacman -Syu --noconfirm >/dev/null 2>&1 || true ;;
        alpine) apk update >/dev/null 2>&1 || true ;;
        *)      apt-get update -y >/dev/null 2>&1 || true ;;
    esac
}

# Proxmox apt-hook bypass helpers
proxmox_safe_install() {
    if [ "$ENV_TYPE" = "proxmox" ]; then
        touch /please-remove-proxmox-ve 2>/dev/null || true
        DEBIAN_FRONTEND=noninteractive apt-get install -y \
            -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" "$@" >/dev/null 2>&1
        rm -f /please-remove-proxmox-ve 2>/dev/null || true
    else
        pkg_install "$@"
    fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BANNER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
banner() {
    clear 2>/dev/null || true
    echo -e "${BOLD}${CYAN}"
    cat <<'EOF'
   ███████╗ ██████╗ ███╗   ███╗    ███╗   ██╗ ██████╗ ██████╗ ███████╗
   ██╔════╝██╔════╝ ████╗ ████║    ████╗  ██║██╔═══██╗██╔══██╗██╔════╝
   ███████╗██║  ███╗██╔████╔██║    ██╔██╗ ██║██║   ██║██║  ██║█████╗
   ╚════██║██║   ██║██║╚██╔╝██║    ██║╚██╗██║██║   ██║██║  ██║██╔══╝
   ███████║╚██████╔╝██║ ╚═╝ ██║    ██║ ╚████║╚██████╔╝██████╔╝███████╗
   ╚══════╝ ╚═════╝ ╚═╝     ╚═╝    ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝
EOF
    echo -e "${NC}"
    echo -e "${BOLD}${WHITE}             SGM NODE — LXD VPS host + remote control API${NC}"
    echo -e "${DIM}             SGM-ORG-LTD-V • INSTALLER & API CONTROL PANEL${NC}"
    echo ""
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DETECTION ENGINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
detect_env() {
    section "Detecting Operating System"
    local os_id="" os_name="" os_version=""
    if [ -f /etc/os-release ]; then
        os_id=$(grep -m1 "^ID=" /etc/os-release | cut -d= -f2 | tr -d '"' | tr '[:upper:]' '[:lower:]')
        os_name=$(grep -m1 "^NAME=" /etc/os-release | cut -d= -f2 | tr -d '"')
        os_version=$(grep -m1 "^VERSION_ID=" /etc/os-release | cut -d= -f2 | tr -d '"')
    fi
    if [ -d /etc/pve ] || command -v pvesh >/dev/null 2>&1; then
        ENV_TYPE="proxmox"; os_name="Proxmox VE"
        os_version=$(pvesh get /version --output-format=json 2>/dev/null | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
        [ -z "$os_version" ] && os_version="8.x"
    elif echo "$os_id" | grep -qi "^ubuntu$";   then ENV_TYPE="ubuntu"
    elif echo "$os_id" | grep -qi "^debian$";   then ENV_TYPE="debian"
    elif echo "$os_id" | grep -qiE "^centos|^rhel|^almalinux|^rocky"; then ENV_TYPE="centos"
    elif echo "$os_id" | grep -qi "^fedora$";   then ENV_TYPE="fedora"
    elif echo "$os_id" | grep -qi "^arch$";     then ENV_TYPE="arch"
    elif echo "$os_id" | grep -qi "^alpine$";   then ENV_TYPE="alpine"
    else ENV_TYPE="unknown"; fi

    local icon
    case "$ENV_TYPE" in
        proxmox) icon="🖥️ " ;; ubuntu) icon="🟠" ;; debian) icon="🌀" ;;
        centos)  icon="🎩" ;; fedora) icon="🔵" ;; arch)   icon="🏹" ;;
        alpine)  icon="⛰️ " ;; *)      icon="❓" ;;
    esac
    echo -e "  ${BOLD}${icon} OS Detected:${NC}  ${WHITE}${os_name} ${os_version}${NC}"
    echo -e "  ${BOLD}   Type:${NC}        ${LCYAN}${ENV_TYPE}${NC}"
    echo -e "  ${BOLD}   Kernel:${NC}      ${DIM}$(uname -r)${NC}"
    echo -e "  ${BOLD}   Arch:${NC}        ${DIM}$(uname -m)${NC}"
    log "Environment: $ENV_TYPE | OS: $os_name $os_version"
}

detect_virtualization() {
    section "Detecting Virtualization & Container Context"
    local virt="unknown"
    if command -v systemd-detect-virt >/dev/null 2>&1; then
        virt=$(systemd-detect-virt 2>/dev/null || echo "none")
    fi
    [ "$virt" = "none" ] && virt="bare-metal"
    [ -f /.dockerenv ] && virt="docker"
    grep -q "lxc" /proc/1/cgroup 2>/dev/null && virt="lxc"
    case "$virt" in
        bare-metal|kvm|qemu|vmware|virtualbox|microsoft)
            echo -e "  ${GREEN}✔${NC} Virtualization: ${WHITE}${virt}${NC} ${GREEN}(LXD nesting supported)${NC}" ;;
        lxc|openvz)
            echo -e "  ${YELLOW}⚠${NC} Virtualization: ${WHITE}${virt}${NC} ${YELLOW}(nested LXD may need host nesting flag)${NC}" ;;
        docker)
            echo -e "  ${RED}✘${NC} Virtualization: ${WHITE}docker${NC} ${RED}(LXD inside Docker is unsupported)${NC}"
            fail "Running inside Docker — LXD cannot be installed here" ;;
        *)
            echo -e "  ${YELLOW}⚠${NC} Virtualization: ${WHITE}${virt}${NC} ${YELLOW}(unknown — proceeding carefully)${NC}" ;;
    esac
    log "Virtualization: $virt"
}

detect_resources() {
    section "Checking System Resources"
    local ram_kb ram_gb; ram_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    ram_gb=$(awk "BEGIN {printf \"%.1f\", $ram_kb/1048576}")
    if [ "$ram_kb" -lt 1048576 ]; then
        echo -e "  ${RED}✘${NC} RAM: ${WHITE}${ram_gb} GB${NC} ${RED}(min 1 GB)${NC}"; fail "Insufficient RAM: ${ram_gb}GB"
    elif [ "$ram_kb" -lt 2097152 ]; then
        echo -e "  ${YELLOW}⚠${NC} RAM: ${WHITE}${ram_gb} GB${NC} ${YELLOW}(2 GB recommended)${NC}"
    else
        echo -e "  ${GREEN}✔${NC} RAM: ${WHITE}${ram_gb} GB${NC} ${GREEN}(OK)${NC}"
    fi
    local disk_avail disk_gb; disk_avail=$(df / --output=avail -B1 2>/dev/null | tail -1)
    disk_gb=$(awk "BEGIN {printf \"%.1f\", $disk_avail/1073741824}")
    if [ "$disk_avail" -lt 5368709120 ]; then
        echo -e "  ${RED}✘${NC} Disk: ${WHITE}${disk_gb} GB free${NC} ${RED}(min 5 GB)${NC}"; fail "Insufficient disk: ${disk_gb}GB"
    elif [ "$disk_avail" -lt 10737418240 ]; then
        echo -e "  ${YELLOW}⚠${NC} Disk: ${WHITE}${disk_gb} GB free${NC} ${YELLOW}(10 GB recommended)${NC}"
    else
        echo -e "  ${GREEN}✔${NC} Disk: ${WHITE}${disk_gb} GB free${NC} ${GREEN}(OK)${NC}"
    fi
    local cores; cores=$(nproc)
    if [ "$cores" -lt 2 ]; then
        echo -e "  ${YELLOW}⚠${NC} CPU: ${WHITE}${cores} core(s)${NC} ${YELLOW}(2+ recommended)${NC}"
    else
        echo -e "  ${GREEN}✔${NC} CPU: ${WHITE}${cores} core(s)${NC} ${GREEN}(OK)${NC}"
    fi
    log "Resources: RAM=${ram_gb}GB Disk=${disk_gb}GB CPU=${cores}"
}

detect_public_ip() {
    section "Detecting Public IP & Network Topology"
    MAIN_IFACE=$(ip route get 8.8.8.8 2>/dev/null | grep -oP 'dev\s+\K\S+' | head -1)
    [ -z "$MAIN_IFACE" ] && MAIN_IFACE=$(ip route | grep default | awk '{print $5}' | head -1)
    [ -z "$MAIN_IFACE" ] && MAIN_IFACE="eth0"
    HOST_PRIVATE_IP=$(ip -4 addr show "$MAIN_IFACE" 2>/dev/null | grep -oP 'inet\s+\K[\d.]+' | head -1)
    PUBLIC_IP=$(curl -sS --connect-timeout 5 --max-time 10 https://api.ipify.org 2>/dev/null || echo "")
    echo -e "  ${GREEN}✔${NC} Main interface:    ${WHITE}${MAIN_IFACE}${NC} (${HOST_PRIVATE_IP})"
    if [ -n "$PUBLIC_IP" ]; then
        echo -e "  ${GREEN}✔${NC} Public IPv4:       ${WHITE}${PUBLIC_IP}${NC}"
    else
        echo -e "  ${YELLOW}⚠${NC} Public IPv4:       ${YELLOW}not detected${NC}"
    fi
    log "Public IP: $PUBLIC_IP | Interface: $MAIN_IFACE"
}

detect_network() {
    section "Checking Network Connectivity"
    if ping -c 1 -W 3 8.8.8.8 >/dev/null 2>&1; then
        echo -e "  ${GREEN}✔${NC} Internet (ping 8.8.8.8):  ${GREEN}reachable${NC}"
    else
        echo -e "  ${RED}✘${NC} Internet (ping 8.8.8.8):  ${RED}unreachable${NC}"; fail "No internet — cannot download packages"
    fi
    if curl -s --max-time 5 https://pypi.org >/dev/null 2>&1; then
        echo -e "  ${GREEN}✔${NC} PyPI / repos:              ${GREEN}reachable${NC}"
    else
        echo -e "  ${YELLOW}⚠${NC} PyPI / repos:              ${YELLOW}may be slow${NC}"
    fi
}

detect_existing_services() {
    section "Checking Existing Services & Conflicts"
    if command -v lxd >/dev/null 2>&1; then
        echo -e "  ${YELLOW}⚠${NC} LXD found — will be reconfigured/reused"
    else
        echo -e "  ${GREEN}✔${NC} No existing LXD — clean install"
    fi
    if command -v snap >/dev/null 2>&1; then
        SNAP_AVAILABLE=true; LXD_METHOD="snap"
        echo -e "  ${GREEN}✔${NC} Snapd available — LXD via snap"
    else
        SNAP_AVAILABLE=false; LXD_METHOD="apt"
        echo -e "  ${YELLOW}⚠${NC} Snap not available — will use apt LXC fallback"
    fi
}

detect_kernel_features() {
    section "Checking Kernel Capabilities"
    if grep -qE "^cgroup2" /proc/mounts 2>/dev/null; then
        echo -e "  ${GREEN}✔${NC} cgroup v2:  ${GREEN}active${NC}"
    elif [ -d /sys/fs/cgroup ]; then
        echo -e "  ${YELLOW}⚠${NC} cgroup v1:  ${YELLOW}active (v2 preferred)${NC}"
    else
        echo -e "  ${RED}✘${NC} cgroups:    ${RED}not found${NC}"; fail "No cgroup support — containers cannot run"
    fi
    local fwd; fwd=$(cat /proc/sys/net/ipv4/ip_forward 2>/dev/null || echo 0)
    if [ "$fwd" = "1" ]; then
        echo -e "  ${GREEN}✔${NC} IPv4 forwarding: ${GREEN}enabled${NC}"
    else
        echo -e "  ${YELLOW}⚠${NC} IPv4 forwarding: ${YELLOW}disabled (will enable)${NC}"
    fi
}

run_detection() {
    echo -e "${BOLD}${WHITE}"
    echo "  ╔══════════════════════════════════════════════════════════════╗"
    echo "  ║            🔍  ENVIRONMENT DETECTION ENGINE                 ║"
    echo "  ╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    sleep 0.3
    detect_env
    detect_virtualization
    detect_resources
    detect_public_ip
    detect_network
    detect_existing_services
    detect_kernel_features
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  EXISTING-ARTIFACT SCAN  +  REINSTALL-OR-ABORT PROMPT
#  (a re-run NEVER silently updates — it wipes everything or aborts)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FOUND_ARTIFACTS=()
add_artifact() { FOUND_ARTIFACTS+=("$1"); }

scan_existing_artifacts() {
    # Node install directory + identity files
    [ -d "$NODE_DIR" ] && add_artifact "Node directory:            $NODE_DIR"
    [ -f "$NODE_DIR/api-key" ] && add_artifact "API key file:              $NODE_DIR/api-key"
    [ -f "$NODE_DIR/node-id" ] && add_artifact "Node id file:              $NODE_DIR/node-id"
    [ -f "$NODE_DIR/config.json" ] && add_artifact "Config file:               $NODE_DIR/config.json"

    # systemd unit + service state
    [ -f /etc/systemd/system/sgm-node.service ] && add_artifact "systemd unit:              /etc/systemd/system/sgm-node.service"
    systemctl is-active --quiet sgm-node 2>/dev/null && add_artifact "Service state:             sgm-node is ACTIVE (running)"

    # Running API process
    pgrep -f "node-api.py" >/dev/null 2>&1 && add_artifact "Running process:           node-api.py"

    # Install log (only if it predates this run)
    [ "${LOG_PREEXISTED:-false}" = "true" ] && [ -f "$INSTALL_LOG" ] && add_artifact "Install log:               $INSTALL_LOG"

    # Stray copies anywhere obvious
    for f in /tmp/sgm-* /opt/node-api.py /root/node-api.py /home/*/node-api.py; do
        [ -e "$f" ] && add_artifact "Stray file:                $f"
    done

    # LXD artifacts (guard against a present-but-dead daemon, e.g. after snap removal)
    if command -v lxc >/dev/null 2>&1 && timeout 8 lxc info >/dev/null 2>&1; then
        local ct img p
        ct=$(timeout 8 lxc list --format csv -c n 2>/dev/null | grep -c . || true)
        img=$(timeout 8 lxc image list --format csv -c l 2>/dev/null | grep -c . || true)
        [ "${ct:-0}" -gt 0 ] && add_artifact "LXD containers:            ${ct} container(s)"
        [ "${img:-0}" -gt 0 ] && add_artifact "LXD images:                ${img} image(s)"
        for p in quota default; do
            timeout 8 lxc storage show "$p" >/dev/null 2>&1 && add_artifact "LXD storage pool:          $p"
        done
    fi
}

check_existing_and_prompt() {
    FOUND_ARTIFACTS=()
    scan_existing_artifacts

    if [ "${#FOUND_ARTIFACTS[@]}" -gt 0 ]; then
        if [ "${FORCE_CLEAN:-0}" = "1" ]; then
            warn "FORCE_CLEAN=1 — reinstall prompt skipped, wiping ALL existing artifacts"
        else
            echo ""
            echo -e "  ${LRED}╔══════════════════════════════════════════════════════════════╗${NC}"
            echo -e "  ${LRED}║   ⚠   SOME FILES ON THIS VPS ALREADY EXIST                   ║${NC}"
            echo -e "  ${LRED}╚══════════════════════════════════════════════════════════════╝${NC}"
            echo -e "  ${YELLOW}The following artifacts were found:${NC}"
            for a in "${FOUND_ARTIFACTS[@]}"; do
                echo -e "    ${WHITE}•${NC} $a"
            done
            echo ""
            echo -e "  ${LRED}Reinstalling will DELETE every item above and create a${NC}"
            echo -e "  ${LRED}brand-new node (new API key + new node id).${NC}"
            echo ""
            if prompt_yes_no "Reinstall everything and delete ALL existing files?"; then
                warn "Reinstall confirmed — ALL existing files will be destroyed."
            else
                echo ""
                warn "Aborted — nothing was changed. Existing node left untouched."
                return 1
            fi
        fi
    fi
    return 0
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 0: FULL CLEANUP (always — this is a fresh install)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
nuclear_cleanup() {
    step_header "🧹  Cleanup — Preparing Environment"
    if command -v lxd >/dev/null 2>&1 && command -v lxc >/dev/null 2>&1 && timeout 8 lxc info >/dev/null 2>&1; then
        info "Destroying existing LXD containers…"
        timeout 8 lxc list --format csv -c n 2>/dev/null | while read -r c; do
            [ -n "$c" ] && timeout 30 lxc delete "$c" --force 2>/dev/null || true
        done
        info "Removing existing LXD images…"
        timeout 8 lxc image list --format csv -c l 2>/dev/null | while read -r i; do
            [ -n "$i" ] && timeout 30 lxc image delete "$i" 2>/dev/null || true
        done
        info "Removing existing storage pools…"
        for p in quota default; do timeout 30 lxc storage delete "$p" 2>/dev/null || true; done
    fi
    info "Stopping and removing previous node install…"
    systemctl stop sgm-node 2>/dev/null || true
    systemctl disable sgm-node 2>/dev/null || true
    pkill -f "node-api.py" 2>/dev/null || true
    rm -f /etc/systemd/system/sgm-node.service
    systemctl daemon-reload 2>/dev/null || true
    rm -rf "$NODE_DIR"
    # Stray copies
    for f in /tmp/sgm-* /opt/node-api.py /root/node-api.py /home/*/node-api.py; do
        [ -e "$f" ] && rm -rf "$f" 2>/dev/null || true
    done
    ok "Cleanup complete — installing fresh"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 1: INSTALL LXD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
install_lxd() {
    step_header "📦  Installing LXD"
    if command -v lxd >/dev/null 2>&1 && command -v lxc >/dev/null 2>&1; then
        ok "LXD already installed ($(lxc version 2>/dev/null | awk -F': ' '/Server/{print $2}' | head -1))"
        return 0
    fi
    if [ "$ENV_TYPE" = "proxmox" ]; then
        info "Proxmox detected — ensuring container tools (LXD may already be present)…"
        proxmox_safe_install lxc >/dev/null 2>&1 || true
    fi
    pkg_try squashfs-tools
    if command -v snap >/dev/null 2>&1; then
        info "Installing LXD via snap…"
        snap install lxd >/dev/null 2>&1 || true
        snap start lxd >/dev/null 2>&1 || true
    fi
    if ! command -v lxd >/dev/null 2>&1; then
        info "Installing LXD via apt…"
        pkg_try lxd || pkg_try lxd-installer || die "Could not install LXD"
    fi
    command -v lxd >/dev/null 2>&1 || die "LXD binary not found after install"
    for _ in $(seq 1 30); do lxc info >/dev/null 2>&1 && break; sleep 1; done
    ok "LXD installed"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 2: INIT LXD + STORAGE (ZFS quota pool)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
create_quota_zfs_pool() {
    lxc storage create quota zfs size=${POOL_GIB}GiB >/dev/null 2>&1 || true
    lxc storage show quota >/dev/null 2>&1
}

init_lxd() {
    step_header "💾  Configuring Storage (ZFS quota pool)"
    TOTAL_GIB=$(( $(df -B1 --output=size / | tail -1) / 1073741824 ))
    POOL_GIB=$(( TOTAL_GIB - QUOTA_POOL_RESERVE_GB ))
    [ "$POOL_GIB" -lt 1 ] && POOL_GIB=$TOTAL_GIB

    lxd init --auto >/dev/null 2>&1 || true
    sleep 2

    if zfs_usable; then
        ok "ZFS detected and usable"
        info "Creating quota-enforced ZFS pool (${POOL_GIB}GiB)…"
        create_quota_zfs_pool || die "ZFS is usable but the quota pool could not be created"
        ACTIVE_POOL="quota"
    else
        warn "ZFS not available — attempting to install / enable it…"
        if install_zfs_support && zfs_usable; then
            ok "ZFS is now available"
            create_quota_zfs_pool || die "ZFS pool could not be created"
            ACTIVE_POOL="quota"
        else
            echo ""
            echo -e "  ${LRED}╔══════════════════════════════════════════════════════════════╗${NC}"
            echo -e "  ${LRED}║   ⚠   DISK LIMITS CANNOT BE ENFORCED ON THIS HOST          ║${NC}"
            echo -e "  ${LRED}╚══════════════════════════════════════════════════════════════╝${NC}"
            echo -e "  ${YELLOW}Without ZFS there is NO per-VPS disk limit — a single abusive${NC}"
            echo -e "  ${YELLOW}VPS can fill/crash the whole host disk.${NC}"
            echo ""
            if prompt_yes_no "Proceed WITHOUT disk limits? (y = continue, n = abort)"; then
                warn "Proceeding WITHOUT disk limits — the host disk is at risk."
                lxc storage create quota dir >/dev/null 2>&1 || true
                ACTIVE_POOL="quota"; NO_DISK_LIMIT=true
            else
                die "Installation aborted (ZFS unavailable)."
            fi
        fi
    fi
    lxc storage set quota size=${POOL_GIB}GiB >/dev/null 2>&1 || true

    info "Configuring default profile (root -> $ACTIVE_POOL)…"
    lxc profile device set default root pool "$ACTIVE_POOL" >/dev/null 2>&1 || \
        lxc profile device add default root disk path=/ pool="$ACTIVE_POOL" >/dev/null 2>&1 || true
    lxc profile device add default eth0 nic network=lxdbr0 name=eth0 >/dev/null 2>&1 || true
    lxc profile set default security.nesting true >/dev/null 2>&1 || true
    lxc profile set default security.privileged true >/dev/null 2>&1 || true
    # Remove unused 'default' pool if we use quota
    [ "$ACTIVE_POOL" = "quota" ] && lxc storage delete default >/dev/null 2>&1 || true
    ok "Storage ready: pool '${ACTIVE_POOL}' (${POOL_GIB} GiB, enforced: $([ "${NO_DISK_LIMIT:-false}" = true ] && echo NO || echo YES))"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 3: NETWORK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
setup_network() {
    step_header "🌐  Configuring Network (NAT)"
    lxc network create lxdbr0 ipv4.address=10.111.49.1/24 ipv4.nat=true >/dev/null 2>&1 || true
    lxc network set lxdbr0 ipv4.dhcp=true >/dev/null 2>&1 || true
    echo 1 > /proc/sys/net/ipv4/ip_forward 2>/dev/null || true
    grep -q '^net.ipv4.ip_forward=1' /etc/sysctl.conf 2>/dev/null || echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf
    sysctl -p >/dev/null 2>&1 || true
    ok "Bridge lxdbr0 ready (NAT enabled)"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 4: API DEPENDENCIES (isolated venv)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
install_api_deps() {
    step_header "🐍  Installing Node API (FastAPI + Uvicorn)"
    command -v python3 >/dev/null 2>&1 || die "python3 not found"
    pkg_try python3-pip; pkg_try python3-venv; pkg_try curl; pkg_try ca-certificates; pkg_try jq
    mkdir -p "$NODE_DIR"

    VENV_DIR="$NODE_DIR/venv"
    # Preferred: isolated virtualenv. Avoids clashing with Debian-managed packages
    # ("Cannot uninstall typing_extensions ... RECORD file not found").
    if python3 -m venv "$VENV_DIR" >/dev/null 2>&1; then
        "$VENV_DIR/bin/pip" install --quiet --upgrade pip >/dev/null 2>&1 || true
        info "Installing FastAPI + Uvicorn into venv…"
        "$VENV_DIR/bin/pip" install --quiet fastapi "uvicorn[standard]" pydantic 2>&1 | tail -3 || true
        if "$VENV_DIR/bin/python" -c "import fastapi, uvicorn, pydantic" >/dev/null 2>&1; then
            API_PYTHON="$VENV_DIR/bin/python"
            ok "Python API dependencies ready (venv: $VENV_DIR)"
            return 0
        fi
        warn "venv install failed — falling back to system pip"
    else
        warn "Could not create venv — falling back to system pip"
    fi

    info "Installing FastAPI + Uvicorn (system pip)…"
    pip3 install --quiet --break-system-packages --ignore-installed fastapi "uvicorn[standard]" pydantic 2>/dev/null \
        || pip3 install --quiet --ignore-installed fastapi "uvicorn[standard]" pydantic 2>/dev/null \
        || die "Failed to install Python web dependencies"
    python3 -c "import fastapi, uvicorn, pydantic" || die "FastAPI/Uvicorn import check failed"
    API_PYTHON="python3"
    ok "Python API dependencies ready (system)"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 5: WRITE API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
download_api_code() {
    local target="$1" tmp="${1}.new"
    command -v curl >/dev/null 2>&1 || pkg_try curl

    info "Fetching API code from GitHub…"
    info "  $NODE_API_URL"
    rm -f "$tmp"
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL --connect-timeout 15 --max-time 120 "$NODE_API_URL" -o "$tmp" \
            || { rm -f "$tmp"; fail "Could not download $NODE_API_FILE from GitHub"; return 1; }
    elif command -v wget >/dev/null 2>&1; then
        wget -qO "$tmp" --timeout=120 "$NODE_API_URL" \
            || { rm -f "$tmp"; fail "Could not download $NODE_API_FILE from GitHub"; return 1; }
    else
        fail "curl or wget is required to download the API code"
        return 1
    fi

    [ -s "$tmp" ] || { rm -f "$tmp"; fail "Downloaded API file is empty"; return 1; }
    [ "$(wc -c < "$tmp")" -gt 10000 ] || { rm -f "$tmp"; fail "Downloaded API file looks invalid (too small)"; return 1; }
    head -n 1 "$tmp" | grep -q '^#!.*python' || { rm -f "$tmp"; fail "Downloaded file is not a Python API source"; return 1; }
    grep -q 'SGM NODE API' "$tmp" || { rm -f "$tmp"; fail "Downloaded file is not the SGM Node API"; return 1; }
    python3 -m py_compile "$tmp" || { rm -f "$tmp"; fail "$NODE_API_FILE failed to compile"; return 1; }

    chmod 755 "$tmp"
    mv -f "$tmp" "$target"
    return 0
}

write_api() {
    step_header "🛠️  Installing SGM Node API"
    mkdir -p "$NODE_DIR"
    download_api_code "$NODE_DIR/node-api.py" \
        || die "Could not install the API from GitHub. Check $NODE_API_URL"
    ok "API installed from GitHub: $NODE_API_FILE"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 6: IDENTITY (API key, node id)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
gen_identity() {
    step_header "🔑  Generating Node Identity"
    umask 077
    if [ -f "$NODE_DIR/api-key" ]; then
        API_KEY="$(cat "$NODE_DIR/api-key")"; info "Reusing existing API key"
    else
        if command -v openssl >/dev/null 2>&1; then API_KEY="$(openssl rand -hex 32)"
        else API_KEY="$(head -c 32 /dev/urandom | od -An -tx1 | tr -d ' \n')"; fi
        printf '%s' "$API_KEY" > "$NODE_DIR/api-key"
    fi
    chmod 600 "$NODE_DIR/api-key"

    if [ -f "$NODE_DIR/node-id" ]; then
        NODE_ID="$(cat "$NODE_DIR/node-id")"
    else
        NODE_ID="sgm-$(head -c 3 /dev/urandom | od -An -tx1 | tr -d ' \n')"
        printf '%s' "$NODE_ID" > "$NODE_DIR/node-id"
    fi

    NODE_NAME="${SGM_NODE_NAME:-$(hostname)}"
    printf '%s' "$NODE_NAME" > "$NODE_DIR/node-name"
    [ -z "$PUBLIC_IP" ] && PUBLIC_IP="$(curl -sS --max-time 6 https://api.ipify.org 2>/dev/null || echo '')"
    [ -n "$PUBLIC_IP" ] && printf '%s' "$PUBLIC_IP" > "$NODE_DIR/public-ip"

    cat > "$NODE_DIR/config.json" <<EOF
{
  "node_id": "$NODE_ID",
  "node_name": "$NODE_NAME",
  "port": $NODE_PORT,
  "bind": "$NODE_BIND",
  "storage_pool": "$ACTIVE_POOL",
  "public_ip": "$PUBLIC_IP",
  "installed_at": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
}
EOF
    chmod 600 "$NODE_DIR/config.json"
    ok "Node ID: $NODE_ID"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 7: SYSTEMD SERVICE + HEALTH CHECK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
resolve_api_python() {
    if [ -x "$NODE_DIR/venv/bin/python" ]; then
        printf '%s' "$NODE_DIR/venv/bin/python"
    elif [ -n "${API_PYTHON:-}" ] && [ -x "$API_PYTHON" ]; then
        printf '%s' "$API_PYTHON"
    elif command -v python3 >/dev/null 2>&1; then
        command -v python3
    else
        printf '%s' "/usr/bin/python3"
    fi
}

write_service_unit() {
    local api_py
    api_py="$(resolve_api_python)"
    cat > /etc/systemd/system/sgm-node.service <<EOF
[Unit]
Description=SGM Node API
After=network-online.target snap.lxd.daemon.service
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$NODE_DIR
Environment=SGM_NODE_DIR=$NODE_DIR
Environment=SGM_NODE_PORT=$NODE_PORT
Environment=SGM_BIND_HOST=$NODE_BIND
Environment=SGM_STORAGE_POOL=$ACTIVE_POOL
ExecStart=$api_py $NODE_DIR/node-api.py
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
}

install_service() {
    step_header "⚙️  Installing systemd service (sgm-node)"
    write_service_unit
    systemctl daemon-reload
    systemctl enable sgm-node >/dev/null 2>&1 || true
    systemctl restart sgm-node
    sleep 2
    systemctl is-active --quiet sgm-node && ok "sgm-node service is running" \
        || fail "sgm-node failed to start — see: journalctl -u sgm-node -n 50"
}

health_check() {
    step_header "🩺  Health Check"
    local tries=0
    while [ "$tries" -lt 15 ]; do
        if curl -fsS --max-time 3 -H "X-API-Key: $API_KEY" "http://127.0.0.1:${NODE_PORT}/health" >/dev/null 2>&1; then
            ok "API reachable on 127.0.0.1:${NODE_PORT}"
            return 0
        fi
        tries=$((tries + 1)); sleep 1
    done
    warn "API did not respond to the local health check — check: journalctl -u sgm-node -n 50"
    return 0
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SUMMARY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
summary() {
    local ip="$PUBLIC_IP"; [ -n "$ip" ] || ip="<your-server-ip>"
    echo ""
    echo -e "${BOLD}${LGREEN}══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BOLD}${LGREEN}   SGM NODE INSTALLED SUCCESSFULLY${NC}"
    echo -e "${BOLD}${LGREEN}══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BOLD}  Node ID     :${NC} ${LCYAN}${NODE_ID}${NC}"
    echo -e "${BOLD}  Node Name   :${NC} ${NODE_NAME}"
    echo -e "${BOLD}  Storage     :${NC} ${ACTIVE_POOL} (${POOL_GIB} GiB)"
    echo -e "${BOLD}  Endpoint    :${NC} http://${ip}:${NODE_PORT}"
    echo ""
    echo -e "${BOLD}${YELLOW}  ── API KEY (keep this secret!) ──${NC}"
    echo -e "${BOLD}${WHITE}  ${API_KEY}${NC}"
    echo ""
    echo -e "${BOLD}  Connect from the bot:${NC}"
    echo -e "  ${GREEN}\$connect-vps ${ip}:${NODE_PORT} ${API_KEY}${NC}"
    echo ""
    echo -e "${DIM}  Test:  curl -H \"X-API-Key: \$KEY\" http://127.0.0.1:${NODE_PORT}/info-vps${NC}"
    echo -e "${DIM}  Svc:   systemctl status sgm-node | Logs: journalctl -u sgm-node -f${NC}"
    echo -e "${DIM}  API source: ${NODE_API_URL}${NC}"
    echo ""
    echo -e "${BOLD}${YELLOW}  NEXT STEPS${NC}"
    echo -e "  1. Open TCP ${NODE_PORT} in your cloud firewall / security group (or use a"
    echo -e "     Cloudflare Tunnel you set up yourself:"
    echo -e "       ${DIM}cloudflared tunnel --url http://127.0.0.1:${NODE_PORT}${NC})"
    echo -e "  2. Add in Discord:  ${GREEN}\$connect-vps <endpoint> <api-key>${NC}"
    echo ""
    echo -e "${DIM}  Install log: ${INSTALL_LOG}${NC}"
    echo ""
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CONTROL PANEL HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
require_root() { [ "$(id -u)" -eq 0 ] || die "Run as root:  sudo bash $0"; }

load_node_meta() {
    API_KEY=""
    if [ -f "$NODE_DIR/api-key" ]; then API_KEY="$(cat "$NODE_DIR/api-key" 2>/dev/null || true)"; fi
    if [ -f "$NODE_DIR/node-id" ]; then NODE_ID="$(cat "$NODE_DIR/node-id" 2>/dev/null || true)"; fi
    if [ -f "$NODE_DIR/node-name" ]; then NODE_NAME="$(cat "$NODE_DIR/node-name" 2>/dev/null || true)"; fi
    if [ -f "$NODE_DIR/config.json" ] && command -v python3 >/dev/null 2>&1; then
        local meta
        meta="$(python3 - "$NODE_DIR/config.json" <<'PY'
import json, sys
try:
    with open(sys.argv[1], 'r', encoding='utf-8') as fh:
        d = json.load(fh)
except Exception:
    d = {}
print('\t'.join(str(d.get(k, '') or '') for k in
                ('node_id', 'node_name', 'port', 'bind', 'storage_pool', 'public_ip')))
PY
)"
        local nid nname nport nbind npool nip
        IFS=$'\t' read -r nid nname nport nbind npool nip <<< "$meta"
        [ -n "$nid" ] && NODE_ID="$nid"
        [ -n "$nname" ] && NODE_NAME="$nname"
        [ -n "$nport" ] && NODE_PORT="$nport"
        [ -n "$nbind" ] && NODE_BIND="$nbind"
        [ -n "$npool" ] && ACTIVE_POOL="$npool"
        [ -n "$nip" ] && PUBLIC_IP="$nip"
    fi
}

node_state() {
    if [ -f /etc/systemd/system/sgm-node.service ] || systemctl list-unit-files 2>/dev/null | grep -q '^sgm-node\.service'; then
        if systemctl is-active --quiet sgm-node 2>/dev/null; then echo "RUNNING"; else echo "STOPPED"; fi
        return 0
    fi
    if [ -d "$NODE_DIR" ]; then echo "NO SERVICE"; else echo "NOT INSTALLED"; fi
}

api_local_host() {
    case "${NODE_BIND:-0.0.0.0}" in
        0.0.0.0|''|::) printf '127.0.0.1' ;;
        *) printf '%s' "$NODE_BIND" ;;
    esac
}

api_health() {
    [ -n "${API_KEY:-}" ] || return 1
    command -v curl >/dev/null 2>&1 || return 1
    curl -fsS --max-time 3 -H "X-API-Key: $API_KEY" \
        "http://$(api_local_host):${NODE_PORT}/health" >/dev/null 2>&1
}

wait_api_health() {
    local i=0
    while [ "$i" -lt 10 ]; do
        api_health && return 0
        i=$((i + 1)); sleep 1
    done
    return 1
}

node_container_count() {
    if command -v lxc >/dev/null 2>&1; then
        timeout 8 lxc list --format csv -c n 2>/dev/null | grep -c . || true
    else
        echo "0"
    fi
}

node_lxd_version() {
    if command -v lxc >/dev/null 2>&1; then
        timeout 8 lxc version 2>/dev/null | awk -F': ' '/Server/{print $2}' | head -1
    fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ACTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
do_install() {
    clear 2>/dev/null || true
    banner
    CURRENT_STEP=0
    TOTAL_STEPS=9
    NO_DISK_LIMIT=false
    run_detection
    if ! check_existing_and_prompt; then
        sleep 1
        show_menu
        return 1
    fi
    nuclear_cleanup
    pkg_update
    install_lxd
    init_lxd
    setup_network
    install_api_deps
    write_api
    gen_identity
    install_service
    health_check
    summary
    press_enter
    load_node_meta
    show_menu
}

do_update_api() {
    clear 2>/dev/null || true
    banner
    load_node_meta
    local st; st="$(node_state)"
    if [ "$st" = "NOT INSTALLED" ] || [ "$st" = "NO SERVICE" ]; then
        warn "Node API is not installed. Use option 1 (Install NODE) first."
        sleep 3; show_menu; return 1
    fi
    ui_section "UPDATE API — GITHUB"
    echo -e "  ${UI_MUTED}This downloads the latest ${NODE_API_FILE} from GitHub and replaces only:${NC}"
    echo -e "  ${UI_MUTED}  ${NODE_DIR}/node-api.py${NC}"
    echo -e "  ${UI_MUTED}Node identity, API key, config and LXD containers are kept.${NC}"
    echo -e "  ${DIM}  ${NODE_API_URL}${NC}"
    echo ""
    if ! prompt_yes_no "Update API code from GitHub and restart?"; then
        warn "Update cancelled."
        sleep 1; show_menu; return 1
    fi
    if [ -x "$NODE_DIR/venv/bin/python" ] && "$NODE_DIR/venv/bin/python" -c "import fastapi, uvicorn, pydantic" >/dev/null 2>&1; then
        API_PYTHON="$NODE_DIR/venv/bin/python"
        info "Python dependencies already installed."
    else
        install_api_deps
    fi
    if ! download_api_code "$NODE_DIR/node-api.py"; then
        warn "Update failed — existing API file was left untouched."
        sleep 3; show_menu; return 1
    fi
    ok "API code updated from GitHub: $NODE_API_FILE"
    write_service_unit
    systemctl daemon-reload >/dev/null 2>&1 || true
    systemctl restart sgm-node >/dev/null 2>&1 || true
    sleep 2
    if systemctl is-active --quiet sgm-node; then
        log "API code updated from GitHub."
        wait_api_health && log "API health check passed." || warn "Service is active but health check failed."
    else
        fail "API failed to start after update."
        journalctl -u sgm-node -n 15 --no-pager 2>/dev/null | tail -n 15 || true
    fi
    sleep 1
    show_menu
}

do_edit() {
    clear 2>/dev/null || true
    banner
    load_node_meta
    local st; st="$(node_state)"
    if [ "$st" = "NOT INSTALLED" ] || [ "$st" = "NO SERVICE" ]; then
        warn "Node API is not installed as a service. Use option 1 (Install NODE) first."
        sleep 3; show_menu; return 1
    fi
    ui_section "EDIT API SETTINGS"
    ui_kv "Current port" "$NODE_PORT"
    ui_kv "Current bind" "$NODE_BIND"
    echo
    local newport newbind
    printf "  %bNew port%b [%s]: " "$UI_TEXT" "$NC" "$NODE_PORT"
    read -r newport || newport=""
    [ -z "$newport" ] && newport="$NODE_PORT"
    case "$newport" in
        ''|*[!0-9]*) warn "Invalid port — keeping $NODE_PORT."; newport="$NODE_PORT" ;;
        *) if [ "$newport" -lt 1 ] || [ "$newport" -gt 65535 ]; then warn "Port out of range — keeping $NODE_PORT."; newport="$NODE_PORT"; fi ;;
    esac
    printf "  %bNew bind%b [%s]: " "$UI_TEXT" "$NC" "$NODE_BIND"
    read -r newbind || newbind=""
    [ -z "$newbind" ] && newbind="$NODE_BIND"

    NODE_PORT="$newport"
    NODE_BIND="$newbind"
    if [ -f "$NODE_DIR/config.json" ] && command -v python3 >/dev/null 2>&1; then
        python3 - "$NODE_DIR/config.json" "$NODE_PORT" "$NODE_BIND" <<'PY'
import json, sys
path = sys.argv[1]
try:
    with open(path, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
except Exception:
    data = {}
data['port'] = int(sys.argv[2])
data['bind'] = sys.argv[3]
with open(path, 'w', encoding='utf-8') as fh:
    json.dump(data, fh, indent=2)
    fh.write('\n')
PY
    fi
    write_service_unit
    systemctl daemon-reload >/dev/null 2>&1 || true
    systemctl restart sgm-node >/dev/null 2>&1 || true
    sleep 2
    if systemctl is-active --quiet sgm-node; then
        log "API restarted on ${NODE_BIND}:${NODE_PORT}."
        wait_api_health && log "API health check passed." || warn "Service is active but health check failed."
    else
        fail "API failed to start. Recent logs:"
        journalctl -u sgm-node -n 15 --no-pager 2>/dev/null | tail -n 15 || true
    fi
    sleep 1
    show_menu
}

do_cleanup_node() {
    clear 2>/dev/null || true
    banner
    local st; st="$(node_state)"
    if [ "$st" = "NOT INSTALLED" ] && [ ! -d "$NODE_DIR" ]; then
        warn "Node API is not installed. Nothing to clean up."
        sleep 2; show_menu; return 1
    fi
    ui_section "CLEANUP NODE API"
    echo -e "  ${YELLOW}This removes the sgm-node service, its config, API key and node identity.${NC}"
    echo -e "  ${YELLOW}LXD containers and VPS data are NOT deleted.${NC}"
    echo ""
    if ! prompt_yes_no "Remove the SGM Node API from this host?"; then
        warn "Cleanup cancelled."
        sleep 1; show_menu; return 1
    fi
    systemctl stop sgm-node >/dev/null 2>&1 || true
    systemctl disable sgm-node >/dev/null 2>&1 || true
    pkill -f "node-api.py" >/dev/null 2>&1 || true
    rm -f /etc/systemd/system/sgm-node.service
    systemctl daemon-reload >/dev/null 2>&1 || true
    rm -rf "$NODE_DIR"
    ok "Node API removed. LXD containers were left untouched."
    sleep 1
    show_menu
}

do_show_key() {
    clear 2>/dev/null || true
    banner
    load_node_meta
    local st; st="$(node_state)"
    if [ "$st" = "NOT INSTALLED" ]; then
        warn "Node API is not installed."
        sleep 2; show_menu; return 1
    fi
    local ip="$PUBLIC_IP"; [ -n "$ip" ] || ip="<your-server-ip>"
    ui_section "NODE CONNECTION DETAILS"
    ui_kv "Node ID" "${NODE_ID:--}"
    ui_kv "Node Name" "${NODE_NAME:--}"
    ui_kv "Endpoint" "http://${ip}:${NODE_PORT}"
    ui_kv "Bind" "${NODE_BIND}:${NODE_PORT}"
    ui_kv "Storage Pool" "${ACTIVE_POOL:--}"
    echo ""
    echo -e "  ${BOLD}${YELLOW}API KEY (keep this secret)${NC}"
    echo -e "  ${BOLD}${WHITE}${API_KEY:--}${NC}"
    echo ""
    echo -e "  ${BOLD}Connect from Discord:${NC}"
    echo -e "  ${GREEN}\$connect-vps ${ip}:${NODE_PORT} ${API_KEY}${NC}"
    echo ""
    press_enter
    show_menu
}

do_info() {
    clear 2>/dev/null || true
    banner
    load_node_meta
    local st; st="$(node_state)"
    local sc="$YELLOW"
    [ "$st" = "RUNNING" ] && sc="$GREEN"
    [ "$st" = "STOPPED" ] && sc="$RED"

    local enabled="-" pid="-" uptime="-" cpu="-" mem="-" restarts="-" health="unreachable" hc="$RED"
    if [ "$st" = "RUNNING" ] || [ "$st" = "STOPPED" ]; then
        enabled="$(systemctl is-enabled sgm-node 2>/dev/null || true)"; [ -z "$enabled" ] && enabled="-"
        pid="$(systemctl show -p MainPID --value sgm-node 2>/dev/null || true)"
        { [ -z "$pid" ] || [ "$pid" = "0" ]; } && pid="-"
        restarts="$(systemctl show -p NRestarts --value sgm-node 2>/dev/null || true)"; [ -z "$restarts" ] && restarts="-"
        if [ "$st" = "RUNNING" ]; then
            local since secs
            since="$(systemctl show -p ActiveEnterTimestamp --value sgm-node 2>/dev/null || true)"
            if [ -n "$since" ]; then
                secs="$(date -d "$since" +%s 2>/dev/null || echo 0)"
                if [ "$secs" -gt 0 ] 2>/dev/null; then uptime="$(fmt_dur "$(( $(date +%s) - secs ))")"; fi
            fi
            api_health && { health="reachable"; hc="$GREEN"; }
        fi
    fi
    if [ -n "$pid" ] && [ "$pid" != "-" ]; then
        local pc pu
        pc="$(ps -o %cpu= -p "$pid" 2>/dev/null | tr -d ' ' || true)"; [ -n "$pc" ] && cpu="${pc}%"
        pu="$(ps -o rss= -p "$pid" 2>/dev/null | tr -d ' ' || true)"; [ -n "$pu" ] && mem="$(awk -v k="$pu" 'BEGIN{printf "%.1f MB", k/1024}')"
    fi

    local ip="$PUBLIC_IP"; [ -n "$ip" ] || ip="<your-server-ip>"
    local lxdver; lxdver="$(node_lxd_version)"; [ -z "$lxdver" ] && lxdver="not installed"
    local ct; ct="$(node_container_count)"

    ui_section "NODE API INFORMATION"
    info_row "Status" "$st" "$sc"
    info_row "Health" "$health" "$hc"
    info_row "Service" "systemd (sgm-node)"
    info_row "Enabled" "$enabled"
    info_row "PID" "$pid"
    info_row "Uptime" "$uptime" "$UI_ACCENT"
    info_row "CPU" "$cpu"
    info_row "Memory" "$mem"
    info_row "Restarts" "$restarts"
    print_rule
    info_row "Node ID" "${NODE_ID:--}"
    info_row "Node Name" "${NODE_NAME:--}"
    info_row "Endpoint" "http://${ip}:${NODE_PORT}"
    info_row "Bind" "${NODE_BIND}:${NODE_PORT}"
    info_row "Storage" "${ACTIVE_POOL:--}"
    info_row "API Key" "$( [ -n "$API_KEY" ] && echo 'configured (hidden)' || echo 'missing' )"
    info_row "LXD" "$lxdver"
    info_row "Containers" "$ct"
    info_row "Install Dir" "$NODE_DIR"
    info_row "Log" "$INSTALL_LOG"
    print_rule
    echo -e "  ${DIM}Reboot API restarts only the sgm-node service, not the host.${NC}"
    echo ""
    press_enter
    show_menu
}

do_start() {
    local st; st="$(node_state)"
    if [ "$st" = "RUNNING" ]; then warn "API is already running."; sleep 2; show_menu; return 0; fi
    if [ "$st" = "NOT INSTALLED" ] || [ "$st" = "NO SERVICE" ]; then
        warn "API is not installed. Use option 1 (Install NODE) first."
        sleep 3; show_menu; return 1
    fi
    load_node_meta
    log "Starting SGM Node API..."
    systemctl reset-failed sgm-node >/dev/null 2>&1 || true
    systemctl start sgm-node >/dev/null 2>&1 || true
    sleep 2
    if systemctl is-active --quiet sgm-node; then
        log "API started."
        wait_api_health && log "API health check passed." || warn "Service is active but health check failed."
    else
        fail "API failed to start."
        journalctl -u sgm-node -n 15 --no-pager 2>/dev/null | tail -n 15 || true
    fi
    sleep 2; show_menu
}

do_reboot() {
    local st; st="$(node_state)"
    if [ "$st" != "RUNNING" ]; then
        warn "API is not running. Use option 6 (Start API) instead."
        sleep 3; show_menu; return 1
    fi
    load_node_meta
    log "Rebooting SGM Node API..."
    systemctl reset-failed sgm-node >/dev/null 2>&1 || true
    systemctl restart sgm-node >/dev/null 2>&1 || true
    sleep 2
    if systemctl is-active --quiet sgm-node; then
        log "API rebooted."
        wait_api_health && log "API health check passed." || warn "Service is active but health check failed."
    else
        fail "API failed to start after reboot."
        journalctl -u sgm-node -n 15 --no-pager 2>/dev/null | tail -n 15 || true
    fi
    sleep 2; show_menu
}

do_shutdown() {
    local st; st="$(node_state)"
    if [ "$st" != "RUNNING" ]; then warn "API is not running. Nothing to shut down."; sleep 3; show_menu; return 1; fi
    log "Shutting down SGM Node API..."
    systemctl stop sgm-node >/dev/null 2>&1 || true
    sleep 2
    if systemctl is-active --quiet sgm-node; then
        fail "API is still running."
    else
        log "API shut down. Containers keep running."
    fi
    sleep 2; show_menu
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAIN MENU
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
show_menu() {
    clear 2>/dev/null || true
    banner
    load_node_meta
    local st sc can_start=0 can_stop=0
    st="$(node_state)"
    case "$st" in RUNNING) sc="$GREEN";; STOPPED) sc="$RED";; *) sc="$YELLOW";; esac
    if [ "$st" = "RUNNING" ]; then can_stop=1; elif [ "$st" = "STOPPED" ]; then can_start=1; fi
    printf "  %b╭────────────────────────────────────────────────────────────╮%b\n" "$UI_BORDER" "$NC"
    printf "  %b│%b  %bSGM NODE CONTROL PANEL%b\n" "$UI_BORDER" "$NC" "$UI_TEXT" "$NC"
    printf "  %b│%b  %bStatus%b   %b● %s%b\n" "$UI_BORDER" "$NC" "$UI_MUTED" "$NC" "$sc" "$st" "$NC"
    printf "  %b│%b  %bAPI%b      %b%s%b\n" "$UI_BORDER" "$NC" "$UI_MUTED" "$NC" "$UI_ACCENT" "GitHub • code updates only" "$NC"
    printf "  %b╰────────────────────────────────────────────────────────────╯%b\n\n" "$UI_BORDER" "$NC"
    printf "  %b[1]%b  %bInstall NODE%b       %bFresh install / reinstall the API host%b\n" "$GREEN" "$NC" "$UI_TEXT" "$NC" "$UI_MUTED" "$NC"
    printf "  %b[2]%b  %bUpdate API%b         %bUpdate only API code from GitHub%b\n" "$CYAN" "$NC" "$UI_TEXT" "$NC" "$UI_MUTED" "$NC"
    printf "  %b[3]%b  %bEdit API%b           %bChange port / bind and restart%b\n" "$CYAN" "$NC" "$UI_TEXT" "$NC" "$UI_MUTED" "$NC"
    printf "  %b[4]%b  %bCleanUP NODE%b      %bRemove service and local node files%b\n" "$RED" "$NC" "$UI_TEXT" "$NC" "$UI_MUTED" "$NC"
    printf "  %b[5]%b  %bINFO%b               %bService, health and node details%b\n" "$UI_ACCENT" "$NC" "$UI_TEXT" "$NC" "$UI_MUTED" "$NC"
    if [ "$can_start" = "1" ]; then
        printf "  %b[6]%b  %bStart API%b          %bStart the stopped API%b\n" "$GREEN" "$NC" "$UI_TEXT" "$NC" "$UI_MUTED" "$NC"
    else
        printf "  %b[6]%b  %bStart API%b          %bUnavailable - API is %s%b\n" "$UI_MUTED" "$NC" "$UI_MUTED" "$NC" "$UI_MUTED" "$( [ "$st" = "RUNNING" ] && echo running || echo 'not installed' )" "$NC"
    fi
    if [ "$can_stop" = "1" ]; then
        printf "  %b[7]%b  %bReboot API%b         %bRestart the running API service%b\n" "$YELLOW" "$NC" "$UI_TEXT" "$NC" "$UI_MUTED" "$NC"
        printf "  %b[8]%b  %bShutdown API%b       %bStop the running API service%b\n" "$RED" "$NC" "$UI_TEXT" "$NC" "$UI_MUTED" "$NC"
    else
        printf "  %b[7]%b  %bReboot API%b         %bUnavailable - API is not running%b\n" "$UI_MUTED" "$NC" "$UI_MUTED" "$NC" "$UI_MUTED" "$NC"
        printf "  %b[8]%b  %bShutdown API%b       %bUnavailable - API is not running%b\n" "$UI_MUTED" "$NC" "$UI_MUTED" "$NC" "$UI_MUTED" "$NC"
    fi
    printf "  %b[9]%b  %bShow API KEY%b       %bEndpoint and connect-vps command%b\n" "$MAGENTA" "$NC" "$UI_TEXT" "$NC" "$UI_MUTED" "$NC"
    printf "  %b[0]%b  %bExit%b\n\n" "$UI_MUTED" "$NC" "$UI_TEXT" "$NC"
    printf "  %b❯%b Select option %b[0-9]%b: " "$UI_ACCENT" "$NC" "$UI_MUTED" "$NC"
    local opt
    if ! read -r opt; then log "Goodbye."; exit 0; fi
    echo
    case "$opt" in
        1) do_install ;;
        2) do_update_api ;;
        3) do_edit ;;
        4) do_cleanup_node ;;
        5) do_info ;;
        6) do_start ;;
        7) do_reboot ;;
        8) do_shutdown ;;
        9) do_show_key ;;
        0|q|Q) log "Goodbye."; exit 0 ;;
        *) warn "Invalid option"; sleep 2; show_menu ;;
    esac
}

main() {
    require_root
    case "${1:-}" in
        install|--install|-i) do_install ;;
        *) show_menu ;;
    esac
}

main "$@"
