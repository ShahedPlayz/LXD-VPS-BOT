#!/usr/bin/env bash
set -e

BOT_SERVICE="sgm-bot"
INSTALL_DIR="/opt/sgm-bot"
NODE_MAJOR="24"
HIDDEN_DIR="${HOME:-/root}/.config/.sgm-bot"
DB_FILE="${HIDDEN_DIR}/.sgmbot.db.json"
BOT_BIN_DIR="${HIDDEN_DIR}/bin"
PATCHER="${HIDDEN_DIR}/sgm_patch.py"

GITHUB_OWNER="ShahedPlayz"
GITHUB_REPO="LXD-VPS-BOT"
GITHUB_BFDB="BF-DB"
BOT_FILE_NAME="ASP-VM-SGM.py"
RAW_BASE="https://raw.githubusercontent.com/${GITHUB_OWNER}/${GITHUB_REPO}/main/${GITHUB_BFDB}"
BOT_URL="${RAW_BASE}/${BOT_FILE_NAME}"

BOT_USER="${BOT_USER:-root}"
id "$BOT_USER" >/dev/null 2>&1 || BOT_USER="root"
[ -e /etc/os-release ] && . /etc/os-release

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[0;33m'; CYAN='\033[0;36m'; MAGENTA='\033[0;35m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'
UI_BORDER='\033[38;5;39m'; UI_ACCENT='\033[38;5;45m'; UI_ACCENT2='\033[38;5;213m'; UI_MUTED='\033[38;5;244m'; UI_TEXT='\033[1;97m'
log(){ echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" >&2; }
warn(){ echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" >&2; }
err(){ echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" >&2; }
info(){ echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" >&2; }

ui_cols(){
  local c="${COLUMNS:-}"
  if [ -z "$c" ] && [ -r /dev/tty ]; then c="$(tput cols </dev/tty 2>/dev/null || true)"; fi
  [ -z "$c" ] && c="$(tput cols 2>/dev/null || true)"
  case "$c" in ''|*[!0-9]*) c=80;; esac
  [ "$c" -gt 100 ] && c=100
  [ "$c" -lt 46 ] && c=46
  printf '%s' "$c"
}
ui_repeat(){
  local n="$1" ch="${2:-─}" s
  [ "$n" -lt 0 ] && n=0
  s="$(printf '%*s' "$n" '')"
  printf '%s' "${s// /$ch}"
}
ui_trim(){
  local val="$1" max="$2"
  if [ "${#val}" -le "$max" ]; then printf '%s' "$val"; else printf '%s…' "${val:0:$((max-1))}"; fi
}
ui_section(){
  local label="$1" w inner avail l r
  w="$(ui_cols)"; inner=$((w-2)); avail=$((inner-${#label}-2))
  [ "$avail" -lt 4 ] && avail=4
  l=$((avail/2)); r=$((avail-l))
  printf '\n  %b%s%b %s %b%s%b\n' "$UI_BORDER" "$(ui_repeat "$l")" "$UI_TEXT" "$label" "$UI_BORDER" "$(ui_repeat "$r")" "$NC" >&2
}
ui_field(){
  local num="$1" label="$2" cur="$3" hint="$4" w max
  w="$(ui_cols)"
  printf '\n  %b%s%b\n' "$UI_BORDER" "$(ui_repeat "$((w-2))")" "$NC" >&2
  printf '  %b[%s]%b %b%s%b' "$UI_ACCENT" "$num" "$NC" "$UI_TEXT" "$label" "$NC" >&2
  if [ -n "$cur" ]; then
    max=$((w-${#label}-14)); [ "$max" -lt 8 ] && max=8
    printf '  %b%s%b' "$UI_MUTED" "$(ui_trim "$cur" "$max")" "$NC" >&2
  fi
  printf '\n' >&2
  [ -n "$hint" ] && printf '  %b%s%b\n' "$UI_MUTED" "$hint" "$NC" >&2
  return 0
}
ui_kv(){
  local k="$1" v="$2" w max
  w="$(ui_cols)"; max=$((w-20)); [ "$max" -lt 10 ] && max=10
  printf '  %b%-16s%b %s\n' "$UI_MUTED" "$k" "$NC" "$(ui_trim "$v" "$max")" >&2
}

need_root(){ [[ $EUID -eq 0 ]] || { err "Please run as root: sudo bash $0"; exit 1; }; }

has_systemd(){
  [ "${SGM_FORCE_PM2:-0}" = "1" ] && return 1
  command -v systemctl >/dev/null 2>&1 || return 1
  [ -d /run/systemd/system ] || return 1
  systemctl show --property=Version >/dev/null 2>&1
}

detect_pkg(){
  local p; for p in apt-get dnf yum apk zypper pacman; do command -v "$p" >/dev/null 2>&1 && echo "$p" && return 0; done; return 1
}
PKG="$(detect_pkg || true)"

pkg_install(){
  case "$PKG" in
    apt-get) DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "$@" ;;
    dnf) dnf install -y "$@" ;;
    yum) yum install -y "$@" ;;
    apk) apk add --no-cache "$@" ;;
    zypper) zypper --non-interactive install -y "$@" ;;
    pacman) pacman -Sy --noconfirm "$@" ;;
    *) return 1 ;;
  esac
}

fetch_stdout(){ if command -v curl >/dev/null 2>&1; then curl -fsSL "$1"; else wget -qO- "$1"; fi; }
fetch_file(){ local url="$1" out="$2"; mkdir -p "$(dirname "$out")"; if command -v curl >/dev/null 2>&1; then curl -fsSL "$url" -o "$out"; else wget -qO "$out" "$url"; fi; }

write_patcher(){
  cat > "$PATCHER" << 'PYEOF'
#!/usr/bin/env python3
import json, os, re, sys
CFG_START = re.compile(r'^#\s*=+\s*BOT CONFIGURATION\s*=+\s*$', re.M)
CFG_END = re.compile(r'^#\s*=+\s*BOT CONFIGURATION END\s*=+\s*$', re.M)
INV_START = re.compile(r'^#\s*=+\s*INVITE/BOOST TRACKING EVENTS\s*=+\s*$', re.M)
INV_END = re.compile(r'^#\s*=+\s*INVITE/BOOST TRACKING EVENTS END\s*=+\s*$', re.M)
def find_region(src,start_pat,end_pat):
    m=start_pat.search(src)
    if not m:return None
    m2=end_pat.search(src,m.end())
    if not m2:return None
    return (m.end(),m2.start())
def strip_leading_ws(src,idx):
    ls=src.rfind('\n',0,idx)+1
    if src[ls:idx].strip()=='': return ls
    return idx
def remove_call(src,call,start,end):
    pos=start
    while True:
        idx=src.find(call,pos,end)
        if idx==-1:return src
        p=src.find('(',idx,end)
        if p==-1: pos=idx+len(call); continue
        i=p+1; depth=1; quote=None
        while i<end and depth>0:
            ch=src[i]
            if quote:
                if ch=='\\': i+=2; continue
                if ch==quote: quote=None
            else:
                if ch in ('"',"'",): quote=ch
                elif ch=='(': depth+=1
                elif ch==')': depth-=1
            i+=1
        j=src.find('\n',i)
        if j==-1: j=len(src)
        begin=strip_leading_ws(src,idx)
        end=end-(j+1-begin)
        src=src[:begin]+(src[j+1:] if j<len(src) else '')
        pos=begin
def sanitize(src):
    notes=[]
    new_src,n=re.subn(r'(?m)^[ \t]*YOUR_SERVER_IP[ \t]*=.*\n?','',src)
    if n: notes.append('removed YOUR_SERVER_IP'); src=new_src
    reg=find_region(src,INV_START,INV_END)
    if reg:
        start,end=reg; before=src[start:end]
        seg=remove_call(src,'await send_log(',start,end)
        removed=before.count('await send_log(')-seg[start:end].count('await send_log(')
        if removed: notes.append('moved %d invite/boost log call(s) to tracking only'%removed)
        src=seg
    else: notes.append('WARN: invite/boost section not found')
    return src,notes
def py_str(v): return "'"+str(v).replace('\\','\\\\').replace("'", "\\'")+"'"
def build_lines(cfg):
    admins=cfg.get('MAIN_ADMIN_IDS') or []
    if isinstance(admins,str): admins=[a.strip() for a in admins.split(',') if a.strip()]
    lines=[]
    lines.append(('DISCORD_TOKEN',"DISCORD_TOKEN = %s  # Your bot token here"%py_str(cfg.get('DISCORD_TOKEN',''))))
    lines.append(('BOT_NAME',"BOT_NAME = %s  # Bot name"%py_str(cfg.get('BOT_NAME',''))))
    lines.append(('PREFIX',"PREFIX = %s  # Command prefix"%py_str(cfg.get('PREFIX','.'))))
    ab="MAIN_ADMIN_IDS = [ #===== MAIN ADMINS ======\n"
    for a in admins: ab+="                  %s\n"%py_str(a)
    ab+="                 ]"
    lines.append(('MAIN_ADMIN_IDS',ab))
    thumb=str(cfg.get('THUMBNAIL_URL','') or '').strip()
    if thumb.lower() in ('0','none','off','false','disable','disabled'): thumb=''
    lines.append(('THUMBNAIL_URL',"THUMBNAIL_URL = %s # Thumbnail URL (empty disables)"%py_str(thumb)))
    lines.append(('LOGGIN_CHANNEL',"LOGGIN_CHANNEL = %s # Channel ID for logging important actions (suspensions, deletions, etc.)"%cfg.get('LOGGIN_CHANNEL',0)))
    lines.append(('TRACKING_CHANNEL',"TRACKING_CHANNEL = %s # Channel ID for tracking invite/boost activity"%cfg.get('TRACKING_CHANNEL',0)))
    return lines
def apply_config(src,cfg):
    notes=[]
    reg=find_region(src,CFG_START,CFG_END)
    if not reg: notes.append('WARN: bot configuration section not found'); return src,notes
    start,end=reg; body=src[start:end]
    for key,repl in build_lines(cfg):
        if key=='MAIN_ADMIN_IDS': pattern=r'(?ms)^MAIN_ADMIN_IDS[ \t]*=[ \t]*\[.*?\]'
        else: pattern=r'(?m)^%s[ \t]*=[^\n]*$'%re.escape(key)
        body,n=re.subn(pattern,lambda m,r=repl:r,body,count=1)
        if not n: body=body.rstrip('\n')+'\n'+repl+'\n'; notes.append('added missing %s'%key)
    src=src[:start]+body+src[end:]; return src,notes
GUARD_START='# >>> SGM THUMBNAIL GUARD >>>'
GUARD_END='# <<< SGM THUMBNAIL GUARD <<<'
GUARD_BLOCK = GUARD_START + """
try:
    import discord as _sgm_discord
    def _sgm_url_ok(u):
        v=str(u or '').strip().lower()
        return bool(v) and v not in ('0','none','off','false') and v.startswith(('http://','https://'))
    if not getattr(_sgm_discord.Embed, '_sgm_guarded', False):
        _sgm_orig_footer = _sgm_discord.Embed.set_footer
        _sgm_orig_thumb = _sgm_discord.Embed.set_thumbnail
        def _sgm_safe_footer(self, *args, **kwargs):
            if not _sgm_url_ok(kwargs.get('icon_url')): kwargs['icon_url'] = None
            return _sgm_orig_footer(self, *args, **kwargs)
        def _sgm_safe_thumbnail(self, *args, **kwargs):
            if not _sgm_url_ok(kwargs.get('url')): return self
            return _sgm_orig_thumb(self, *args, **kwargs)
        _sgm_discord.Embed.set_footer = _sgm_safe_footer
        _sgm_discord.Embed.set_thumbnail = _sgm_safe_thumbnail
        _sgm_discord.Embed._sgm_guarded = True
except Exception:
    pass
""" + GUARD_END + '\n'
def inject_guard(src):
    if GUARD_START in src: return src,[]
    m=CFG_END.search(src)
    if not m: return src,['WARN: config end marker not found; thumbnail guard skipped']
    j=src.find('\n',m.end())
    insert=len(src) if j==-1 else j+1
    return src[:insert]+GUARD_BLOCK+src[insert:],['installed thumbnail guard']
def main():
    args=sys.argv[1:]
    if len(args)<1: print('usage',file=sys.stderr); return 2
    target=args[0]; cfg_path=None; sanitize_only=False; i=1
    while i<len(args):
        if args[i]=='--config' and i+1<len(args): cfg_path=args[i+1]; i+=2
        elif args[i]=='--sanitize-only': sanitize_only=True; i+=1
        else: i+=1
    with open(target,'r',encoding='utf-8') as fh: src=fh.read()
    src,notes=sanitize(src)
    if cfg_path and not sanitize_only:
        with open(cfg_path,'r',encoding='utf-8') as fh: cfg=json.load(fh)
        src,n2=apply_config(src,cfg); notes.extend(n2)
        src,n3=inject_guard(src); notes.extend(n3)
    tmp=target+'.patch.tmp'
    with open(tmp,'w',encoding='utf-8') as fh: fh.write(src)
    try: os.chmod(tmp,os.stat(target).st_mode&0o7777 or 0o644)
    except: pass
    os.replace(tmp,target)
    for n in notes: print('patch: '+n)
if __name__=='__main__': sys.exit(main())
PYEOF
  chmod +x "$PATCHER" 2>/dev/null || true
}

ensure_hidden(){ mkdir -p "$HIDDEN_DIR" "$BOT_BIN_DIR"; chmod 700 "$HIDDEN_DIR" "$BOT_BIN_DIR" 2>/dev/null || true; write_patcher; }
load_db(){ if [ -f "$DB_FILE" ]; then cat "$DB_FILE"; else echo '{"installed":false,"bot_file":"","bot_source":"","config":{}}'; fi; }
save_db(){ local json="$1"; mkdir -p "$(dirname "$DB_FILE")"; umask 077; printf '%s' "$json" > "$DB_FILE"; chmod 600 "$DB_FILE" 2>/dev/null || true; }

json_get(){
  local key="$1" db; db="$(load_db)"
  python3 - "$db" "$key" << 'PY'
import sys,json
d=json.loads(sys.argv[1]); k=sys.argv[2]; cur=d
for part in k.split('.'):
    if isinstance(cur,dict): cur=cur.get(part)
    else: cur=None; break
if isinstance(cur,(dict,list)): print(json.dumps(cur))
elif cur is None: print("")
else:
    s=str(cur)
    if len(s)>=2 and s[0]=='"' and s[-1]=='"':
        try: s=json.loads(s)
        except: pass
    print(s)
PY
}

json_set(){
  local key="$1" value="$2" db tmp; db="$(load_db)"; tmp="$(mktemp)"
  python3 - "$db" "$key" "$value" "$tmp" << 'PY'
import sys,json
d=json.loads(sys.argv[1]); k=sys.argv[2]; v=sys.argv[3]; out=sys.argv[4]
try:
    if v.strip().startswith('{') or v.strip().startswith('['): vv=json.loads(v)
    elif v.strip()=='true': vv=True
    elif v.strip()=='false': vv=False
    elif v.strip()=='null': vv=None
    elif v.strip().lstrip('-').isdigit(): vv=int(v)
    else:
        try:
            if '.' in v.strip() and v.strip().replace('.','').replace('-','').isdigit(): vv=float(v)
            else: vv=v
        except: vv=v
except: vv=v
cur=d; parts=k.split('.')
for p in parts[:-1]:
    if p not in cur or not isinstance(cur.get(p),dict): cur[p]={}
    cur=cur[p]
cur[parts[-1]]=vv
with open(out,'w') as f: json.dump(d,f)
PY
  save_db "$(cat "$tmp")"; rm -f "$tmp"
}

spin(){
  local pid=$1 msg=$2 chars='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏' i=0
  while kill -0 "$pid" 2>/dev/null; do
    printf "\r%b%s%b %s" "$CYAN" "${chars:$i:1}" "$NC" "$msg"; i=$(( (i+1)%${#chars} )); sleep 0.08
  done
  printf "\r%b✔%b %s\n" "$GREEN" "$NC" "$msg"
}

progress_wait(){
  local label="$1" pid="$2" pct=0 i=0 rc=0 chars='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
  while kill -0 "$pid" 2>/dev/null; do
    [ "$pct" -lt 99 ] && pct=$((pct+1))
    printf "\r%b%s%b %s [%3d%%]" "$CYAN" "${chars:$i:1}" "$NC" "$label" "$pct"
    i=$(( (i+1)%${#chars} )); sleep 0.25
  done
  wait "$pid" 2>/dev/null || rc=$?
  printf "\r%b✔%b %s [100%%]\033[K\n" "$GREEN" "$NC" "$label"
  return $rc
}

download_progress(){
  local url="$1" out="$2" label="${3:-Downloading}" total="" cur pct pid i=0
  mkdir -p "$(dirname "$out")"
  if command -v curl >/dev/null 2>&1; then
    total="$(curl -fsSLI "$url" 2>/dev/null | tr -d '\r' | awk 'tolower($1)=="content-length:"{v=$2} END{if(v)print v}')"
    curl -fsSL "$url" -o "$out" &
  else
    wget -qO "$out" "$url" &
  fi
  pid=$!
  while kill -0 "$pid" 2>/dev/null; do
    cur="$(stat -c%s "$out" 2>/dev/null || echo 0)"
    if [ -n "$total" ] && [ "$total" -gt 0 ] 2>/dev/null; then
      pct=$(( cur * 100 / total )); [ "$pct" -gt 100 ] && pct=100
      printf "\r%b↓%b %s [%3d%%] %d/%d KB\033[K" "$CYAN" "$NC" "$label" "$pct" $((cur/1024)) $((total/1024))
    else
      printf "\r%b↓%b %s [%d KB]\033[K" "$CYAN" "$NC" "$label" $((cur/1024))
    fi
    sleep 0.1
  done
  wait "$pid" 2>/dev/null || true
  [ ! -s "$out" ] && { printf "\n"; return 1; }
  printf "\r%b✔%b %s [100%%]\033[K\n" "$GREEN" "$NC" "$label"
}

ensure_bot_file(){
  local force="${1:-0}" cached; cached="$BOT_BIN_DIR/$BOT_FILE_NAME"
  [ "$force" = "1" ] || { [ -s "$cached" ] && { json_set bot_source "$cached"; json_set bot_file "$BOT_FILE_NAME"; return 0; }; }
  mkdir -p "$BOT_BIN_DIR"
  info "Downloading: $BOT_FILE_NAME"
  download_progress "$BOT_URL" "$cached" "Downloading from GitHub..." || { err "Download failed."; return 1; }
  python3 "$PATCHER" "$cached" --sanitize-only >/dev/null 2>&1 || true
  json_set bot_source "$cached"; json_set bot_file "$BOT_FILE_NAME"
  log "Bot source ready: $cached"
}

install_deps(){
  log "Installing dependencies..."
  if [ -n "$PKG" ]; then
    case "$PKG" in
      apt-get) (apt-get update -qq >/dev/null 2>&1 || true) & progress_wait "Updating package lists" $! ;;
    esac
    (pkg_install python3 git curl ca-certificates nano >/dev/null 2>&1 || true) & progress_wait "Installing system packages" $!
    (pkg_install python3-pip python3-venv >/dev/null 2>&1 || pkg_install py3-pip >/dev/null 2>&1 || true) & progress_wait "Installing pip" $!
  fi
  local py; py="$(command -v python3 || command -v python || true)"; [ -n "$py" ] || { err "python3 not found"; exit 1; }
  ("$py" -m pip install -q --break-system-packages discord.py aiohttp requests python-dotenv 2>/dev/null \
    || "$py" -m pip install -q discord.py aiohttp requests python-dotenv 2>/dev/null \
    || "$py" -m pip install -q --user discord.py aiohttp requests python-dotenv 2>/dev/null || true) & progress_wait "Installing Python packages" $!
}

ensure_node(){
  local cur; cur="$( (node -v 2>/dev/null | sed 's/^v//;s/\..*//') || echo 0 )"; [ "${cur:-0}" -ge "$NODE_MAJOR" ] 2>/dev/null && return 0
  log "Installing Node.js ${NODE_MAJOR}..."
  case "$PKG" in
    apt-get) fetch_stdout "https://deb.nodesource.com/setup_${NODE_MAJOR}.x" 2>/dev/null | bash - >/dev/null 2>&1 || true; pkg_install nodejs >/dev/null 2>&1 || true ;;
    dnf|yum) fetch_stdout "https://rpm.nodesource.com/setup_${NODE_MAJOR}.x" 2>/dev/null | bash - >/dev/null 2>&1 || true; pkg_install nodejs >/dev/null 2>&1 || true ;;
    *) pkg_install nodejs npm >/dev/null 2>&1 || true ;;
  esac
  cur="$( (node -v 2>/dev/null | sed 's/^v//;s/\..*//') || echo 0 )"; [ "${cur:-0}" -ge "$NODE_MAJOR" ] 2>/dev/null && return 0
  local arch narch base ver tmp url; arch="$(uname -m)"; case "$arch" in x86_64|amd64)narch=x64;; aarch64|arm64)narch=arm64;; armv7l|armhf)narch=armv7l;; *)narch=x64;; esac
  base="https://nodejs.org/dist/latest-v${NODE_MAJOR}.x"; ver="$(fetch_stdout "$base/" 2>/dev/null | grep -oE "node-v${NODE_MAJOR}\.[0-9]+\.[0-9]+" | head -n1 || true)"; [ -n "$ver" ] || return 1
  url="$base/$ver-linux-$narch.tar.xz"; tmp="$(mktemp -d)"; fetch_file "$url" "$tmp/node.tar.xz"; mkdir -p /usr/local/lib/nodejs; tar -xJf "$tmp/node.tar.xz" -C /usr/local/lib/nodejs
  ln -sf "/usr/local/lib/nodejs/$ver-linux-$narch/bin/node" /usr/local/bin/node 2>/dev/null || true
  ln -sf "/usr/local/lib/nodejs/$ver-linux-$narch/bin/npm" /usr/local/bin/npm 2>/dev/null || true
  rm -rf "$tmp"
}
ensure_pm2(){ command -v pm2 >/dev/null 2>&1 && return 0; npm install -g pm2 >/dev/null 2>&1 || return 1; local gbin; gbin="$(npm prefix -g 2>/dev/null)/bin"; case ":$PATH:" in *":$gbin:"*) ;; *) export PATH="$gbin:$PATH" ;; esac; }

clean_token(){
  local t="$1"
  t="${t//$'\r'/}"; t="${t//$'\n'/}"
  t="${t#"${t%%[![:space:]]*}"}"; t="${t%"${t##*[![:space:]]}"}"
  if [ "${#t}" -ge 2 ]; then
    case "$t" in \"*\") t="${t:1:${#t}-2}" ;; esac
    case "$t" in \'*\') t="${t:1:${#t}-2}" ;; esac
  fi
  case "$t" in "Bot "*) t="${t#Bot }" ;; esac
  printf '%s' "$t"
}

prompt_config(){
  local mode="$1" oldcfg token botname prefix thumb logch track admins ans
  oldcfg="$(json_get config)"
  if [ "$mode" = "edit" ]; then
    token="$(echo "$oldcfg" | python3 -c "import sys,json;d=json.loads(sys.stdin.read());print(d.get('DISCORD_TOKEN',''))" 2>/dev/null || true)"
    botname="$(echo "$oldcfg" | python3 -c "import sys,json;d=json.loads(sys.stdin.read());print(d.get('BOT_NAME',''))" 2>/dev/null || true)"
    prefix="$(echo "$oldcfg" | python3 -c "import sys,json;d=json.loads(sys.stdin.read());print(d.get('PREFIX','.'))" 2>/dev/null || true)"
    thumb="$(echo "$oldcfg" | python3 -c "import sys,json;d=json.loads(sys.stdin.read());print(d.get('THUMBNAIL_URL',''))" 2>/dev/null || true)"
    logch="$(echo "$oldcfg" | python3 -c "import sys,json;d=json.loads(sys.stdin.read());print(d.get('LOGGIN_CHANNEL','0'))" 2>/dev/null || true)"
    track="$(echo "$oldcfg" | python3 -c "import sys,json;d=json.loads(sys.stdin.read());print(d.get('TRACKING_CHANNEL','0'))" 2>/dev/null || true)"
    admins="$(echo "$oldcfg" | python3 -c "import sys,json;d=json.loads(sys.stdin.read());a=d.get('MAIN_ADMIN_IDS',[]);print(', '.join(a) if isinstance(a,list) else a)" 2>/dev/null || true)"
  else
    token=""; botname=""; prefix="."; thumb=""; logch="0"; track="0"; admins=""
  fi

  ui_section "SGM BOT CONFIGURATION · ${mode^^}"

  while true; do
    ui_field "1/7" "DISCORD TOKEN" "" "Ctrl+U clears the prefilled value · Enter keeps it"
    read -r -e -i "$token" -p "  ❯ DISCORD_TOKEN: " ntoken||ntoken=""
    ntoken="$(clean_token "$ntoken")"; [ -z "$ntoken" ]&&ntoken="$token"
    [ -z "$ntoken" ]&&{ warn "Token cannot be empty."; continue; }
    token="$ntoken"; break
  done

  while true; do
    ui_field "2/7" "BOT NAME" "${botname:-<unset>}" "Shown in messages and bot presence"
    read -r -e -i "$botname" -p "  ❯ BOT_NAME: " nbot||nbot=""
    [ -z "$nbot" ]&&nbot="$botname"
    [ -z "$nbot" ]&&{ warn "Cannot be empty."; continue; }
    botname="$nbot"; break
  done

  while true; do
    ui_field "3/7" "COMMAND PREFIX" "${prefix:-.}" "Prefix used for text commands"
    read -r -e -i "$prefix" -p "  ❯ PREFIX: " np||np=""
    [ -z "$np" ]&&np="$prefix"; [ -z "$np" ]&&np="."
    prefix="$np"; break
  done

  while true; do
    ui_field "4/7" "MAIN ADMIN IDs" "${admins:-<unset>}" "Comma separated Discord user IDs"
    read -r -e -i "$admins" -p "  ❯ MAIN_ADMIN_IDS: " nadmins||nadmins=""
    [ -z "$nadmins" ]&&nadmins="$admins"
    [ -z "$nadmins" ]&&{ warn "At least one admin ID is required."; continue; }
    admins="$nadmins"; break
  done

  while true; do
    ui_field "5/7" "THUMBNAIL URL" "${thumb:-<disabled>}" "http(s) image URL · enter 0 to disable"
    read -r -e -i "$thumb" -p "  ❯ THUMBNAIL_URL: " nthumb||nthumb=""
    [ -z "$nthumb" ]&&nthumb="$thumb"
    case "${nthumb,,}" in
      0|none|off|false|disable|disabled) thumb="0"; break;;
    esac
    [ -z "$nthumb" ]&&{ thumb="0"; break; }
    if [[ ! "$nthumb" =~ ^https?://[^[:space:]]+\.[^[:space:]]+ ]]; then
      warn "Enter a valid http(s) URL, or 0 to disable."; continue
    fi
    thumb="$nthumb"; break
  done

  while true; do
    ui_field "6/7" "LOGGING CHANNEL ID" "${logch:-0}" "Numeric channel ID (0 disables)"
    read -r -e -i "$logch" -p "  ❯ LOGGIN_CHANNEL: " nlog||nlog=""
    [ -z "$nlog" ]&&nlog="$logch"
    [[ ! "$nlog" =~ ^[0-9]+$ ]]&&{ warn "Numbers only."; continue; }
    logch="$nlog"; break
  done

  while true; do
    ui_field "7/7" "TRACKING CHANNEL ID" "${track:-0}" "Numeric channel ID (0 disables)"
    read -r -e -i "$track" -p "  ❯ TRACKING_CHANNEL: " ntrack||ntrack=""
    [ -z "$ntrack" ]&&ntrack="$track"
    [[ ! "$ntrack" =~ ^[0-9]+$ ]]&&{ warn "Numbers only."; continue; }
    track="$ntrack"; break
  done

  local admins_json; admins_json="$(python3 - "$admins" << 'PYJSON'
import sys,json
s=sys.argv[1]; items=[]
for p in s.split(','):
    p=p.strip()
    if p: items.append(p)
print(json.dumps(items))
PYJSON
)"

  ui_section "REVIEW CONFIGURATION"
  ui_kv "DISCORD TOKEN" "••••••••  (${#token} characters)"
  ui_kv "BOT NAME" "$botname"
  ui_kv "PREFIX" "$prefix"
  ui_kv "MAIN ADMINS" "$admins"
  if [ "$thumb" = "0" ]; then ui_kv "THUMBNAIL" "disabled (0)"; else ui_kv "THUMBNAIL" "$thumb"; fi
  ui_kv "LOGGING CHANNEL" "$logch"
  ui_kv "TRACKING CHANNEL" "$track"
  printf '  %b%s%b\n' "$UI_BORDER" "$(ui_repeat "$(( $(ui_cols) - 2 ))")" "$NC" >&2
  read -r -p "  Apply this configuration? [Y/n]: " ans||ans=""
  case "$ans" in n|N) echo -e "${YELLOW}  Cancelled. Returning to menu...${NC}" >&2; return 1;; esac
  local cfgjson; cfgjson="$(python3 - "$token" "$botname" "$prefix" "$thumb" "$logch" "$track" "$admins_json" << 'PY'
import sys,json
d={"DISCORD_TOKEN":sys.argv[1],"BOT_NAME":sys.argv[2],"PREFIX":sys.argv[3],"THUMBNAIL_URL":sys.argv[4],"LOGGIN_CHANNEL":sys.argv[5],"TRACKING_CHANNEL":sys.argv[6],"MAIN_ADMIN_IDS":json.loads(sys.argv[7])}
print(json.dumps(d))
PY
)"
  json_set config "$cfgjson"; echo "$cfgjson"
}

stop_bot(){
  if has_systemd && systemctl list-unit-files 2>/dev/null | grep -q "^${BOT_SERVICE}\.service"; then
    systemctl stop ${BOT_SERVICE} >/dev/null 2>&1 || true
    systemctl disable ${BOT_SERVICE} >/dev/null 2>&1 || true
    rm -f /etc/systemd/system/${BOT_SERVICE}.service 2>/dev/null || true
    systemctl daemon-reload >/dev/null 2>&1 || true
  fi
  if command -v pm2 >/dev/null 2>&1; then pm2 delete "$BOT_SERVICE" >/dev/null 2>&1 || true; pm2 save >/dev/null 2>&1 || true; fi
}

cleanup_all(){
  echo -e "${YELLOW}This will cleanup ALL files, configs, database and bot service. No history left.${NC}"
  read -r -p "Are you sure? (y/n): " ans||ans=""; case "$ans" in y|Y) ;; *) echo "Cancelled."; return 0;; esac
  stop_bot
  rm -rf "$INSTALL_DIR" 2>/dev/null || true
  rm -rf "$HIDDEN_DIR" 2>/dev/null || true
  rm -rf /root/.cache/sgm-bot 2>/dev/null || true
  rm -rf /home/*/.cache/sgm-bot 2>/dev/null || true
  log "Cleanup complete."
  sleep 2
  show_menu
}

token_check(){
  python3 - "$1" << 'PY'
import sys,json,urllib.request,urllib.error
t=sys.argv[1].strip()
if not t:
    print("token is empty"); sys.exit(1)
req=urllib.request.Request("https://discord.com/api/v10/users/@me",headers={"Authorization":"Bot "+t,"User-Agent":"SGM-Bot-Installer"})
try:
    with urllib.request.urlopen(req,timeout=15) as r: d=json.load(r)
    print("logged in as %s"%(d.get("username") or d.get("id")))
    sys.exit(0)
except urllib.error.HTTPError as e:
    if e.code==401: print("Discord rejected the token (401 Unauthorized)")
    elif e.code==429: print("Discord rate limit (429), try again shortly")
    else: print("Discord API returned HTTP %s"%e.code)
    sys.exit(1)
except Exception as e:
    print("could not reach Discord: %s"%e)
    sys.exit(2)
PY
}

extract_bot_token(){
  python3 - "$1" << 'PY'
import re,sys
try: src=open(sys.argv[1],encoding='utf-8').read()
except Exception: sys.exit(0)
m=re.search(r'''^DISCORD_TOKEN[ \t]*=[ \t]*(['"])(.*?)\1''',src,re.M|re.S)
print(m.group(2) if m else "")
PY
}

verify_token_in_file(){
  local got; got="$(extract_bot_token "$1")"
  [ -n "$got" ] && [ "$got" = "$2" ]
}

sync_runtime_settings(){
  local db="$INSTALL_DIR/vps.db"
  [ -f "$db" ] || return 0
  printf '%s' "$1" | python3 -c '
import json,sqlite3,sys
cfg=json.load(sys.stdin)
con=sqlite3.connect(sys.argv[1],timeout=10)
pairs=(("bot_activity_name",str(cfg.get("BOT_NAME",""))+" VPS Manager"),("prefix",str(cfg.get("PREFIX","."))))
for k,v in pairs:
    cur=con.execute("UPDATE settings SET value=? WHERE key=?",(v,k))
    if cur.rowcount==0:
        con.execute("INSERT INTO settings(key,value) VALUES(?,?)",(k,v))
con.commit(); con.close()
' "$db" 2>/dev/null || warn "Could not sync runtime settings (vps.db)."
}

do_install(){
  local inst src; inst="$(json_get installed)"; src="$(json_get bot_source)"
  if [ "$inst" = "true" ] || ([ -n "$src" ] && [ -f "$src" ] && (systemctl list-unit-files 2>/dev/null | grep -q "^${BOT_SERVICE}\.service" || (command -v pm2 >/dev/null 2>&1 && pm2 describe "$BOT_SERVICE" >/dev/null 2>&1))); then
    warn "Bot appears installed/running or found in database."; read -r -p "Do you want to reinstall/update? (y/n): " ans||ans=""; case "$ans" in y|Y) ;; *) show_menu; return 0;; esac
  fi
  ensure_hidden; ensure_bot_file 1 || return 1; src="$(json_get bot_source)"
  install_deps
  local cfg; cfg="$(prompt_config install)" || { show_menu; return 0; }
  local token vmsg vrc=0
  token="$(printf '%s' "$cfg" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("DISCORD_TOKEN",""))' 2>/dev/null || true)"
  vmsg="$(token_check "$token")" || vrc=$?
  if [ "$vrc" -eq 1 ]; then
    err "Token verification failed: $vmsg"
    read -r -p "Save this token anyway? (y/n): " ans || ans=""
    case "$ans" in y|Y) warn "Saving unverified token; the bot will not stay online." ;; *) warn "Nothing was changed. Fix the token with option 2 (Edit BOT) or reinstall."; sleep 3; show_menu; return 1 ;; esac
  elif [ "$vrc" -eq 2 ]; then
    warn "Token not verified: $vmsg"
  else
    log "Token verified: $vmsg"
  fi
  mkdir -p "$INSTALL_DIR"; chown -R "$BOT_USER:$BOT_USER" "$INSTALL_DIR" 2>/dev/null || true
  local stage="$INSTALL_DIR/ASP-VM-SGM.py.new" pout
  cp "$src" "$stage"
  chmod +x "$stage" 2>/dev/null || true
  pout="$(python3 "$PATCHER" "$stage" --config <(echo "$cfg") 2>&1)" || true
  if ! verify_token_in_file "$stage" "$token"; then
    err "Config patch failed: token was not written to the bot file."
    [ -n "$pout" ] && printf '%s\n' "$pout" | tail -n 8
    rm -f "$stage"
    warn "Try option 3 (CleanUP) then option 1 (Install) again."
    sleep 3; show_menu; return 1
  fi
  chown "$BOT_USER:$BOT_USER" "$stage" 2>/dev/null || true
  mv -f "$stage" "$INSTALL_DIR/ASP-VM-SGM.py"
  log "Config written to bot file."
  sync_runtime_settings "$cfg"
  stop_bot
  local py; py="$(command -v python3 || command -v python)"
  if has_systemd; then
    cat > /etc/systemd/system/${BOT_SERVICE}.service <<EOF
[Unit]
Description=SGM Discord Bot (ASP-VM-SGM)
After=network.target
StartLimitIntervalSec=60
StartLimitBurst=5

[Service]
User=${BOT_USER}
Group=${BOT_USER}
WorkingDirectory=${INSTALL_DIR}
Environment=PYTHONUNBUFFERED=1
ExecStart=${py} ${INSTALL_DIR}/ASP-VM-SGM.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload
    systemctl enable ${BOT_SERVICE} >/dev/null 2>&1 || true
    systemctl reset-failed ${BOT_SERVICE} >/dev/null 2>&1 || true
    systemctl restart ${BOT_SERVICE}
    sleep 3
    if systemctl is-active --quiet ${BOT_SERVICE}; then
      log "Bot is online (systemd)."
    else
      err "Bot failed to start (systemd). Recent logs:"
      journalctl -u ${BOT_SERVICE} -n 12 --no-pager 2>/dev/null | tail -n 12 || true
    fi
  else
    ensure_node; ensure_pm2 || { err "PM2 failed"; return 1; }
    pm2 delete "$BOT_SERVICE" >/dev/null 2>&1 || true
    pm2 start "$INSTALL_DIR/ASP-VM-SGM.py" --name "$BOT_SERVICE" --cwd "$INSTALL_DIR" --interpreter "$py" >/dev/null 2>&1 || true
    pm2 save >/dev/null 2>&1 || true
    sleep 3
    local ppid; ppid="$(pm2 pid "$BOT_SERVICE" 2>/dev/null | tail -n1)"
    if [[ "$ppid" =~ ^[0-9]+$ ]] && [ "$ppid" -gt 0 ]; then
      log "Bot is online (pm2, PID $ppid)."
    else
      err "Bot failed to start (pm2). Recent logs:"
      pm2 logs "$BOT_SERVICE" --lines 12 --nostream 2>/dev/null || true
    fi
  fi
  json_set installed "true"; log "Installation complete."
  printf "  %bReturning to main menu in 3s...%b\n" "$UI_MUTED" "$NC"
  sleep 3
  show_menu
}

do_edit(){
  ensure_hidden; ensure_bot_file || return 1
  local src cfg; src="$(json_get bot_source)"; cfg="$(prompt_config edit)" || { show_menu; return 0; }
  local token vmsg vrc=0
  token="$(printf '%s' "$cfg" | python3 -c 'import sys,json;print(json.load(sys.stdin).get("DISCORD_TOKEN",""))' 2>/dev/null || true)"
  vmsg="$(token_check "$token")" || vrc=$?
  if [ "$vrc" -eq 1 ]; then
    err "Token verification failed: $vmsg"
    read -r -p "Save this token anyway? (y/n): " ans || ans=""
    case "$ans" in y|Y) warn "Saving unverified token; the bot will not stay online." ;; *) warn "Config was not applied. Please enter a valid bot token."; sleep 3; show_menu; return 1 ;; esac
  elif [ "$vrc" -eq 2 ]; then
    warn "Token not verified: $vmsg"
  else
    log "Token verified: $vmsg"
  fi
  mkdir -p "$INSTALL_DIR"
  local stage="$INSTALL_DIR/ASP-VM-SGM.py.new" pout
  cp "$src" "$stage"; chmod +x "$stage" 2>/dev/null || true
  pout="$(python3 "$PATCHER" "$stage" --config <(echo "$cfg") 2>&1)" || true
  if ! verify_token_in_file "$stage" "$token"; then
    err "Config patch failed: token was not written to the bot file."
    [ -n "$pout" ] && printf '%s\n' "$pout" | tail -n 8
    rm -f "$stage"
    warn "Config was not applied."
    sleep 3; show_menu; return 1
  fi
  chown "$BOT_USER:$BOT_USER" "$stage" 2>/dev/null || true
  mv -f "$stage" "$INSTALL_DIR/ASP-VM-SGM.py"
  log "Config written to bot file."
  sync_runtime_settings "$cfg"
  if has_systemd && systemctl list-unit-files 2>/dev/null | grep -q "^${BOT_SERVICE}\.service"; then
    systemctl reset-failed ${BOT_SERVICE} >/dev/null 2>&1 || true
    systemctl restart ${BOT_SERVICE}; sleep 3
    if systemctl is-active --quiet ${BOT_SERVICE}; then log "Bot restarted and online."; else err "Bot failed to start."; journalctl -u ${BOT_SERVICE} -n 12 --no-pager 2>/dev/null | tail -n 12 || true; fi
  elif command -v pm2 >/dev/null 2>&1 && pm2 describe "$BOT_SERVICE" >/dev/null 2>&1; then
    pm2 restart "$BOT_SERVICE" >/dev/null 2>&1 || true; sleep 3
    local ppid; ppid="$(pm2 pid "$BOT_SERVICE" 2>/dev/null | tail -n1)"
    if [[ "$ppid" =~ ^[0-9]+$ ]] && [ "$ppid" -gt 0 ]; then log "Bot restarted and online (pm2)."; else err "Bot failed to start (pm2)."; pm2 logs "$BOT_SERVICE" --lines 12 --nostream 2>/dev/null || true; fi
  else warn "Bot not found as service. Clean up or install again."
  fi
  json_set installed "true"
  printf "  %bReturning to main menu in 3s...%b\n" "$UI_MUTED" "$NC"
  sleep 3; show_menu
}

do_mledit(){
  ensure_hidden; ensure_bot_file || return 1
  local src target; src="$(json_get bot_source)"
  if [ -f "$INSTALL_DIR/ASP-VM-SGM.py" ]; then target="$INSTALL_DIR/ASP-VM-SGM.py"; else target="$src"; fi
  [ -n "$target" ] && [ -f "$target" ] || { err "No bot file found. Install the bot first."; sleep 3; show_menu; return 1; }
  echo -e "${BOLD}Manual Edit (ML EDIT)${NC}"; echo -e "${DIM}Opening installed bot file $target in nano. Ctrl+O, Enter, Ctrl+X to save & exit.${NC}"
  command -v nano >/dev/null 2>&1 || pkg_install nano >/dev/null 2>&1 || { err "nano not found"; return 1; }
  nano "$target"
  read -r -p "Apply changes and restart bot? (y/n): " ans||ans=""; case "$ans" in y|Y) ;; *) echo "Cancelled."; show_menu; return 0;; esac
  mkdir -p "$INSTALL_DIR"
  if [ "$target" != "$INSTALL_DIR/ASP-VM-SGM.py" ]; then cp -f "$target" "$INSTALL_DIR/ASP-VM-SGM.py"; fi
  chmod +x "$INSTALL_DIR/ASP-VM-SGM.py" 2>/dev/null || true
  python3 "$PATCHER" "$INSTALL_DIR/ASP-VM-SGM.py" --sanitize-only >/dev/null 2>&1 || true
  if has_systemd && systemctl list-unit-files 2>/dev/null | grep -q "^${BOT_SERVICE}\.service"; then
    systemctl reset-failed ${BOT_SERVICE} >/dev/null 2>&1 || true
    systemctl restart ${BOT_SERVICE}; sleep 3
    if systemctl is-active --quiet ${BOT_SERVICE}; then log "Manual edit applied. Bot is online."; else err "Bot failed to start."; journalctl -u ${BOT_SERVICE} -n 12 --no-pager 2>/dev/null | tail -n 12 || true; fi
  elif command -v pm2 >/dev/null 2>&1 && pm2 describe "$BOT_SERVICE" >/dev/null 2>&1; then
    pm2 restart "$BOT_SERVICE" >/dev/null 2>&1 || true; sleep 3
    log "Manual edit applied (pm2)."
  else warn "Bot not found as service. Clean up or install again."
  fi
  printf "  %bReturning to main menu in 3s...%b\n" "$UI_MUTED" "$NC"
  sleep 3; show_menu
}

print_banner(){
  local c=(51 45 39 33 27 21) i
  local logo=(
'███████╗ ██████╗ ███╗   ███╗'
'██╔════╝██╔════╝ ████╗ ████║'
'███████╗██║  ███╗██╔████╔██║'
'╚════██║██║   ██║██║╚██╔╝██║'
'███████║╚██████╔╝██║ ╚═╝ ██║'
'╚══════╝ ╚═════╝ ╚═╝     ╚═╝'
  )
  echo
  for i in "${!logo[@]}"; do
    printf "  \033[38;5;%sm%s\033[0m\n" "${c[$i]}" "${logo[$i]}"
  done
  printf "  %bSGM BOT%b %b·%b %bINSTALLER & CONTROL PANEL%b\n\n" "$UI_TEXT" "$NC" "$UI_MUTED" "$NC" "$UI_MUTED" "$NC"
}

print_rule(){ printf "  %b─────────────────────────────────────────────────────────────%b\n" "$UI_BORDER" "$NC"; }

info_row(){
  local label="$1" value="${2:--}" color="${3:-$UI_TEXT}"
  printf "  %b▌%b %b%-14s%b %b%s%b\n" "$UI_ACCENT" "$NC" "$UI_MUTED" "$label" "$NC" "$color" "$value" "$NC"
}

fmt_dur(){
  local t="${1:-0}" out=""
  [ "$t" -lt 0 ] 2>/dev/null && t=0
  local d=$((t/86400)) h=$(((t%86400)/3600)) m=$(((t%3600)/60)) s=$((t%60))
  [ "$d" -gt 0 ] && out="${out}${d}d "
  [ "$h" -gt 0 ] && out="${out}${h}h "
  [ "$m" -gt 0 ] && out="${out}${m}m "
  out="${out}${s}s"
  echo "$out"
}

bot_state(){
  if has_systemd && systemctl list-unit-files 2>/dev/null | grep -q "^${BOT_SERVICE}\.service"; then
    if systemctl is-active --quiet "$BOT_SERVICE" 2>/dev/null; then echo "RUNNING"; else echo "STOPPED"; fi
    return 0
  fi
  if command -v pm2 >/dev/null 2>&1 && pm2 describe "$BOT_SERVICE" >/dev/null 2>&1; then
    local p; p="$(pm2 pid "$BOT_SERVICE" 2>/dev/null | tail -n1)"
    if [[ "$p" =~ ^[0-9]+$ ]] && [ "$p" -gt 0 ]; then echo "RUNNING"; else echo "STOPPED"; fi
    return 0
  fi
  echo "NOT INSTALLED"
}

pm2_metrics(){
  command -v pm2 >/dev/null 2>&1 || return 1
  pm2 jlist 2>/dev/null | python3 - "$BOT_SERVICE" << 'PY'
import sys,json,time
try: arr=json.load(sys.stdin)
except Exception: sys.exit(1)
name=sys.argv[1]
for it in arr:
    if it.get('name')==name:
        env=it.get('pm2_env') or {}
        mon=it.get('monit') or {}
        up=0
        if env.get('status')=='online' and env.get('pm_uptime'):
            up=max(0,int((time.time()*1000-float(env['pm_uptime']))/1000))
        print('%s\t%s\t%s\t%s\t%s\t%s'%(env.get('status',''),it.get('pid') or 0,mon.get('cpu') or 0,mon.get('memory') or 0,env.get('restart_time') or 0,up))
        sys.exit(0)
sys.exit(1)
PY
}

do_start(){
  local st; st="$(bot_state)"
  if [ "$st" = "RUNNING" ]; then warn "Bot is already running."; sleep 2; show_menu; return 0; fi
  if [ "$st" = "NOT INSTALLED" ]; then warn "Bot is not installed. Use option 1 (Install BOT) first."; sleep 3; show_menu; return 1; fi
  log "Starting bot..."
  if has_systemd && systemctl list-unit-files 2>/dev/null | grep -q "^${BOT_SERVICE}\.service"; then
    systemctl reset-failed "$BOT_SERVICE" >/dev/null 2>&1 || true
    systemctl start "$BOT_SERVICE" >/dev/null 2>&1 || true
    sleep 3
    if systemctl is-active --quiet "$BOT_SERVICE"; then log "Bot started (systemd)."; else err "Bot failed to start (systemd)."; journalctl -u "$BOT_SERVICE" -n 12 --no-pager 2>/dev/null | tail -n 12 || true; fi
  elif command -v pm2 >/dev/null 2>&1; then
    pm2 start "$BOT_SERVICE" >/dev/null 2>&1 || pm2 start "$INSTALL_DIR/ASP-VM-SGM.py" --name "$BOT_SERVICE" --cwd "$INSTALL_DIR" --interpreter "$(command -v python3 || command -v python)" >/dev/null 2>&1 || true
    pm2 save >/dev/null 2>&1 || true
    sleep 3
    local ppid; ppid="$(pm2 pid "$BOT_SERVICE" 2>/dev/null | tail -n1)"
    if [[ "$ppid" =~ ^[0-9]+$ ]] && [ "$ppid" -gt 0 ]; then log "Bot started (pm2, PID $ppid)."; else err "Bot failed to start (pm2)."; fi
  else err "No service manager found for this bot."
  fi
  sleep 2; show_menu
}

do_reboot(){
  local st; st="$(bot_state)"
  if [ "$st" != "RUNNING" ]; then warn "Bot is not running. Use option 6 (Start BOT) instead."; sleep 3; show_menu; return 1; fi
  log "Rebooting bot..."
  if has_systemd && systemctl list-unit-files 2>/dev/null | grep -q "^${BOT_SERVICE}\.service"; then
    systemctl reset-failed "$BOT_SERVICE" >/dev/null 2>&1 || true
    systemctl restart "$BOT_SERVICE" >/dev/null 2>&1 || true
    sleep 3
    if systemctl is-active --quiet "$BOT_SERVICE"; then log "Bot rebooted and online (systemd)."; else err "Bot failed to start after reboot."; journalctl -u "$BOT_SERVICE" -n 12 --no-pager 2>/dev/null | tail -n 12 || true; fi
  elif command -v pm2 >/dev/null 2>&1 && pm2 describe "$BOT_SERVICE" >/dev/null 2>&1; then
    pm2 restart "$BOT_SERVICE" >/dev/null 2>&1 || true
    pm2 save >/dev/null 2>&1 || true
    sleep 3
    local ppid; ppid="$(pm2 pid "$BOT_SERVICE" 2>/dev/null | tail -n1)"
    if [[ "$ppid" =~ ^[0-9]+$ ]] && [ "$ppid" -gt 0 ]; then log "Bot rebooted (pm2, PID $ppid)."; else err "Bot failed to start after reboot (pm2)."; fi
  else err "No service manager found for this bot."
  fi
  sleep 2; show_menu
}

do_shutdown(){
  local st; st="$(bot_state)"
  if [ "$st" != "RUNNING" ]; then warn "Bot is not running. Nothing to shut down."; sleep 3; show_menu; return 1; fi
  log "Shutting down bot..."
  if has_systemd && systemctl list-unit-files 2>/dev/null | grep -q "^${BOT_SERVICE}\.service"; then
    systemctl stop "$BOT_SERVICE" >/dev/null 2>&1 || true
    sleep 2
    if systemctl is-active --quiet "$BOT_SERVICE"; then err "Bot is still running."; else log "Bot shut down (systemd)."; fi
  elif command -v pm2 >/dev/null 2>&1 && pm2 describe "$BOT_SERVICE" >/dev/null 2>&1; then
    pm2 stop "$BOT_SERVICE" >/dev/null 2>&1 || true
    pm2 save >/dev/null 2>&1 || true
    sleep 2
    log "Bot shut down (pm2)."
  else err "No service manager found for this bot."
  fi
  sleep 2; show_menu
}

do_info(){
  clear 2>/dev/null || true
  print_banner
  printf "  %b▌%b %bBOT INFORMATION%b\n" "$UI_ACCENT2" "$NC" "$UI_TEXT" "$NC"
  print_rule

  local mode="-" state="NOT INSTALLED" sc="$YELLOW" enabled="-" pid="-" uptime="-" cpu="-" mem="-" restarts="-"
  local since secs uptime_sec=0

  if has_systemd && systemctl list-unit-files 2>/dev/null | grep -q "^${BOT_SERVICE}\.service"; then
    mode="systemd"
    state="$(systemctl is-active "$BOT_SERVICE" 2>/dev/null || true)"; [ -z "$state" ] && state="unknown"
    enabled="$(systemctl is-enabled "$BOT_SERVICE" 2>/dev/null || true)"; [ -z "$enabled" ] && enabled="-"
    pid="$(systemctl show -p MainPID --value "$BOT_SERVICE" 2>/dev/null || true)"
    { [ -z "$pid" ] || [ "$pid" = "0" ]; } && pid="-"
    restarts="$(systemctl show -p NRestarts --value "$BOT_SERVICE" 2>/dev/null || true)"; [ -z "$restarts" ] && restarts="-"
    if [ "$state" = "active" ]; then
      sc="$GREEN"
      since="$(systemctl show -p ActiveEnterTimestamp --value "$BOT_SERVICE" 2>/dev/null || true)"
      if [ -n "$since" ]; then
        secs="$(date -d "$since" +%s 2>/dev/null || echo 0)"
        if [ "$secs" -gt 0 ] 2>/dev/null; then
          uptime_sec=$(( $(date +%s) - secs ))
          [ "$uptime_sec" -ge 0 ] && uptime="$(fmt_dur "$uptime_sec")"
        fi
      fi
    else
      sc="$RED"
    fi
  elif command -v pm2 >/dev/null 2>&1 && pm2 describe "$BOT_SERVICE" >/dev/null 2>&1; then
    mode="pm2"
    local m; m="$(pm2_metrics || true)"
    if [ -n "$m" ]; then
      IFS=$'\t' read -r state pid cpu mem restarts uptime_sec <<< "$m"
      if [ "$state" = "online" ]; then state="RUNNING"; sc="$GREEN"; else state="STOPPED"; sc="$RED"; fi
      [ "$pid" = "0" ] && pid="-"
      [ "$mem" = "0" ] || mem="$(awk -v b="$mem" 'BEGIN{printf "%.1f MB", b/1048576}')"
      [ "$uptime_sec" -gt 0 ] 2>/dev/null && uptime="$(fmt_dur "$uptime_sec")"
    fi
    enabled="pm2"
  else
    local inst; inst="$(json_get installed)"
    if [ "$inst" = "true" ]; then state="INSTALLED (service missing)"; else state="NOT INSTALLED"; fi
  fi

  if [ -n "$pid" ] && [ "$pid" != "-" ]; then
    local pc pu
    pc="$(ps -o %cpu= -p "$pid" 2>/dev/null | tr -d ' ' || true)"; [ -n "$pc" ] && cpu="${pc}%"
    pu="$(ps -o rss= -p "$pid" 2>/dev/null | tr -d ' ' || true)"; [ -n "$pu" ] && mem="$(awk -v k="$pu" 'BEGIN{printf "%.1f MB", k/1024}')"
  fi

  local cfg bn px an ht file src installed lastmod
  cfg="$(json_get config)"
  IFS=$'\t' read -r bn px an ht <<< "$(python3 - "$cfg" << 'PY'
import sys,json
try: d=json.loads(sys.argv[1])
except Exception: d={}
a=d.get('MAIN_ADMIN_IDS') or []
n=len(a) if isinstance(a,list) else len([x for x in str(a).split(',') if x.strip()])
print('%s\t%s\t%s\t%s'%(d.get('BOT_NAME','') or '-',d.get('PREFIX','') or '.',n,'yes' if d.get('DISCORD_TOKEN') else 'no'))
PY
)"
  [ -z "$bn" ] && bn="-"; [ -z "$px" ] && px="."; [ -z "$an" ] && an="0"
  file="$(json_get bot_file)"; [ -z "$file" ] && file="$BOT_FILE_NAME"
  src="$(json_get bot_source)"
  installed="$(json_get installed)"; [ -z "$installed" ] && installed="no"
  lastmod="-"; [ -f "$INSTALL_DIR/ASP-VM-SGM.py" ] && lastmod="$(stat -c '%y' "$INSTALL_DIR/ASP-VM-SGM.py" 2>/dev/null | cut -d'.' -f1)"

  info_row "Status" "$state" "$sc"
  info_row "Service" "$mode"
  info_row "Enabled" "$enabled"
  info_row "PID" "$pid"
  info_row "Uptime" "$uptime" "$UI_ACCENT"
  info_row "CPU" "$cpu"
  info_row "Memory" "$mem"
  info_row "Restarts" "$restarts"
  print_rule
  info_row "Bot Name" "$bn"
  info_row "Prefix" "$px"
  info_row "Admins" "$an"
  info_row "Token" "$( [ "$ht" = "yes" ] && echo 'configured (hidden)' || echo 'missing' )"
  info_row "Source" "$file"
  info_row "Cached" "${src:--}"
  info_row "Installed" "$installed"
  info_row "Last Update" "$lastmod"
  print_rule
  echo
  printf "  %b❯%b Press Enter to return to menu..." "$UI_ACCENT" "$NC"
  read -r _ || true
  show_menu
}

show_menu(){
  clear 2>/dev/null || true
  print_banner
  local st sc can_start can_stop
  st="$(bot_state)"
  case "$st" in RUNNING) sc="$GREEN";; STOPPED) sc="$RED";; *) sc="$YELLOW";; esac
  can_start=0; can_stop=0
  if [ "$st" = "RUNNING" ]; then can_stop=1; elif [ "$st" = "STOPPED" ]; then can_start=1; fi
  printf "  %b╭────────────────────────────────────────────────────────────╮%b\n" "$UI_BORDER" "$NC"
  printf "  %b│%b  %bSGM CONTROL PANEL%b\n" "$UI_BORDER" "$NC" "$UI_TEXT" "$NC"
  printf "  %b│%b  %bStatus%b   %b● %s%b\n" "$UI_BORDER" "$NC" "$UI_MUTED" "$NC" "$sc" "$st" "$NC"
  printf "  %b╰────────────────────────────────────────────────────────────╯%b\n\n" "$UI_BORDER" "$NC"
  printf "  %b[1]%b  %bInstall BOT%b        %bDeploy or update the bot%b\n" "$GREEN" "$NC" "$UI_TEXT" "$NC" "$UI_MUTED" "$NC"
  printf "  %b[2]%b  %bEdit BOT%b           %bEdit config and restart%b\n" "$CYAN" "$NC" "$UI_TEXT" "$NC" "$UI_MUTED" "$NC"
  printf "  %b[3]%b  %bCleanUP BOT%b        %bRemove service, files and config%b\n" "$RED" "$NC" "$UI_TEXT" "$NC" "$UI_MUTED" "$NC"
  printf "  %b[4]%b  %bML EDIT%b            %bManually edit the bot source%b\n" "$MAGENTA" "$NC" "$UI_TEXT" "$NC" "$UI_MUTED" "$NC"
  printf "  %b[5]%b  %bINFO%b               %bService status and details%b\n" "$UI_ACCENT" "$NC" "$UI_TEXT" "$NC" "$UI_MUTED" "$NC"
  if [ "$can_start" = "1" ]; then
    printf "  %b[6]%b  %bStart BOT%b          %bStart the stopped bot%b\n" "$GREEN" "$NC" "$UI_TEXT" "$NC" "$UI_MUTED" "$NC"
  else
    printf "  %b[6]%b  %bStart BOT%b          %bUnavailable - bot is %s%b\n" "$UI_MUTED" "$NC" "$UI_MUTED" "$NC" "$UI_MUTED" "$( [ "$st" = "RUNNING" ] && echo running || echo 'not installed' )" "$NC"
  fi
  if [ "$can_stop" = "1" ]; then
    printf "  %b[7]%b  %bReboot BOT%b         %bRestart the running bot%b\n" "$YELLOW" "$NC" "$UI_TEXT" "$NC" "$UI_MUTED" "$NC"
    printf "  %b[8]%b  %bShutdown BOT%b       %bStop the running bot%b\n" "$RED" "$NC" "$UI_TEXT" "$NC" "$UI_MUTED" "$NC"
  else
    printf "  %b[7]%b  %bReboot BOT%b         %bUnavailable - bot is not running%b\n" "$UI_MUTED" "$NC" "$UI_MUTED" "$NC" "$UI_MUTED" "$NC"
    printf "  %b[8]%b  %bShutdown BOT%b       %bUnavailable - bot is not running%b\n" "$UI_MUTED" "$NC" "$UI_MUTED" "$NC" "$UI_MUTED" "$NC"
  fi
  printf "  %b[0]%b  %bExit%b\n\n" "$UI_MUTED" "$NC" "$UI_TEXT" "$NC"
  printf "  %b❯%b Select option %b[0-8]%b: " "$UI_ACCENT" "$NC" "$UI_MUTED" "$NC"
  local opt; read -r opt || opt=""
  echo
  case "$opt" in
    1) do_install ;;
    2) do_edit ;;
    3) cleanup_all ;;
    4) do_mledit ;;
    5) do_info ;;
    6) do_start ;;
    7) do_reboot ;;
    8) do_shutdown ;;
    0|q|Q) log "Goodbye."; exit 0 ;;
    *) warn "Invalid option"; sleep 2; show_menu ;;
  esac
}

main(){ need_root; ensure_hidden; show_menu; }
main "$@"
