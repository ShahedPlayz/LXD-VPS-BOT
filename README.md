# 🚀 LXD-VPS-BOT

A powerful Discord-based VPS management platform built around LXD/LXC containers, Made by SGM.

LXD-VPS-BOT allows communities, hosting providers, and VPS services to create, manage, monitor, and automate VPS deployments directly from Discord without requiring users to access the host machine.

---

## ✨ Features

### 🖥️ VPS Management

* Create and deploy LXD containers
* Manage VPS directly from Discord
* Restart, suspend, and delete VPS
* Resize CPU, RAM, and Disk resources
* View detailed VPS information
* Live VPS statistics monitoring

### 📦 Backup System

* Create snapshots
* Restore backups instantly
* Clone existing VPS
* Disaster recovery support

### 🌐 Port Forwarding

* Create port forwards
* Remove port forwards
* Manage user port allocations
* Dedicated port management system

### 👥 User Management

* VPS ownership tracking
* Shared VPS access
* Revoke shared permissions
* User resource monitoring

### 🎁 Reward System

* Invite-based VPS claiming
* Boost-based VPS claiming
* Automatic resource allocation
* User statistics tracking

### 🛡️ Administrative Tools

* Multi-level permission system
* VPS suspension system
* VPS whitelist protection
* Maintenance mode
* VPS purge protection
* Detailed activity logs

### 📊 Monitoring

* Live machine statistics
* Resource usage tracking
* Container health monitoring
* Host system information
* Threshold alert system

### ⚡ Automation

* Automatic VPS provisioning
* Automated renewals
* Resource validation
* Permission management
* Service management

---

## 🔧 Installation

1. Upload `bot.py` to your VPS.

2. Open the configuration section inside `bot.py`.

3. Configure all required variables

4. Run the installer:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/ShahedPlayz/LXD-VPS-BOT/main/install.sh | tr -d '\r')
```

The installer automatically installs all required dependencies and prepares the environment.

5. Start the service:

```bash
systemctl restart MagnexHostSYS
```

6. Verify the bot is online in Discord.

---

## 💡 Use Cases

* Free VPS communities
* Hosting providers
* Discord-based VPS services
* Internal development environments
* Educational Linux labs
* Community reward systems

---

## 🛠️ Technology Stack

* Python
* Discord.py
* LXD / LXC
* Systemd
* Linux Server Infrastructure

---

## ⚠️ Requirements

* Linux VPS or Dedicated Server
* Root Access
* Discord Bot Application

---

## 🌟 Why LXD-VPS-BOT?

Instead of using a traditional web panel, everything can be managed directly from Discord.

Provisioning, monitoring, backups, renewals, suspensions, and resource management are all handled through Discord commands and interactive menus.

This makes VPS management simple, accessible, and community-friendly while maintaining production-ready container infrastructure.
