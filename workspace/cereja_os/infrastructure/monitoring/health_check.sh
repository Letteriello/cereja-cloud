#!/usr/bin/env bash
# ============================================================
# Cereja OS — Health Check Script
# Run via cron or container HEALTHCHECK
# Usage: ./health_check.sh [API_URL] [DASHBOARD_URL]
# ============================================================
set -euo pipefail

API_URL="${1:-http://localhost:8000}"
DASHBOARD_URL="${2:-http://localhost:80}"
REDIS_HOST="${REDIS_HOST:-redis}"
LOG_FILE="${LOG_FILE:-/app/logs/healthcheck.log}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_api() {
    local url="$1/health"
    local http_code
    local response
    
    log "Checking API at $url..."
    
    http_code=$(curl -sf -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$http_code" = "200" ]; then
        log -e "${GREEN}[OK]${NC} API health check passed (HTTP $http_code)"
        return 0
    else
        log -e "${RED}[FAIL]${NC} API health check failed (HTTP $http_code)"
        return 1
    fi
}

check_dashboard() {
    local url="$1"
    local http_code
    
    log "Checking Dashboard at $url..."
    
    http_code=$(curl -sf -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$http_code" = "200" ]; then
        log -e "${GREEN}[OK]${NC} Dashboard check passed (HTTP $http_code)"
        return 0
    else
        log -e "${YELLOW}[WARN]${NC} Dashboard check returned (HTTP $http_code)"
        return 0  # Dashboard failure is not critical
    fi
}

check_redis() {
    local host="$1"
    
    log "Checking Redis at $host..."
    
    if command -v redis-cli &> /dev/null; then
        local pong
        pong=$(redis-cli -h "$host" ping 2>/dev/null || echo "FAIL")
        
        if [ "$pong" = "PONG" ]; then
            log -e "${GREEN}[OK]${NC} Redis is responding"
            return 0
        else
            log -e "${RED}[FAIL]${NC} Redis is not responding (got: $pong)"
            return 1
        fi
    else
        log -e "${YELLOW}[WARN]${NC} redis-cli not found, skipping Redis check"
        return 0
    fi
}

check_api_v1() {
    local url="$1/api/v1/health"
    local http_code
    
    log "Checking API v1 at $url..."
    
    http_code=$(curl -sf -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$http_code" = "200" ]; then
        log -e "${GREEN}[OK]${NC} API v1 health check passed"
        return 0
    else
        log -e "${RED}[FAIL]${NC} API v1 health check failed (HTTP $http_code)"
        return 1
    fi
}

# ─── Main ───────────────────────────────────────────────────
main() {
    log "=========================================="
    log "Cereja OS Health Check starting..."
    log "=========================================="
    
    local failed=0
    
    check_api "$API_URL" || ((failed++))
    check_api_v1 "$API_URL" || ((failed++))
    check_dashboard "$DASHBOARD_URL" || ((failed++))
    check_redis "$REDIS_HOST" || ((failed++))
    
    log "=========================================="
    if [ $failed -eq 0 ]; then
        log -e "${GREEN}All health checks passed!${NC}"
        log "=========================================="
        exit 0
    else
        log -e "${RED}$failed health check(s) failed!${NC}"
        log "=========================================="
        exit 1
    fi
}

main "$@"
