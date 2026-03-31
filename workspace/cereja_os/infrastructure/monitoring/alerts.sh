#!/usr/bin/env bash
# ============================================================
# Cereja OS — Alerting Script
# Send alerts on service failures
# ============================================================
set -euo pipefail

# Configuration
ALERT_WEBHOOK_URL="${ALERT_WEBHOOK_URL:-}"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"
ALERT_COOLDOWN=300  # seconds between repeated alerts

# Alert levels
LEVEL_INFO="info"
LEVEL_WARN="warn"
LEVEL_ERROR="error"
LEVEL_CRITICAL="critical"

# ─── Logging ───────────────────────────────────────────────
log() {
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S')] [ALERT] $1" >> /app/logs/alerts.log
}

# ─── Send Telegram Alert ───────────────────────────────────
send_telegram() {
    local message="$1"
    local level="$2"
    
    if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
        log "Telegram not configured, skipping"
        return 1
    fi
    
    local emoji
    case "$level" in
        critical) emoji="🚨" ;;
        error) emoji="❌" ;;
        warn) emoji="⚠️" ;;
        info) emoji="ℹ️" ;;
        *) emoji="📢" ;;
    esac
    
    local text="$emoji Cereja OS Alert ($level)%0A%0A$message"
    
    curl -sf -X POST \
        "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d "chat_id=$TELEGRAM_CHAT_ID" \
        -d "text=$text" \
        -d "parse_mode=HTML" \
        >> /app/logs/alerts.log 2>&1 || log "Telegram send failed"
}

# ─── Send Webhook Alert ────────────────────────────────────
send_webhook() {
    local message="$1"
    local level="$2"
    
    if [ -z "$ALERT_WEBHOOK_URL" ]; then
        log "Webhook not configured, skipping"
        return 1
    fi
    
    local payload
    payload=$(cat <<EOF
{
    "alert": "cereja-os",
    "level": "$level",
    "message": "$message",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "hostname": "$(hostname)"
}
EOF
)
    
    curl -sf -X POST "$ALERT_WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        >> /app/logs/alerts.log 2>&1 || log "Webhook send failed"
}

# ─── Main Alert Function ───────────────────────────────────
alert() {
    local level="$1"
    local message="$2"
    
    log "[$level] $message"
    send_telegram "$message" "$level"
    send_webhook "$message" "$level"
}

# ─── Check Cooldown ────────────────────────────────────────
should_alert() {
    local alert_name="$1"
    local cooldown_file="/tmp/alert_cooldown_$alert_name"
    
    if [ -f "$cooldown_file" ]; then
        local last_alert
        last_alert=$(cat "$cooldown_file")
        local now
        now=$(date +%s)
        local elapsed=$((now - last_alert))
        
        if [ $elapsed -lt $ALERT_COOLDOWN ]; then
            log "Alert $alert_name suppressed (cooldown: ${elapsed}s remaining)"
            return 1
        fi
    fi
    
    echo "$(date +%s)" > "$cooldown_file"
    return 0
}

# ─── Predefined Alerts ────────────────────────────────────
alert_service_down() {
    local service="$1"
    if should_alert "service_down_$service"; then
        alert "$LEVEL_ERROR" "Service DOWN: $service on $(hostname)"
    fi
}

alert_service_recovered() {
    local service="$1"
    if should_alert "service_recovered_$service"; then
        alert "$LEVEL_INFO" "Service RECOVERED: $service on $(hostname)"
    fi
}

alert_disk_space() {
    local usage="$1"
    if should_alert "disk_space"; then
        alert "$LEVEL_WARN" "Disk space usage: $usage% on $(hostname)"
    fi
}

alert_ssl_expiring() {
    local days="$1"
    if should_alert "ssl_expiring"; then
        alert "$LEVEL_WARN" "SSL certificate expires in $days days"
    fi
}

# ─── CLI Usage ────────────────────────────────────────────
if [ $# -ge 2 ]; then
    case "$1" in
        service-down)
            alert_service_down "$2"
            ;;
        service-recovered)
            alert_service_recovered "$2"
            ;;
        disk-space)
            alert_disk_space "$2"
            ;;
        ssl-expiring)
            alert_ssl_expiring "$2"
            ;;
        *)
            alert "$1" "$2"
            ;;
    esac
fi
