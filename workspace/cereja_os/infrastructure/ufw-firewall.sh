#!/usr/bin/env bash
# ============================================================
# Cereja OS — UFW Firewall Configuration
# Run as root on a fresh VPS
# ============================================================
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

ok()   { echo -e "${GREEN}[UFW]${NC} $1"; }

# ─── Pre-flight: prevent lockout ───────────────────────────
if ! ss -tlnp | grep -q ':22 '; then
    echo -e "${RED}[ERROR]${NC} SSH not detected on port 22. Check your SSH port first."
    exit 1
fi

# ─── Reset existing rules ───────────────────────────────────
ufw --force reset

# ─── Default policies ────────────────────────────────────────
ufw default deny incoming
ufw default allow outgoing

# ─── Allow SSH (port 22) ───────────────────────────────────
# Comment prevents duplicate rules on re-run
ufw allow 22/tcp comment 'SSH' || true

# ─── Allow HTTP + HTTPS ─────────────────────────────────────
ufw allow 80/tcp comment 'HTTP'  || true
ufw allow 443/tcp comment 'HTTPS' || true

# ─── Allow Docker internal (optional) ───────────────────────
# ufw allow 2375/tcp comment 'Docker'  # Only if remote Docker API needed

# ─── Rate limiting on SSH (brute-force protection) ────────
ufw limit 22/tcp comment 'SSH rate-limit'

# ─── Enable UFW ─────────────────────────────────────────────
echo "y" | ufw enable

# ─── Show status ────────────────────────────────────────────
ufw status numbered

ok "Firewall configured — only SSH(22), HTTP(80), HTTPS(443) open"
