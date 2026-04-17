#!/usr/bin/env bash
# Prepare a fresh Ubuntu server (Contabo or any VPS) for the sreality scraper.
#
# Run as root on the NEW server:
#   curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/master/scripts/setup_server.sh | bash
# or after cloning:
#   bash scripts/setup_server.sh

set -euo pipefail

echo "================================================================"
echo "  sreality-scraper — new server setup"
echo "================================================================"

# --- 1. System packages ---------------------------------------------------

echo "[setup] Updating system packages..."
apt-get update -qq
apt-get upgrade -y -qq

echo "[setup] Installing base utilities..."
apt-get install -y -qq \
    git \
    curl \
    htop \
    ufw \
    fail2ban \
    ca-certificates \
    gnupg \
    lsb-release

# --- 2. Docker (official script, not snap) --------------------------------

if command -v docker &>/dev/null; then
    echo "[setup] Docker already installed: $(docker --version)"
else
    echo "[setup] Installing Docker via official script..."
    curl -fsSL https://get.docker.com | sh
    echo "[setup] Docker installed: $(docker --version)"
fi

# Add the invoking user (or $SUDO_USER if run via sudo) to the docker group
REAL_USER="${SUDO_USER:-$USER}"
if [ "$REAL_USER" != "root" ]; then
    usermod -aG docker "$REAL_USER"
    echo "[setup] Added $REAL_USER to docker group (re-login or run 'newgrp docker' to activate)"
fi

# --- 3. UFW firewall ------------------------------------------------------

echo "[setup] Configuring UFW firewall..."
ufw allow 22/tcp    comment "SSH"
ufw allow 80/tcp    comment "HTTP (portal)"
ufw allow 443/tcp   comment "HTTPS (portal)"

# Enable non-interactively
echo "y" | ufw enable
ufw status verbose

# --- 4. fail2ban (SSH brute-force protection) -----------------------------

echo "[setup] Configuring fail2ban..."
systemctl enable fail2ban
systemctl start fail2ban

# Basic jail override — ban after 5 failures for 10 minutes
cat > /etc/fail2ban/jail.d/sreality.conf <<'EOF'
[sshd]
enabled  = true
port     = ssh
maxretry = 5
bantime  = 600
findtime = 600
EOF

systemctl reload fail2ban
echo "[setup] fail2ban active. Check with: fail2ban-client status sshd"

# --- 5. Create app directory ----------------------------------------------

echo "[setup] Creating /opt/sreality directory..."
mkdir -p /opt/sreality/backups
mkdir -p /opt/sreality/logs

if [ "$REAL_USER" != "root" ]; then
    chown -R "$REAL_USER:$REAL_USER" /opt/sreality
fi

# --- 6. Smoke test --------------------------------------------------------

echo "[setup] Running Docker hello-world smoke test..."
docker run --rm hello-world

# --- Summary --------------------------------------------------------------

SERVER_IP="$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')"

echo ""
echo "================================================================"
echo "  Setup complete!"
echo "================================================================"
echo ""
echo "  Server IP   : $SERVER_IP"
echo "  Docker      : $(docker --version)"
echo "  App dir     : /opt/sreality"
echo ""
echo "  Next steps:"
echo "    1. Clone repo:  cd /opt/sreality && git clone <REPO_URL> ."
echo "    2. Create .env: cp .env.example .env && nano .env"
echo "    3. Deploy:      bash scripts/deploy.sh"
echo ""
echo "  Then restore backup — see docs/migration.md Phase 3."
echo ""
