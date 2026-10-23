# 🚀 LXD-VPS-BOT

A powerful Discord-based VPS management platform built around LXD/LXC containers, made by SGM.

LXD-VPS-BOT allows communities, hosting providers, and VPS services to create, manage, monitor, and automate VPS deployments directly from Discord — without requiring a traditional web panel.

The bot uses a remote **SGM Node API** to manage containers across multiple servers.

---

## ✨ Features

### 🖥️ VPS Management

- Create and deploy LXD containers
- Start, stop, restart, and delete VPS
- Reinstall VPS with different OS templates
- Resize CPU, RAM, and disk resources
- Manage bandwidth limits
- Freeze and unfreeze containers
- View VPS information, statistics, and logs

### 🌐 Networking

- Create and remove port forwards
- Manage user port allocations
- IPv4 tunnel support
- File Manager tunnel support
- SSHX / TMATE console access
- Multi-node network management

### 🗂️ Node Management

- Connect multiple remote nodes
- Monitor node health and resources
- View node information and status
- Automatically route VPS operations to the correct node
- Restart and remove nodes

### 👥 User Management

- VPS ownership tracking
- Shared VPS access
- Revoke shared permissions
- User resource monitoring
- Invite and boost statistics

### 🎁 Reward System

- Invite-based VPS claiming
- Boost-based VPS claiming
- Free VPS plans
- Automatic resource allocation
- Invite and boost tracking logs

### 🛡️ Administrative Tools

- Main Admin and Admin permissions
- VPS suspension and unsuspension
- VPS renewal with timers
- VPS whitelist protection
- Purge protection
- Maintenance mode
- Bulk VPS start and stop controls
- Detailed activity logs

### 📊 Monitoring

- Live node and container statistics
- Resource usage tracking
- Container health checks
- Host system information
- Disk usage monitoring
- Full-disk alerts
- Automatic expiry checks

### ⚡ Automation

- Automatic VPS provisioning
- Expired VPS suspension
- Automatic deletion after a grace period
- Resource validation before deployment
- Automatic Discord emoji management
- Service management through the installer

---

The Discord bot acts as the control panel, while remote node hosts handle container operations through the SGM Node API.

---

## 🔧 Installation

### Requirements

- Linux server or VPS for the bot
- Root access for installation
- Python 3

### 1. Bot Installer

```bash
sudo bash -c 'tmp=$(mktemp /tmp/.sgm-installer.XXXXXX.sh); trap "rm -f \"$tmp\"" EXIT INT TERM; curl -fsSL https://raw.githubusercontent.com/ShahedPlayz/LXD-VPS-BOT/main/bot-installer.sh | tr -d "\r" > "$tmp"; bash "$tmp"'
```

### 2. Node Installer

```bash
coming soon
```

---

## 💡 Use Cases

- Free/Paid VPS communities
- VPS hosting providers
- Discord-based hosting services
- Multi-node container infrastructure
- Internal development environments
- Educational Linux labs
- Community reward systems

---

## 🔐 Security

- Never share your Discord bot token or node API keys.
- Restrict administrative permissions to trusted users.
- Use HTTPS for remote node APIs.
- Configure firewall rules to restrict API access.
- Keep your bot and node software updated.

---

## 🌟 Why LXD-VPS-BOT?

Instead of relying on a traditional web panel, LXD-VPS-BOT lets you manage your VPS infrastructure directly from Discord.

Provisioning, monitoring, networking, renewals, suspensions, rewards, and multi-node management are accessible through Discord commands and interactive menus.

Whether you're running a free VPS community or managing multiple container hosts, LXD-VPS-BOT provides a centralized way to manage your infrastructure.
