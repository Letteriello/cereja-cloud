#!/usr/bin/env bash
# ============================================================
# Cereja OS — SSL Certificate Renewal
# Run via cron: 0 0 * * * /opt/cereja-os/infrastructure/monitoring/ssl-renew.sh
# ============================================================
set -euo pipefail

# Configuration
DOMAINS="${DOMAINS:-api.cereja.cloud,dashboard.cereja.cloud,cereja.cloud}"
EMAIL="${SSL_EMAIL:-admin@cereja.cloud}"
CERT_DIR="${CERT_DIR:-/opt/cereja-os/infrastructure/docker/ssl}"
WEBROOT="${WEBROOT:-/tmp/letsencrypt}"
STAGING="${STAGING:-0}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S')] $1"
}

log_success() {
    log -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    log -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    log -e "${RED}[ERROR]${NC} $1"
}

# ─── Check Certificate Expiry ───────────────────────────────
check_expiry() {
    local domain="$1"
    local expiry
    local days_left
    
    # Use openssl to check certificate
    expiry=$(echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null \
        | openssl x509 -noout -dates 2>/dev/null \
        | grep notAfter \
        | cut -d= -f2)
    
    if [ -z "$expiry" ]; then
        log_error "Could not check certificate for $domain"
        return 1
    fi
    
    local expiry_epoch
    expiry_epoch=$(date -d "$expiry" +%s 2>/dev/null || date -j -f "%b %d %H:%M:%S %Y" "$expiry" +%s 2>/dev/null)
    local now_epoch
    now_epoch=$(date +%s)
    days_left=$(( (expiry_epoch - now_epoch) / 86400 ))
    
    log "Certificate for $domain expires: $expiry ($days_left days)"
    
    if [ "$days_left" -lt 30 ]; then
        return 0  # Should renew
    else
        return 1  # No renewal needed
    fi
}

# ─── Renew Certificate ─────────────────────────────────────
renew_cert() {
    local domain="$1"
    
    log "Renewing certificate for $domain..."
    
    if [ "$STAGING" = "1" ]; then
        certbot certonly --webroot -w "$WEBROOT" -d "$domain" \
            --email "$EMAIL" --agree-tos --noninteractive --staging
    else
        certbot certonly --webroot -w "$WEBROOT" -d "$domain" \
            --email "$EMAIL" --agree-tos --noninteractive
    fi
    
    # Copy to ssl directory
    local live_dir="/etc/letsencrypt/live/$domain"
    if [ -d "$live_dir" ]; then
        mkdir -p "$CERT_DIR"
        cp "$live_dir/fullchain.pem" "$CERT_DIR/fullchain.pem"
        cp "$live_dir/privkey.pem" "$CERT_DIR/privkey.pem"
        log_success "Certificates copied to $CERT_DIR"
    else
        log_error "Certificate directory not found: $live_dir"
        return 1
    fi
}

# ─── Reload Nginx ─────────────────────────────────────────
reload_nginx() {
    log "Reloading nginx..."
    
    if command -v docker &> /dev/null; then
        docker exec cereja-nginx nginx -s reload 2>/dev/null \
            || docker restart cereja-nginx
        log_success "Nginx reloaded"
    else
        nginx -s reload
        log_success "Nginx reloaded (native)"
    fi
}

# ─── Main ─────────────────────────────────────────────────
main() {
    log "=========================================="
    log "Cereja OS SSL Certificate Renewal Check"
    log "=========================================="
    
    local needs_renewal=0
    
    # Check each domain
    for domain in $(echo "$DOMAINS" | tr ',' ' '); do
        if check_expiry "$domain"; then
            needs_renewal=1
        fi
    done
    
    if [ "$needs_renewal" = "1" ]; then
        log_warn "Certificate(s) need renewal"
        
        for domain in $(echo "$DOMAINS" | tr ',' ' '); do
            if ! renew_cert "$domain"; then
                log_error "Failed to renew $domain"
            fi
        done
        
        reload_nginx
        log_success "SSL renewal process completed"
    else
        log_success "All certificates are valid (>30 days)"
    fi
    
    log "=========================================="
}

main "$@"
