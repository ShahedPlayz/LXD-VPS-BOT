#!/bin/bash
# ╔══════════════════════════════════════════════════════════════════════════╗
# ║         MagnexHostSYS — Ultimate Auto Installer v6.1 (FIXED)             ║
# ║              Environment-Aware • Self-Healing • Production               ║
# ║                      Made with ❤️ • by SGM Company                       ║
# ╚══════════════════════════════════════════════════════════════════════════╝

export DEBIAN_FRONTEND=noninteractive
export PATH=$PATH:/snap/bin:/usr/local/sbin:/usr/sbin:/sbin

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  COLORS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RED='\033[0;31m'
LRED='\033[1;31m'
GREEN='\033[0;32m'
LGREEN='\033[1;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
LCYAN='\033[1;36m'
BLUE='\033[0;34m'
LBLUE='\033[1;34m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
GRAY='\033[0;37m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GLOBAL STATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ENV_TYPE=""
ENV_USABLE=false
ISSUES=()
WARNINGS=()
SNAP_AVAILABLE=false
LXD_METHOD="snap"
TOTAL_STEPS=9
CURRENT_STEP=0
LOG_FILE="/var/log/magnexhost-install.log"
START_TIME=$(date +%s)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LOGGING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
mkdir -p "$(dirname "$LOG_FILE")"
exec > >(tee -a "$LOG_FILE") 2>&1

log()  { echo -e "${DIM}[$(date '+%H:%M:%S')]${NC} $*"; }
info() { echo -e "${LCYAN}  ➤${NC} $*"; }
ok()   { echo -e "${LGREEN}  ✔${NC} $*"; }
warn() { echo -e "${YELLOW}  ⚠${NC} $*"; WARNINGS+=("$*"); }
fail() { echo -e "${LRED}  ✘${NC} $*"; ISSUES+=("$*"); }
die()  {
    echo ""
    echo -e "${LRED}╔══ FATAL ERROR ══════════════════════════════╗${NC}"
    echo -e "${LRED}║  $*"
    echo -e "${LRED}╚═════════════════════════════════════════════╝${NC}"
    echo ""
    exit 1
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PROGRESS BAR (no seq, pure bash)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
make_bar() {
    local filled=$1
    local empty=$2
    local bar=""
    local i=0
    while [ $i -lt $filled ]; do
        bar="${bar}█"
        i=$((i+1))
    done
    i=0
    while [ $i -lt $empty ]; do
        bar="${bar}░"
        i=$((i+1))
    done
    echo "$bar"
}

step_header() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    local pct=$(( CURRENT_STEP * 100 / TOTAL_STEPS ))
    local filled=$(( pct / 5 ))
    local empty=$(( 20 - filled ))
    local bar
    bar=$(make_bar "$filled" "$empty")
    echo ""
    echo -e "${BOLD}${LBLUE}┌─[${NC}${WHITE}${CURRENT_STEP}/${TOTAL_STEPS}${NC}${BOLD}${LBLUE}]────────────────────────────────────────────┐${NC}"
    echo -e "${BOLD}${LBLUE}│${NC}  ${BOLD}${WHITE}$1${NC}"
    echo -e "${BOLD}${LBLUE}│${NC}  ${LGREEN}${bar}${NC} ${DIM}${pct}%${NC}"
    echo -e "${BOLD}${LBLUE}└────────────────────────────────────────────────┘${NC}"
}

section() {
    echo -e "\n${BOLD}${MAGENTA}  ◆ $*${NC}"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BANNER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
clear
echo -e "${LGREEN}"
echo "  ╔══════════════════════════════════════════════════════════════╗"
echo "  ║  ███╗   ███╗ █████╗  ██████╗ ███╗   ██╗███████╗██╗  ██╗    ║"
echo "  ║  ████╗ ████║██╔══██╗██╔════╝ ████╗  ██║██╔════╝╚██╗██╔╝    ║"
echo "  ║  ██╔████╔██║███████║██║  ███╗██╔██╗ ██║█████╗   ╚███╔╝     ║"
echo "  ║  ██║╚██╔╝██║██╔══██║██║   ██║██║╚██╗██║██╔══╝   ██╔██╗     ║"
echo "  ║  ██║ ╚═╝ ██║██║  ██║╚██████╔╝██║ ╚████║███████╗██╔╝ ██╗    ║"
echo "  ║  ╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝    ║"
echo "  ╠══════════════════════════════════════════════════════════════╣"
echo -e "  ║${NC}${BOLD}${WHITE}           MAGNEX HOST  —  VPS BOT SYSTEM                     ${NC}${LGREEN}║"
echo -e "  ║${NC}${DIM}         Smart Auto Installer v6.1  •  Environment-Aware       ${NC}${LGREEN}║"
echo "  ╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
sleep 1

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ROOT CHECK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[ "$EUID" -ne 0 ] && die "Run as root!  Try: sudo bash $0"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DETECTION ENGINE HEADER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo -e "${BOLD}${WHITE}"
echo "  ╔══════════════════════════════════════════════════════════════╗"
echo "  ║            🔍  ENVIRONMENT DETECTION ENGINE                 ║"
echo "  ╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
sleep 0.3

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DETECT OS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
detect_env() {
    section "Detecting Operating System"

    local os_id="" os_name="" os_version=""

    if [ -f /etc/os-release ]; then
        os_id=$(grep -m1 "^ID=" /etc/os-release | cut -d= -f2 | tr -d '"' | tr '[:upper:]' '[:lower:]')
        os_name=$(grep -m1 "^NAME=" /etc/os-release | cut -d= -f2 | tr -d '"')
        os_version=$(grep -m1 "^VERSION_ID=" /etc/os-release | cut -d= -f2 | tr -d '"')
    fi

    # Proxmox detection (takes priority over debian)
    if [ -d /etc/pve ] || command -v pvesh >/dev/null 2>&1; then
        ENV_TYPE="proxmox"
        os_name="Proxmox VE"
        # Get version cleanly — just the number
        os_version=$(pvesh get /version --output-format=json 2>/dev/null | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
        if [ -z "$os_version" ]; then
            os_version=$(cat /usr/share/doc/proxmox-ve/changelog.Debian.gz 2>/dev/null | zcat 2>/dev/null | grep -m1 "proxmox-ve" | grep -o '[0-9]\+\.[0-9]\+\.[0-9]*' | head -1)
        fi
        if [ -z "$os_version" ]; then
            os_version=$(dpkg -l proxmox-ve 2>/dev/null | grep "^ii" | awk '{print $3}' | cut -d'-' -f1)
        fi
        [ -z "$os_version" ] && os_version="8.x"
    elif echo "$os_id" | grep -qi "^ubuntu$"; then
        ENV_TYPE="ubuntu"
    elif echo "$os_id" | grep -qi "^debian$"; then
        ENV_TYPE="debian"
    elif echo "$os_id" | grep -qi "^centos\|^rhel\|^almalinux\|^rocky"; then
        ENV_TYPE="centos"
    elif echo "$os_id" | grep -qi "^fedora$"; then
        ENV_TYPE="fedora"
    elif echo "$os_id" | grep -qi "^arch$"; then
        ENV_TYPE="arch"
    elif echo "$os_id" | grep -qi "^alpine$"; then
        ENV_TYPE="alpine"
    else
        ENV_TYPE="unknown"
    fi

    local icon
    case "$ENV_TYPE" in
        proxmox) icon="🖥️ " ;;
        ubuntu)  icon="🟠" ;;
        debian)  icon="🌀" ;;
        centos)  icon="🎩" ;;
        fedora)  icon="🔵" ;;
        arch)    icon="🏹" ;;
        alpine)  icon="⛰️ " ;;
        *)       icon="❓" ;;
    esac

    echo -e "  ${BOLD}${icon} OS Detected:${NC}  ${WHITE}${os_name} ${os_version}${NC}"
    echo -e "  ${BOLD}   Type:${NC}        ${LCYAN}${ENV_TYPE}${NC}"
    echo -e "  ${BOLD}   Kernel:${NC}      ${DIM}$(uname -r)${NC}"
    echo -e "  ${BOLD}   Arch:${NC}        ${DIM}$(uname -m)${NC}"
    log "Environment: $ENV_TYPE | OS: $os_name $os_version"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DETECT VIRTUALIZATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
            echo -e "  ${GREEN}✔${NC} Virtualization: ${WHITE}${virt}${NC} ${GREEN}(LXD nesting supported)${NC}"
            ;;
        lxc|openvz)
            echo -e "  ${YELLOW}⚠${NC} Virtualization: ${WHITE}${virt}${NC} ${YELLOW}(nested LXD may need host nesting flag)${NC}"
            warn "Running inside LXC/OpenVZ — nested containers may need host-side nesting enabled"
            ;;
        docker)
            echo -e "  ${RED}✘${NC} Virtualization: ${WHITE}docker${NC} ${RED}(LXD inside Docker is unsupported)${NC}"
            fail "Running inside Docker — LXD cannot be installed here"
            ;;
        *)
            echo -e "  ${YELLOW}⚠${NC} Virtualization: ${WHITE}${virt}${NC} ${YELLOW}(unknown — proceeding carefully)${NC}"
            warn "Unknown virtualization: $virt"
            ;;
    esac

    log "Virtualization: $virt"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DETECT RESOURCES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
detect_resources() {
    section "Checking System Resources"

    # RAM
    local ram_kb ram_gb
    ram_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    ram_gb=$(awk "BEGIN {printf \"%.1f\", $ram_kb/1048576}")

    if [ "$ram_kb" -lt 1048576 ]; then
        echo -e "  ${RED}✘${NC} RAM: ${WHITE}${ram_gb} GB${NC} ${RED}(minimum 1 GB required)${NC}"
        fail "Insufficient RAM: ${ram_gb}GB"
    elif [ "$ram_kb" -lt 2097152 ]; then
        echo -e "  ${YELLOW}⚠${NC} RAM: ${WHITE}${ram_gb} GB${NC} ${YELLOW}(2 GB recommended)${NC}"
        warn "Low RAM: ${ram_gb}GB"
    else
        echo -e "  ${GREEN}✔${NC} RAM: ${WHITE}${ram_gb} GB${NC} ${GREEN}(OK)${NC}"
    fi

    # Disk
    local disk_avail disk_avail_gb
    disk_avail=$(df / --output=avail -B1 2>/dev/null | tail -1)
    disk_avail_gb=$(awk "BEGIN {printf \"%.1f\", $disk_avail/1073741824}")

    if [ "$disk_avail" -lt 5368709120 ]; then
        echo -e "  ${RED}✘${NC} Disk: ${WHITE}${disk_avail_gb} GB free${NC} ${RED}(minimum 5 GB required)${NC}"
        fail "Insufficient disk: ${disk_avail_gb}GB"
    elif [ "$disk_avail" -lt 10737418240 ]; then
        echo -e "  ${YELLOW}⚠${NC} Disk: ${WHITE}${disk_avail_gb} GB free${NC} ${YELLOW}(10 GB recommended)${NC}"
        warn "Low disk: ${disk_avail_gb}GB"
    else
        echo -e "  ${GREEN}✔${NC} Disk: ${WHITE}${disk_avail_gb} GB free${NC} ${GREEN}(OK)${NC}"
    fi

    # CPU
    local cpu_cores
    cpu_cores=$(nproc)
    if [ "$cpu_cores" -lt 2 ]; then
        echo -e "  ${YELLOW}⚠${NC} CPU: ${WHITE}${cpu_cores} core(s)${NC} ${YELLOW}(2+ recommended)${NC}"
        warn "Single core CPU"
    else
        echo -e "  ${GREEN}✔${NC} CPU: ${WHITE}${cpu_cores} core(s)${NC} ${GREEN}(OK)${NC}"
    fi

    log "Resources: RAM=${ram_gb}GB Disk=${disk_avail_gb}GB CPU=${cpu_cores}"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PUBLIC IP / NAT / INTERFACE DETECTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PUBLIC_IP=""
PUBLIC_IPV6=""
MAIN_IFACE=""
HOST_PRIVATE_IP=""
BEHIND_NAT=false

detect_public_ip() {
    section "Detecting Public IP & Network Topology"

    MAIN_IFACE=$(ip route get 8.8.8.8 2>/dev/null | grep -oP 'dev\s+\K\S+' | head -1)
    [ -z "$MAIN_IFACE" ] && MAIN_IFACE=$(ip route | grep default | awk '{print $5}' | head -1)
    [ -z "$MAIN_IFACE" ] && MAIN_IFACE="eth0"

    HOST_PRIVATE_IP=$(ip -4 addr show "$MAIN_IFACE" 2>/dev/null | grep -oP 'inet\s+\K[\d.]+' | head -1)

    PUBLIC_IP=$(curl -sS --connect-timeout 5 --max-time 10 https://api.ipify.org 2>/dev/null || echo "")
    PUBLIC_IPV6=$(curl -sS --connect-timeout 5 --max-time 10 https://api6.ipify.org 2>/dev/null || echo "")

    echo -e "  ${GREEN}✔${NC} Main interface:    ${WHITE}${MAIN_IFACE}${NC} (${HOST_PRIVATE_IP})"

    if [ -n "$PUBLIC_IP" ]; then
        BEHIND_NAT=false
        # Check if public IP matches any local interface IP
        local match=false
        for iface_ip in $(ip -4 addr show | grep -oP 'inet\s+\K[\d.]+'); do
            if [ "$iface_ip" = "$PUBLIC_IP" ]; then
                match=true
                break
            fi
        done
        if [ "$match" = true ]; then
            echo -e "  ${GREEN}✔${NC} Public IPv4:       ${WHITE}${PUBLIC_IP}${NC} ${GREEN}(direct — on ${MAIN_IFACE})${NC}"
        else
            BEHIND_NAT=true
            echo -e "  ${YELLOW}⚠${NC} Public IPv4:       ${WHITE}${PUBLIC_IP}${NC} ${YELLOW}(behind NAT — not on local interface)${NC}"
            warn "Host appears to be behind NAT — containers will need port forwarding"
        fi
    else
        BEHIND_NAT=true
        echo -e "  ${RED}✘${NC} Public IPv4:       ${RED}not detected${NC}"
        warn "No public IPv4 detected — containers will be NAT-only"
    fi

    if [ -n "$PUBLIC_IPV6" ]; then
        echo -e "  ${GREEN}✔${NC} Public IPv6:       ${WHITE}${PUBLIC_IPV6}${NC}"
    else
        echo -e "  ${YELLOW}⚠${NC} Public IPv6:       ${YELLOW}not available${NC}"
    fi

    log "Public IP: $PUBLIC_IP | NAT: $BEHIND_NAT | Interface: $MAIN_IFACE"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DETECT NETWORK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
detect_network() {
    section "Checking Network Connectivity"

    if ping -c 1 -W 3 8.8.8.8 >/dev/null 2>&1; then
        echo -e "  ${GREEN}✔${NC} Internet (ping 8.8.8.8):  ${GREEN}reachable${NC}"
    else
        echo -e "  ${RED}✘${NC} Internet (ping 8.8.8.8):  ${RED}unreachable${NC}"
        fail "No internet — cannot download packages"
    fi

    if nslookup google.com 8.8.8.8 >/dev/null 2>&1 || host google.com >/dev/null 2>&1; then
        echo -e "  ${GREEN}✔${NC} DNS resolution:            ${GREEN}working${NC}"
    else
        echo -e "  ${YELLOW}⚠${NC} DNS resolution:            ${YELLOW}failed (8.8.8.8 fallback will be used)${NC}"
        warn "DNS may be broken — containers will have DNS forced to 8.8.8.8"
    fi

    if curl -s --max-time 5 http://deb.debian.org >/dev/null 2>&1; then
        echo -e "  ${GREEN}✔${NC} Package repos:            ${GREEN}reachable${NC}"
    else
        echo -e "  ${YELLOW}⚠${NC} Package repos:            ${YELLOW}may be slow${NC}"
        warn "Package repo may be slow or blocked"
    fi

    log "Network check done"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DETECT EXISTING SERVICES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
detect_existing_services() {
    section "Checking Existing Services & Conflicts"

    if command -v lxd >/dev/null 2>&1; then
        echo -e "  ${YELLOW}⚠${NC} LXD found — will be reconfigured"
        warn "Existing LXD found — installer will reset it"
    else
        echo -e "  ${GREEN}✔${NC} No existing LXD — clean install"
    fi

    if command -v docker >/dev/null 2>&1 && systemctl is-active docker >/dev/null 2>&1; then
        echo -e "  ${YELLOW}⚠${NC} Docker is running — iptables rules will coexist"
        warn "Docker detected — coexistence iptables rules will be added"
    else
        echo -e "  ${GREEN}✔${NC} Docker: not running (OK)"
    fi

    if [ "$ENV_TYPE" = "proxmox" ] && [ -f /usr/share/proxmox-ve/pve-apt-hook ]; then
        echo -e "  ${YELLOW}⚠${NC} Proxmox pve-apt-hook detected — will auto-bypass"
        warn "pve-apt-hook will be bypassed with the touch workaround"
    fi

    if command -v snap >/dev/null 2>&1; then
        SNAP_AVAILABLE=true
        LXD_METHOD="snap"
        echo -e "  ${GREEN}✔${NC} Snapd available — LXD will be installed via snap"
    else
        SNAP_AVAILABLE=false
        LXD_METHOD="apt"
        echo -e "  ${YELLOW}⚠${NC} Snap not available — will use apt LXC fallback"
        warn "Snap not found — using apt LXC"
    fi

    log "LXD method: $LXD_METHOD | Snap: $SNAP_AVAILABLE"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DETECT KERNEL CAPABILITIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
detect_kernel_features() {
    section "Checking Kernel Capabilities"

    # User namespaces
    if [ -f /proc/self/ns/user ]; then
        echo -e "  ${GREEN}✔${NC} User namespaces:  ${GREEN}enabled${NC}"
    else
        echo -e "  ${YELLOW}⚠${NC} User namespaces:  ${YELLOW}unknown${NC}"
        warn "User namespace support could not be confirmed"
    fi

    # cgroups
    if grep -qE "^cgroup2" /proc/mounts 2>/dev/null; then
        echo -e "  ${GREEN}✔${NC} cgroup v2:        ${GREEN}active${NC}"
    elif [ -d /sys/fs/cgroup ]; then
        echo -e "  ${YELLOW}⚠${NC} cgroup v1:        ${YELLOW}active (v2 preferred)${NC}"
        warn "cgroup v1 detected — LXD works, but v2 is preferred"
    else
        echo -e "  ${RED}✘${NC} cgroups:          ${RED}not found${NC}"
        fail "No cgroup support — containers cannot run"
    fi

    # SquashFS
    if modinfo squashfs >/dev/null 2>&1 || grep -q squashfs /proc/filesystems 2>/dev/null; then
        echo -e "  ${GREEN}✔${NC} SquashFS:         ${GREEN}available${NC}"
    else
        echo -e "  ${YELLOW}⚠${NC} SquashFS:         ${YELLOW}not loaded (will modprobe)${NC}"
        warn "SquashFS not loaded — installer will load it"
    fi

    # IP forwarding
    local fwd
    fwd=$(cat /proc/sys/net/ipv4/ip_forward 2>/dev/null || echo 0)
    if [ "$fwd" = "1" ]; then
        echo -e "  ${GREEN}✔${NC} IPv4 forwarding:  ${GREEN}enabled${NC}"
    else
        echo -e "  ${YELLOW}⚠${NC} IPv4 forwarding:  ${YELLOW}disabled (will enable)${NC}"
    fi

    # AppArmor
    if command -v aa-status >/dev/null 2>&1 && aa-status >/dev/null 2>&1; then
        echo -e "  ${YELLOW}⚠${NC} AppArmor:         ${YELLOW}active (may restrict containers)${NC}"
        warn "AppArmor active — check profiles if containers fail to start"
    else
        echo -e "  ${GREEN}✔${NC} AppArmor:         ${GREEN}not blocking${NC}"
    fi

    log "Kernel check done"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  RUN ALL DETECTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
detect_env
detect_virtualization
detect_resources
detect_public_ip
detect_network
detect_existing_services
detect_kernel_features

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  COMPATIBILITY REPORT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo ""
echo -e "${BOLD}${WHITE}"
echo "  ╔══════════════════════════════════════════════════════════════╗"
echo "  ║                  📋  COMPATIBILITY REPORT                   ║"
echo "  ╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

if [ ${#ISSUES[@]} -gt 0 ]; then
    ENV_USABLE=false
    echo -e "  ${LRED}❌ BLOCKING ISSUES:${NC}"
    for issue in "${ISSUES[@]}"; do
        echo -e "    ${RED}•${NC} $issue"
    done
    echo ""
else
    ENV_USABLE=true
fi

if [ ${#WARNINGS[@]} -gt 0 ]; then
    echo -e "  ${YELLOW}⚠  WARNINGS (non-blocking):${NC}"
    for w in "${WARNINGS[@]}"; do
    echo -e "    ${YELLOW}•${NC} $w"
done
echo ""
fi

echo -e "  ${BOLD}${GREEN}🌐 Network:${NC}"
echo -e "    ${GREEN}•${NC} Public IP:    ${WHITE}${PUBLIC_IP:-Not detected}${NC}"
echo -e "    ${GREEN}•${NC} Main Iface:   ${WHITE}${MAIN_IFACE:-auto}${NC}"
if [ "$BEHIND_NAT" = true ]; then
    echo -e "    ${YELLOW}•${NC} NAT:          ${YELLOW}Behind NAT (port forwarding will be used)${NC}"
else
    echo -e "    ${GREEN}•${NC} NAT:          ${GREEN}Direct public IP${NC}"
fi
echo ""

echo -e "  ${BOLD}${LCYAN}🔧 Environment Adaptations for: ${WHITE}${ENV_TYPE}${NC}"
case "$ENV_TYPE" in
    proxmox)
        echo -e "    ${GREEN}•${NC} pve-apt-hook will be auto-bypassed"
        echo -e "    ${GREEN}•${NC} proxmox-ve meta-package removal guard auto-handled"
        echo -e "    ${GREEN}•${NC} LXD via snap (best for Proxmox hosts)"
        echo -e "    ${GREEN}•${NC} Container nesting will be enabled in default profile"
        echo -e "    ${GREEN}•${NC} pve-no-subscription repo left untouched"
        ;;
    ubuntu)
        echo -e "    ${GREEN}•${NC} snap install lxd (native Ubuntu path)"
        echo -e "    ${GREEN}•${NC} pip with --break-system-packages as needed"
        ;;
    debian)
        echo -e "    ${GREEN}•${NC} snapd installed first, then LXD via snap"
        echo -e "    ${GREEN}•${NC} pip with --break-system-packages as needed"
        ;;
    centos|fedora)
        echo -e "    ${YELLOW}•${NC} dnf/yum used instead of apt"
        echo -e "    ${YELLOW}•${NC} SELinux policies may need manual adjustment"
        ;;
    arch)
        echo -e "    ${YELLOW}•${NC} pacman used for package management"
        ;;
    alpine)
        echo -e "    ${RED}•${NC} Alpine: LXD support is experimental"
        ;;
    *)
        echo -e "    ${YELLOW}•${NC} Unknown OS: using best-effort generic path"
        ;;
esac
echo ""

if [ "$ENV_USABLE" = false ]; then
    echo -e "  ${LRED}╔══════════════════════════════════════════════════════╗${NC}"
    echo -e "  ${LRED}║  INSTALLATION ABORTED — Fix the issues above first  ║${NC}"
    echo -e "  ${LRED}╚══════════════════════════════════════════════════════╝${NC}"
    exit 1
fi

echo -e "  ${LGREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "  ${LGREEN}║   ✅  Environment COMPATIBLE — starting install...  ║${NC}"
echo -e "  ${LGREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
sleep 1

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PACKAGE MANAGER ABSTRACTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
pkg_install() {
    case "$ENV_TYPE" in
        proxmox|debian|ubuntu)
            DEBIAN_FRONTEND=noninteractive apt-get install -y \
                -o Dpkg::Options::="--force-confdef" \
                -o Dpkg::Options::="--force-confold" \
                "$@"
            ;;
        centos)
            dnf install -y "$@" 2>/dev/null || yum install -y "$@"
            ;;
        fedora)
            dnf install -y "$@"
            ;;
        arch)
            pacman -Sy --noconfirm "$@"
            ;;
        alpine)
            apk add --no-cache "$@"
            ;;
        *)
            DEBIAN_FRONTEND=noninteractive apt-get install -y \
                -o Dpkg::Options::="--force-confdef" \
                -o Dpkg::Options::="--force-confold" \
                "$@" 2>/dev/null || true
            ;;
    esac
}

pkg_update() {
    case "$ENV_TYPE" in
        proxmox|debian|ubuntu)
            apt-get update -y
            DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
                -o Dpkg::Options::="--force-confdef" \
                -o Dpkg::Options::="--force-confold"
            ;;
        centos)
            dnf update -y 2>/dev/null || yum update -y
            ;;
        fedora)
            dnf upgrade -y
            ;;
        arch)
            pacman -Syu --noconfirm
            ;;
        alpine)
            apk update && apk upgrade
            ;;
        *)
            apt-get update -y 2>/dev/null || true
            ;;
    esac
}

# Helper: run apt purge while bypassing the Proxmox hook if needed
proxmox_safe_purge() {
    if [ "$ENV_TYPE" = "proxmox" ]; then
        touch /please-remove-proxmox-ve 2>/dev/null || true
        DEBIAN_FRONTEND=noninteractive apt-get purge -y \
            -o Dpkg::Options::="--force-confdef" \
            -o Dpkg::Options::="--force-confold" \
            "$@" 2>/dev/null || true
        rm -f /please-remove-proxmox-ve 2>/dev/null || true
    else
        DEBIAN_FRONTEND=noninteractive apt-get purge -y \
            -o Dpkg::Options::="--force-confdef" \
            -o Dpkg::Options::="--force-confold" \
            "$@" 2>/dev/null || true
    fi
}

# Helper: install lxc while bypassing Proxmox hook
proxmox_safe_install() {
    if [ "$ENV_TYPE" = "proxmox" ]; then
        touch /please-remove-proxmox-ve 2>/dev/null || true
        DEBIAN_FRONTEND=noninteractive apt-get install -y \
            -o Dpkg::Options::="--force-confdef" \
            -o Dpkg::Options::="--force-confold" \
            "$@" 2>/dev/null || true
        rm -f /please-remove-proxmox-ve 2>/dev/null || true
    else
        pkg_install "$@"
    fi
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 0: NUCLEAR CLEANUP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
step_header "🧹  Nuclear Cleanup — Removing Old State"

info "Stopping MagnexHostSYS service..."
systemctl stop MagnexHostSYS 2>/dev/null || true
pm2 stop all 2>/dev/null || true

info "Destroying existing LXD containers..."
for ct in $(lxc list --format csv -c n 2>/dev/null || true); do
    lxc delete "$ct" --force 2>/dev/null || true
done

info "Removing LXD images..."
for img in $(lxc image list --format csv -c l 2>/dev/null || true); do
    lxc image delete "$img" 2>/dev/null || true
done

info "Purging snap LXD..."
snap stop lxd 2>/dev/null || true
snap remove lxd --purge 2>/dev/null || true
pkill -9 lxd 2>/dev/null || true
pkill -9 lxc 2>/dev/null || true
pkill -9 lxcfs 2>/dev/null || true
systemctl stop lxc lxcfs 2>/dev/null || true

info "Purging apt LXC packages..."
proxmox_safe_purge lxc lxc-templates lxcfs lxc-utils liblxc1 liblxc-common

info "Removing stale data..."
rm -rf \
    /var/snap/lxd /snap/lxd /root/snap/lxd \
    /var/lib/lxc /var/lib/lxcfs /etc/lxc \
    /var/log/lxc /var/cache/lxd /run/lxd \
    /tmp/lxc* /tmp/lxd* /tmp/snap.lxd* \
    /var/lib/snapd/cache/* 2>/dev/null || true

ok "Cleanup complete"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 1: SYSTEM UPDATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
step_header "🔄  System Update"
info "Updating package lists and upgrading..."
pkg_update
ok "System updated"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 2: CORE PACKAGES & SNAP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
step_header "📦  Installing Core Packages & Fixing Snap"

info "Installing base packages..."
case "$ENV_TYPE" in
    proxmox|debian|ubuntu)
        pkg_install squashfs-tools snapd python3 python3-pip sqlite3 wget \
            iptables-persistent curl net-tools iproute2 bc dnsutils
        ;;
    centos|fedora)
        pkg_install squashfs-tools snapd python3 python3-pip sqlite wget \
            iptables-services curl net-tools iproute bind-utils bc
        ;;
    arch)
        pkg_install squashfs-tools snapd python python-pip sqlite wget \
            iptables curl net-tools iproute2 bind-tools bc
        ;;
    alpine)
        pkg_install squashfs-tools python3 py3-pip sqlite wget \
            curl iproute2 bc bind-tools
        ;;
esac

info "Loading squashfs module..."
modprobe squashfs 2>/dev/null || true
echo "squashfs" > /etc/modules-load.d/snap-squashfs.conf
systemctl restart systemd-modules-load 2>/dev/null || true

info "Starting and refreshing snapd..."
systemctl enable snapd 2>/dev/null || true
systemctl restart snapd 2>/dev/null || true
sleep 5
snap refresh 2>/dev/null || true

ok "Packages installed"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 3: LXD INSTALL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
step_header "🐧  Installing LXD  [method: ${LXD_METHOD}]"

case "$LXD_METHOD" in
    snap)
        info "Installing LXD via snap..."
        if snap list lxd >/dev/null 2>&1; then
            info "LXD snap already present — skipping install"
        else
            snap install lxd
        fi
        sleep 5
        snap start lxd
        lxd waitready --timeout=90
        ;;
    apt)
        info "Installing LXD via apt (snap unavailable)..."
        pkg_install lxd lxd-client 2>/dev/null || \
            pkg_install lxc lxc-templates 2>/dev/null || \
            die "Could not install LXD/LXC via any method"
        ;;
esac

info "Installing lxc userspace tools..."
proxmox_safe_install lxc

ok "LXD installed via ${LXD_METHOD}"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 4: LXD CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
step_header "⚙️   Configuring LXD"

info "Running lxd init..."
lxd init --auto 2>/dev/null || true
sleep 2

info "Setting up storage pool..."
lxc storage create default dir 2>/dev/null || true

info "Setting up network bridge..."
lxc network create lxdbr0 ipv4.address=10.111.49.1/24 ipv4.nat=true 2>/dev/null || true
lxc network set lxdbr0 ipv4.dhcp=true 2>/dev/null || true

info "Configuring default profile..."
lxc profile device add default root disk path=/ pool=default 2>/dev/null || true
lxc profile device add default eth0 nic network=lxdbr0 name=eth0 2>/dev/null || true

if [ "$ENV_TYPE" = "proxmox" ]; then
    info "Enabling container nesting (Proxmox host)..."
    lxc profile set default security.nesting true 2>/dev/null || true
    lxc profile set default security.privileged false 2>/dev/null || true
fi

ok "LXD configured"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 5: NETWORK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
step_header "🌐  Configuring Network  (Docker-Safe)"

info "Enabling IPv4 forwarding..."
echo "net.ipv4.ip_forward=1" > /etc/sysctl.d/99-lxc.conf
sysctl --system >/dev/null 2>&1 || true

# Detect which iptables backend to use
IPTABLES_CMD="iptables"
if command -v iptables-nft >/dev/null 2>&1; then
    IPTABLES_CMD="iptables-nft"
fi

# Add NAT rules idempotently — don't flush, Docker and other services may have rules
info "Adding NAT masquerade and forward rules..."
$IPTABLES_CMD -t nat -C POSTROUTING -s 10.111.49.0/24 ! -d 10.111.49.0/24 -j MASQUERADE 2>/dev/null || \
    $IPTABLES_CMD -t nat -A POSTROUTING -s 10.111.49.0/24 ! -d 10.111.49.0/24 -j MASQUERADE
$IPTABLES_CMD -t nat -C POSTROUTING -s 172.17.0.0/16 ! -d 172.17.0.0/16 -j MASQUERADE 2>/dev/null || \
    $IPTABLES_CMD -t nat -A POSTROUTING -s 172.17.0.0/16 ! -d 172.17.0.0/16 -j MASQUERADE 2>/dev/null || true
$IPTABLES_CMD -C FORWARD -i lxdbr0 -j ACCEPT 2>/dev/null || $IPTABLES_CMD -A FORWARD -i lxdbr0 -j ACCEPT
$IPTABLES_CMD -C FORWARD -o lxdbr0 -j ACCEPT 2>/dev/null || $IPTABLES_CMD -A FORWARD -o lxdbr0 -j ACCEPT
$IPTABLES_CMD -C FORWARD -i docker0 -o lxdbr0 -j ACCEPT 2>/dev/null || \
    $IPTABLES_CMD -A FORWARD -i docker0 -o lxdbr0 -j ACCEPT 2>/dev/null || true
$IPTABLES_CMD -C FORWARD -i lxdbr0 -o docker0 -j ACCEPT 2>/dev/null || \
    $IPTABLES_CMD -A FORWARD -i lxdbr0 -o docker0 -j ACCEPT 2>/dev/null || true

info "Saving firewall rules..."
if command -v netfilter-persistent-save >/dev/null 2>&1; then
    netfilter-persistent save 2>/dev/null || true
elif [ -d /etc/iptables ]; then
    $IPTABLES_CMD-save > /etc/iptables/rules.v4 2>/dev/null || true
fi

ok "Network configured"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 6: CONNECTIVITY TEST
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
step_header "🧪  Testing LXD + Internet Connectivity"

info "Launching test container (ubuntu:22.04)..."
lxc init ubuntu:22.04 test-net -s default 2>/dev/null || \
    warn "Could not init test container — skipping connectivity test"

if lxc info test-net >/dev/null 2>&1; then
    lxc start test-net 2>/dev/null
    sleep 8

    info "Injecting DNS resolvers into container..."
    lxc exec test-net -- bash -c \
        "chattr -i /etc/resolv.conf 2>/dev/null; printf 'nameserver 8.8.8.8\nnameserver 1.1.1.1\n' > /etc/resolv.conf" \
        2>/dev/null || true

    if lxc exec test-net -- ping -c 2 -W 3 8.8.8.8 2>/dev/null | grep -q "ttl="; then
        ok "Container ping: SUCCESS"
    else
        warn "Container ping failed — run fix-network after install if needed"
    fi

    if lxc exec test-net -- nslookup google.com 8.8.8.8 2>/dev/null | grep -q "Address:"; then
        ok "Container DNS: SUCCESS"
    else
        warn "Container DNS failed — run fix-dns after install if needed"
    fi

    lxc delete test-net --force 2>/dev/null || true
else
    warn "Test container skipped — verify LXD manually after install"
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 7: PYTHON MODULES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
step_header "🐍  Installing Python Modules"

info "Installing discord.py and aiohttp..."
PIP_FLAGS=""
python3 -m pip install --help 2>&1 | grep -q "break-system-packages" && \
    PIP_FLAGS="--break-system-packages"

python3 -m pip install -U discord.py aiohttp $PIP_FLAGS 2>/dev/null || \
    pip3 install -U discord.py aiohttp 2>/dev/null || \
    warn "pip install failed — run manually: pip3 install discord.py aiohttp"

ok "Python modules installed"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  STEP 8: BOT SETUP & SYSTEMD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
step_header "🤖  Setting Up Bot Service"

mkdir -p /opt/MagnexHostSYS

# Search for user's bot.py — exclude virtualenvs, dist-packages, snap paths,
# and known library bot.py files (discord internal, pip, etc.)
info "Searching for bot.py..."
BOT_PATH=$(find / \
    -name "bot.py" \
    -not -path "*/snap/*" \
    -not -path "*/proc/*" \
    -not -path "*/sys/*" \
    -not -path "*/opt/MagnexHostSYS/*" \
    -not -path "*/site-packages/*" \
    -not -path "*/dist-packages/*" \
    -not -path "*/.local/lib/*" \
    -not -path "*/lib/python*" \
    2>/dev/null | head -1)

if [ -n "$BOT_PATH" ] && [ -f "$BOT_PATH" ]; then
    cp "$BOT_PATH" /opt/MagnexHostSYS/bot.py
    ok "Bot copied from: $BOT_PATH"
else
    warn "bot.py not found — upload it to /opt/MagnexHostSYS/bot.py before starting the service"
fi

info "Creating systemd service unit..."
cat > /etc/systemd/system/MagnexHostSYS.service << 'SERVICE'
[Unit]
Description=MagnexHostSYS Discord VPS Bot
After=network.target snap.lxd.daemon.service
Wants=snap.lxd.daemon.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/MagnexHostSYS
ExecStart=/usr/bin/python3 /opt/MagnexHostSYS/bot.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin

[Install]
WantedBy=multi-user.target
SERVICE

info "Creating logrotate config..."
cat > /etc/logrotate.d/MagnexHostSYS << 'LOGROTATE'
/opt/MagnexHostSYS/bot.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
LOGROTATE

info "Installing fix-dns tool..."
cat > /usr/local/bin/fix-dns << 'FIXDNS'
#!/bin/bash
echo "Fixing DNS for all containers..."
for ct in $(lxc list -c n --format csv 2>/dev/null); do
    echo "  -> $ct"
    lxc exec "$ct" -- bash -c \
        "chattr -i /etc/resolv.conf 2>/dev/null; printf 'nameserver 8.8.8.8\nnameserver 1.1.1.1\n' > /etc/resolv.conf" \
        2>/dev/null || true
done
echo "Done!"
FIXDNS

info "Installing fix-network tool..."
cat > /usr/local/bin/fix-network << 'FIXNET'
#!/bin/bash
IPT=$(command -v iptables-nft 2>/dev/null || echo "iptables")
echo "Resetting iptables/NAT rules..."
# Only flush NAT table — leave filter rules intact (Docker, etc.)
$IPT -t nat -F 2>/dev/null || true
$IPT -t nat -X 2>/dev/null || true
$IPT -t nat -A POSTROUTING -s 10.111.49.0/24 ! -d 10.111.49.0/24 -j MASQUERADE
$IPT -A FORWARD -i lxdbr0 -j ACCEPT 2>/dev/null || true
$IPT -A FORWARD -o lxdbr0 -j ACCEPT 2>/dev/null || true
if command -v netfilter-persistent-save >/dev/null 2>&1; then
    netfilter-persistent save 2>/dev/null || true
elif [ -d /etc/iptables ]; then
    $IPT-save > /etc/iptables/rules.v4 2>/dev/null || true
fi
echo "Done!"
FIXNET

info "Installing magnex-status tool..."
cat > /usr/local/bin/magnex-status << 'STATUS'
#!/bin/bash
PUBLIC=$(curl -sS --connect-timeout 3 --max-time 5 https://api.ipify.org 2>/dev/null || echo "unknown")
echo ""
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "    MagnexHostSYS  —  Live Status"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
systemctl is-active MagnexHostSYS >/dev/null 2>&1 \
    && echo "    Bot:      RUNNING" \
    || echo "    Bot:      STOPPED"
snap services lxd 2>/dev/null | grep -q "active" \
    && echo "    LXD:      Active" \
    || echo "    LXD:      Unknown"
COUNT=$(lxc list --format csv -c n 2>/dev/null | wc -l)
echo "    VPS:      $COUNT container(s)"
echo "    Public IP: $PUBLIC"
echo "    Uptime:   $(uptime -p)"
echo "    Load:     $(cut -d' ' -f1-3 /proc/loadavg)"
FREE_GB=$(df / --output=avail -BG 2>/dev/null | tail -1 | tr -d 'G ')
echo "    Disk:     ${FREE_GB}GB free"
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
STATUS

chmod +x /usr/local/bin/fix-dns /usr/local/bin/fix-network /usr/local/bin/magnex-status

systemctl daemon-reload
ok "Bot service and helper tools installed"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  FINAL SUMMARY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
END_TIME=$(date +%s)
ELAPSED=$(( END_TIME - START_TIME ))
ELAPSED_MIN=$(( ELAPSED / 60 ))
ELAPSED_SEC=$(( ELAPSED % 60 ))

echo ""
echo -e "${LGREEN}"
echo "  ╔══════════════════════════════════════════════════════════════╗"
echo "  ║                                                              ║"
echo "  ║        🎉  INSTALLATION COMPLETE — ALL SYSTEMS GO!          ║"
echo "  ║                                                              ║"
echo "  ╠══════════════════════════════════════════════════════════════╣"
printf "  ║  %-60s║\n" "  ENV: ${ENV_TYPE}  |  LXD: ${LXD_METHOD}  |  Time: ${ELAPSED_MIN}m ${ELAPSED_SEC}s"
echo "  ╠══════════════════════════════════════════════════════════════╣"
printf "  ║  %-60s║\n" "  Public IP: ${PUBLIC_IP:-Not detected}  |  Interface: ${MAIN_IFACE:-auto}"
if [ "$BEHIND_NAT" = true ]; then
    printf "  ║  %-60s║\n" "  ⚠ Behind NAT — containers use port forwarding"
fi
echo "  ╠══════════════════════════════════════════════════════════════╣"
echo "  ║  Next Steps:                                                 ║"
echo "  ║    systemctl start MagnexHostSYS                            ║"
echo "  ║    systemctl enable MagnexHostSYS                           ║"
echo "  ╠══════════════════════════════════════════════════════════════╣"
echo "  ║  Helper Tools:                                               ║"
echo "  ║    magnex-status    live system status                      ║"
echo "  ║    fix-dns          repair DNS in all containers            ║"
echo "  ║    fix-network      reset iptables/NAT rules                ║"
echo "  ╠══════════════════════════════════════════════════════════════╣"
echo "  ║  Logs:                                                       ║"
echo "  ║    journalctl -u MagnexHostSYS -f                           ║"
echo "  ║    cat /var/log/magnexhost-install.log                      ║"
echo "  ╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

if [ ${#WARNINGS[@]} -gt 0 ]; then
    echo -e "  ${YELLOW}⚠  ${#WARNINGS[@]} warning(s) logged — review: cat ${LOG_FILE}${NC}"
    echo ""
fi

echo -e "  ${DIM}Full log: ${LOG_FILE}${NC}"
echo ""
