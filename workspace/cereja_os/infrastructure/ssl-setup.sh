#!/usr/bin/env bash
# ============================================================
# Cereja OS — SSL Certificate Setup
# Run after VPS is provisioned and DNS is pointing
# Usage: ./ssl-setup.sh [email] [domains...]
# Example: ./ssl-setup.sh admin@cereja.cloud api.cereja.cloud dashboard.cereja.cloud cereja.cloud telegram.cereja.cloud
# ============================================================
set -euo pipefail

EMAIL="${1:-${SSL_EMAIL:-admin@cereja.cloud}}"
DOMAINS="${*:2}"
APP_DIR="${APP_DIR:-/opt/cereja-os}"
CERT_DIR="$APP_DIR/infrastructure/docker/ssl"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()   { echo -e "${GREEN}[SSL]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Default domains if none provided
if [ -z "$DOMAINS" ]; then
    DOMAINS="api.cereja.cloud dashboard.cereja.cloud cereja.cloud telegram.cereja.cloud"
fi

log "SSL Certificate Setup"
log "Email: $EMAIL"
log "Domains: $DOMAINS"

mkdir -p "$CERT_DIR"

# Check if port 80 is available
if ! ss -tlnp | grep -q ':80 '; then
    warn "Port 80 not in use — starting temporary nginx for certbot..."
    # Start temporary nginx for ACME challenge
    docker run -d --name certbot-temp \
        --cap-net-bind-service=true \
        -p 80:80 \
        -p 443:443 \
        -v "$APP_DIR/infrastructure/docker/nginx.conf:/etc/nginx/conf.d/default.conf:ro" \
        -v /var/www/html:/usr/share/nginx/html:ro \
        nginx:alpine || true
    sleep 3
fi

# Generate certificates
DOMAIN_LIST=$(echo "$DOMAINS" | tr ' ' ',')
log "Requesting certificate for: $DOMAIN_LIST"

certbot certonly \
    --nginx \
    --noninteractive \
    --agree-tos \
    --email "$EMAIL" \
    -d "$DOMAIN_LIST"

# Copy certificates
PRIMARY_DOMAIN=$(echo "$DOMAINS" | awk '{print $1}')
CERT_PATH="/etc/letsencrypt/live/$PRIMARY_DOMAIN"

if [ -d "$CERT_PATH" ]; then
    cp "$CERT_PATH/fullchain.pem" "$CERT_DIR/fullchain.pem"
    cp "$CERT_PATH/privkey.pem" "$CERT_DIR/privkey.pem"
    chmod 644 "$CERT_DIR/"*.pem
    log "Certificates installed at $CERT_DIR"
else
    warn "Certificate path not found: $CERT_PATH"
    exit 1
fi

# Restart nginx
docker restart cereja-nginx 2>/dev/null || docker compose -f "$APP_DIR/infrastructure/docker/docker-compose.yml" restart nginx

log "SSL setup complete!"
log "Test renewal: certbot renew --dry-run"
