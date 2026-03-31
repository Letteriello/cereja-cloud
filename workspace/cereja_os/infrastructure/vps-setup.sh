#!/usr/bin/env bash
# ============================================================
# Cereja OS — VPS Initial Provisioning Script
# Run once on a fresh VPS (Ubuntu 22.04+) as root
# Usage: curl -fsSL https://your-cdn/vps-setup.sh | bash
# Or:    wget -qO- https://your-cdn/vps-setup.sh | bash
# ============================================================
set -euo pipefail

# ─── Configuration ────────────────────────────────────────
DOMAINS="${DOMAINS:-api.cereja.cloud,dashboard.cereja.cloud,cereja.cloud,telegram.cereja.cloud}"
EMAIL="${SSL_EMAIL:-admin@cereja.cloud}"
APP_DIR="${APP_DIR:-/opt/cereja-os}"
APP_USER="${APP_USER:-ubuntu}"
GIT_REPO="${GIT_REPO:-}"
BRANCH="${BRANCH:-main}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log()    { echo -e "${BLUE}[INFO]${NC} $1"; }
ok()     { echo -e "${GREEN}[OK]${NC} $1"; }
warn()   { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()  { echo -e "${RED}[ERROR]${NC} $1"; }

# ─── Check running as root ────────────────────────────────
if [ "$(id -u)" -ne 0 ]; then
    error "Run as root: sudo $0"
    exit 1
fi

# ─── Detect OS ─────────────────────────────────────────────
if ! command -v apt-get &> /dev/null; then
    error "This script requires Ubuntu/Debian (apt-get)"
    exit 1
fi

log "=========================================="
log "Cereja OS — VPS Provisioning"
log "=========================================="

# ─── 1. System Update ─────────────────────────────────────
log "1/9 — Updating system packages..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq curl wget git ufw certbot python3-certbot-nginx unattended-upgrades
ok "System packages installed"

# ─── 2. Docker & Docker Compose ────────────────────────────
log "2/9 — Installing Docker..."

if command -v docker &> /dev/null; then
    ok "Docker already installed: $(docker --version)"
else
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg

    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
        > /etc/apt/sources.list.d/docker.list

    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    systemctl enable docker
    ok "Docker installed: $(docker --version)"
fi

# ─── 3. Create App User ────────────────────────────────────
log "3/9 — Creating application user ($APP_USER)..."

if id "$APP_USER" &> /dev/null; then
    ok "User $APP_USER already exists"
else
    useradd -m -s /bin/bash -G docker,sudo "$APP_USER"
    ok "User $APP_USER created"
fi

# ─── 4. Create Directory Structure ─────────────────────────
log "4/9 — Creating directory structure..."

mkdir -p "$APP_DIR"/{data,logs,backups}
mkdir -p "$APP_DIR/infrastructure/docker/ssl"
mkdir -p "$APP_DIR/infrastructure/docker/nginx-logs"

chown -R "$APP_USER:$APP_USER" "$APP_DIR"
ok "Directory structure created at $APP_DIR"

# ─── 5. Clone / Pull Code ─────────────────────────────────
if [ -n "$GIT_REPO" ]; then
    log "5/9 — Cloning repository..."

    if [ -d "$APP_DIR/.git" ]; then
        log "Repository exists, pulling..."
        cd "$APP_DIR"
        sudo -u "$APP_USER" git pull
    else
        sudo -u "$APP_USER" git clone --branch "$BRANCH" "$GIT_REPO" "$APP_DIR"
    fi
    chown -R "$APP_USER:$APP_USER" "$APP_DIR"
    ok "Code updated"
else
    log "5/9 — Skipping git clone (GIT_REPO not set)"
fi

# ─── 6. UFW Firewall ───────────────────────────────────────
log "6/9 — Configuring UFW firewall..."

# Default policies
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (prevent lockout — check if using default port 22)
if ss -tlnp | grep -q ':22 '; then
    ufw allow OpenSSH
fi

# Allow HTTP/HTTPS
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'

# Enable UFW (--force skips confirmation)
echo "y" | ufw enable
systemctl enable ufw

ok "UFW firewall enabled (port 22, 80, 443 allowed)"

# ─── 7. SSL Certificates (Let's Encrypt) ───────────────────
log "7/9 — Generating SSL certificates..."

mkdir -p /var/www/html

# Generate certbot hook script
cat > /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh << 'EOF'
#!/bin/bash
# Reload nginx after certificate renewal
docker exec cereja-nginx nginx -s reload 2>/dev/null || true
EOF
chmod +x /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh

# First, start nginx temporarily for certbot to work
docker run -d --name nginx-temp \
    -p 80:80 \
    -p 443:443 \
    -v "$APP_DIR/infrastructure/docker/nginx.conf:/etc/nginx/conf.d/default.conf:ro" \
    -v /var/www/html:/usr/share/nginx/html:ro \
    nginx:alpine || true

# Wait for nginx to start
sleep 3

# Generate certificates for all domains
DOMAIN_LIST=$(echo "$DOMAINS" | tr ',' ' ')
certbot certonly \
    --nginx \
    --noninteractive \
    --agree-tos \
    --email "$EMAIL" \
    -d "$DOMAIN_LIST" \
    || warn "Certbot failed, will retry after nginx setup"

# Stop temp nginx
docker stop nginx-temp 2>/dev/null || true
docker rm nginx-temp 2>/dev/null || true

# Copy certs to app directory
CERT_DOMAIN=$(echo "$DOMAINS" | cut -d',' -f1)
if [ -d "/etc/letsencrypt/live/$CERT_DOMAIN" ]; then
    cp "/etc/letsencrypt/live/$CERT_DOMAIN/fullchain.pem" "$APP_DIR/infrastructure/docker/ssl/fullchain.pem"
    cp "/etc/letsencrypt/live/$CERT_DOMAIN/privkey.pem" "$APP_DIR/infrastructure/docker/ssl/privkey.pem"
    chmod 644 "$APP_DIR/infrastructure/docker/ssl/"*.pem
    ok "SSL certificates copied to $APP_DIR/infrastructure/docker/ssl/"
else
    warn "SSL certificates not found at /etc/letsencrypt/live/$CERT_DOMAIN"
fi

# ─── 8. Environment File ───────────────────────────────────
log "8/9 — Setting up environment file..."

ENV_FILE="$APP_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    if [ -f "$APP_DIR/infrastructure/env/.env.example" ]; then
        cp "$APP_DIR/infrastructure/env/.env.example" "$ENV_FILE"
        chown "$APP_USER:$APP_USER" "$ENV_FILE"
        warn "Environment file created at $ENV_FILE — EDIT IT with real values!"
    fi
else
    ok "Environment file already exists"
fi

# ─── 9. Start Stack ─────────────────────────────────────────
log "9/9 — Starting Cereja OS stack..."

if [ -f "$APP_DIR/infrastructure/docker/docker-compose.yml" ]; then
    cd "$APP_DIR"
    chown -R "$APP_USER:$APP_USER" "$APP_DIR"

    # Pull latest images
    sudo -u "$APP_USER" docker compose \
        -f "$APP_DIR/infrastructure/docker/docker-compose.yml" \
        pull || true

    # Start stack
    sudo -u "$APP_USER" docker compose \
        -f "$APP_DIR/infrastructure/docker/docker-compose.yml" \
        up -d

    ok "Stack started"
else
    warn "docker-compose.yml not found — skipping stack start"
fi

# ─── Post-Install Summary ──────────────────────────────────
log ""
log "=========================================="
ok "Cereja OS VPS provisioning complete!"
log "=========================================="
log ""
log "Next steps:"
log "  1. Edit: nano $ENV_FILE"
log "  2. Restart stack: cd $APP_DIR && docker compose -f infrastructure/docker/docker-compose.yml restart"
log "  3. Check health: curl https://api.cereja.cloud/health"
log "  4. Setup SSL auto-renewal: certbot renew --dry-run"
log ""
log "Services:"
log "  API:       https://api.cereja.cloud"
log "  Dashboard: https://dashboard.cereja.cloud"
log "  Telegram:  https://telegram.cereja.cloud"
log "=========================================="
