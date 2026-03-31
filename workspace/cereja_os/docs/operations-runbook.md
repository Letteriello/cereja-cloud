# Cereja OS — Operations Runbook

**Version:** 1.0
**Last Updated:** 2026-03-30
**Environment:** Production
**Stack:** Docker Compose | FastAPI | Next.js | Redis | Nginx | Telegram Bot

---

## Table of Contents

1. [Service Overview](#1-service-overview)
2. [Health Checks](#2-health-checks)
3. [Service Logs](#3-service-logs)
4. [Service Restart Procedures](#4-service-restart-procedures)
5. [Database Backup & Restore](#5-database-backup--restore)
6. [SSL Certificate Renewal](#6-ssl-certificate-renewal)
7. [Rollback to Previous Version](#7-rollback-to-previous-version)
8. [Scaling Services](#8-scaling-services)
9. [Redis Cache Operations](#9-redis-cache-operations)
10. [Emergency Stop](#10-emergency-stop)
11. [Disk Space Management](#11-disk-space-management)
12. [Memory & CPU Monitoring](#12-memory--cpu-monitoring)
13. [Common Troubleshooting](#13-common-troubleshooting)
14. [Incident Response](#14-incident-response)

---

## 1. Service Overview

### Services

| Container | Image | Port | Purpose | Health Endpoint |
|-----------|-------|------|---------|-----------------|
| `cereja-api` | FastAPI (Python 3.11) | 8000 | Task management API | `http://localhost:8000/health` |
| `cereja-dashboard` | Next.js (Node 22) | 3000 | Vue/Next SPA frontend | `http://localhost:3000/api/health` |
| `cereja-telegram` | Python 3.11 bot | 8080 | Telegram webhook bot | `http://localhost:8080/health` |
| `cereja-redis` | Redis 7 Alpine | 6379 | Cache & sessions | `redis-cli ping` |
| `cereja-nginx` | Nginx Alpine | 80/443 | Reverse proxy + SSL | — |
| `cereja-watchtower` | Watchtower latest | — | Auto-update containers | — |

### Domains

| Domain | Service | SSL |
|--------|---------|-----|
| `api.cereja.cloud` | API (FastAPI) | Yes |
| `dashboard.cereja.cloud` | Dashboard (Next.js SPA) | Yes |
| `telegram.cereja.cloud` | Telegram webhook | Yes |
| `cereja.cloud` | Root redirect | Yes |

### Key Paths

| Purpose | Path |
|---------|------|
| Project root | `/opt/cereja-os/` |
| Docker compose | `/opt/cereja-os/infrastructure/docker/docker-compose.yml` |
| Data (SQLite) | `/opt/cereja-os/data/` |
| Logs | `/opt/cereja-os/logs/` |
| SSL certificates | `/opt/cereja-os/infrastructure/docker/ssl/` |
| Nginx logs | Docker volume `nginx-logs` |
| Redis data | Docker volume `redis-data` |

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | SQLite connection | `sqlite:///./data/cereja.db` |
| `REDIS_URL` | Redis connection | `redis://redis:6379` |
| `EXTERNAL_URL` | Public URL | `https://api.cereja.cloud` |
| `ADMIN_TOKEN` | Admin authentication | (generated) |
| `JWT_SECRET` | JWT signing secret | (generated) |
| `TENANT_SECRET` | Multi-tenant isolation key | (generated) |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | `123456:ABC-...` |
| `TELEGRAM_BOT_WEBHOOK_HOST` | Public webhook URL | `https://telegram.cereja.cloud` |
| `LOG_LEVEL` | Logging level | `INFO` / `DEBUG` |

---

## 2. Health Checks

### Automated Health Check

```bash
# Run the monitoring script
./infrastructure/monitoring/health_check.sh

# With custom URLs
./infrastructure/monitoring/health_check.sh https://api.cereja.cloud https://dashboard.cereja.cloud
```

### Manual Health Checks

```bash
# API health
curl -sf https://api.cereja.cloud/health
# Expected: {"status":"ok","service":"Cereja","version":"1.0.0"}

# API v1 health
curl -sf https://api.cereja.cloud/api/v1/health

# Dashboard health
curl -sf https://dashboard.cereja.cloud/api/health

# Telegram bot health
curl -sf http://localhost:8080/health

# Redis
docker exec cereja-redis redis-cli ping
# Expected: PONG

# All containers status
docker compose -f infrastructure/docker/docker-compose.yml ps
```

### Cron Setup (every 5 minutes)

```bash
# Add to crontab
crontab -e

# Add this line:
*/5 * * * * /opt/cereja-os/infrastructure/monitoring/health_check.sh >> /var/log/cereja-health.log 2>&1
```

### Expected Responses

| Endpoint | Expected Code | Sample Response |
|----------|--------------|----------------|
| `GET /health` | 200 | `{"status":"ok","service":"Cereja"}` |
| `GET /api/v1/health` | 200 | `{"status":"ok"}` |
| `GET /api/health` (Dashboard) | 200 | `{"status":"ok"}` |
| `GET /health` (Telegram) | 200 | `{"status":"running"}` |
| Redis `PING` | PONG | `PONG` |

---

## 3. Service Logs

### View All Logs (real-time)

```bash
docker compose -f infrastructure/docker/docker-compose.yml logs -f
```

### View Specific Service Logs

```bash
# API logs (last 100 lines, follow)
docker compose -f infrastructure/docker/docker-compose.yml logs -f --tail=100 api

# Dashboard logs
docker compose -f infrastructure/docker/docker-compose.yml logs -f --tail=100 dashboard

# Telegram bot logs
docker compose -f infrastructure/docker/docker-compose.yml logs -f --tail=100 telegram

# Nginx access/error logs
docker compose -f infrastructure/docker/docker-compose.yml logs -f --tail=100 nginx

# Redis logs
docker compose -f infrastructure/docker/docker-compose.yml logs -f --tail=100 redis

# Watchtower logs
docker compose -f infrastructure/docker/docker-compose.yml logs -f --tail=100 watchtower
```

### Logs with Timestamps

```bash
docker compose -f infrastructure/docker/docker-compose.yml logs -t --tail=50 api
```

### Grep Logs for Errors

```bash
docker compose -f infrastructure/docker/docker-compose.yml logs api | grep -i error
docker compose -f infrastructure/docker/docker-compose.yml logs api | grep -i exception
docker compose -f infrastructure/docker/docker-compose.yml logs nginx | grep -i "5[0-9][0-9]"
```

### Nginx Access Log (inside container)

```bash
docker exec cereja-nginx tail -f /var/log/nginx/access.log
docker exec cereja-nginx tail -f /var/log/nginx/error.log
```

---

## 4. Service Restart Procedures

### Restart All Services

```bash
docker compose -f infrastructure/docker/docker-compose.yml restart
```

### Restart Individual Service

```bash
# API (FastAPI)
docker compose -f infrastructure/docker/docker-compose.yml restart api

# Dashboard (Next.js)
docker compose -f infrastructure/docker/docker-compose.yml restart dashboard

# Telegram bot
docker compose -f infrastructure/docker/docker-compose.yml restart telegram

# Nginx (reload config without downtime)
docker compose -f infrastructure/docker/docker-compose.yml exec nginx nginx -s reload

# Redis (rarely needed)
docker compose -f infrastructure/docker/docker-compose.yml restart redis
```

### Full Stop and Start

```bash
# Stop all
docker compose -f infrastructure/docker/docker-compose.yml down

# Start all (in detached mode)
docker compose -f infrastructure/docker/docker-compose.yml up -d

# Rebuild and start
docker compose -f infrastructure/docker/docker-compose.yml up -d --build
```

### Verify After Restart

```bash
sleep 10
curl -sf https://api.cereja.cloud/health && echo "API OK"
curl -sf https://dashboard.cereja.cloud/api/health && echo "Dashboard OK"
docker exec cereja-redis redis-cli ping && echo "Redis OK"
```

---

## 5. Database Backup & Restore

### Backup SQLite Database

```bash
# Manual backup
BACKUP_DIR="/opt/cereja-os/backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp /opt/cereja-os/data/cereja.db "$BACKUP_DIR/cereja_$TIMESTAMP.db"

# Compress
gzip "$BACKUP_DIR/cereja_$TIMESTAMP.db"

# List backups
ls -lah "$BACKUP_DIR"
```

### Automated Daily Backup (Crontab)

```bash
# Add to crontab -e
0 3 * * * /opt/cereja-os/infrastructure/scripts/backup.sh >> /var/log/cereja-backup.log 2>&1
```

### Restore from Backup

```bash
# 1. Stop API to avoid writes during restore
docker compose -f infrastructure/docker/docker-compose.yml stop api

# 2. Identify backup file
ls /opt/cereja-os/backups/

# 3. Restore (replace TIMESTAMP with actual)
gunzip /opt/cereja-os/backups/cereja_TIMESTAMPhere.db.gz
cp /opt/cereja-os/backups/cereja_TIMESTAMPhere.db /opt/cereja-os/data/cereja.db

# 4. Verify file ownership
chown $(whoami): /opt/cereja-os/data/cereja.db

# 5. Restart API
docker compose -f infrastructure/docker/docker-compose.yml start api

# 6. Verify
curl -sf https://api.cereja.cloud/health
```

### Backup Redis Data

```bash
# Redis RDB backup (automatic with AOF enabled)
docker exec cereja-redis redis-cli BGSAVE
# Check: docker exec cereja-redis redis-cli LASTSAVE

# Copy RDB file from volume
docker run --rm -v cereja_os_redis-data:/data -v /tmp:/backup alpine \
  cp /data/dump.rdb /backup/redis_backup_$(date +%Y%m%d).rdb
```

---

## 6. SSL Certificate Renewal

### Check Certificate Status

```bash
# Check all certs
sudo certbot certificates

# Check specific domain expiry
echo | openssl s_client -servername api.cereja.cloud -connect api.cereja.cloud:443 2>/dev/null \
  | openssl x509 -noout -dates
```

### Manual Renewal via Certbot

```bash
# Standalone mode (needs port 80 free)
sudo certbot certonly --standalone \
  -d api.cereja.cloud \
  -d dashboard.cereja.cloud \
  -d telegram.cereja.cloud \
  -d cereja.cloud \
  --email admin@cereja.cloud \
  --agree-tos --noninteractive --force-renewal

# Webroot mode (if nginx is running)
sudo certbot certonly --webroot -w /usr/share/nginx/html \
  -d api.cereja.cloud -d dashboard.cereja.cloud \
  --email admin@cereja.cloud --agree-tos --noninteractive
```

### Copy Certs to Nginx Volume

```bash
# After certbot renewal
sudo cp /etc/letsencrypt/live/cereja.cloud/fullchain.pem \
  /opt/cereja-os/infrastructure/docker/ssl/
sudo cp /etc/letsencrypt/live/cereja.cloud/privkey.pem \
  /opt/cereja-os/infrastructure/docker/ssl/

# Reload nginx
docker compose -f infrastructure/docker/docker-compose.yml exec nginx nginx -s reload
```

### Automated SSL Check + Renewal Script

```bash
# Run SSL renewal check
/opt/cereja-os/infrastructure/scripts/ssl-renew.sh

# Add to crontab (daily at 3 AM)
0 3 * * * /opt/cereja-os/infrastructure/scripts/ssl-renew.sh >> /var/log/ssl-renew.log 2>&1
```

### Verify SSL Certificate

```bash
# Test SSL grade
curl -sf https://api.cereja.cloud/health && echo "SSL OK"

# Detailed check
openssl s_client -connect api.cereja.cloud:443 -servername api.cereja.cloud </dev/null 2>/dev/null \
  | openssl x509 -noout -dates -subject
```

---

## 7. Rollback to Previous Version

### List Available Images

```bash
# Docker Hub / GHCR images
docker images | grep cereja

# See available tags
curl -s https://ghcr.io/v2/your-org/cereja-os/api/tags/list
```

### Rollback API

```bash
# Tag current image as rollback backup
docker tag cereja-api:latest cereja-api:rollback-$(date +%Y%m%d)

# Pull specific version
docker pull ghcr.io/your-org/cereja-os/api:SHA_OR_TAG

# Update docker-compose.yml to use specific tag, then:
docker compose -f infrastructure/docker/docker-compose.yml up -d api

# Or via image tag directly in compose override
```

### Rollback Dashboard

```bash
docker pull ghcr.io/your-org/cereja-os/dashboard:SHA_OR_TAG
docker compose -f infrastructure/docker/docker-compose.yml up -d --build dashboard
```

### Rollback Telegram Bot

```bash
docker pull ghcr.io/your-org/cereja-os/telegram:SHA_OR_TAG
docker compose -f infrastructure/docker/docker-compose.yml up -d telegram
```

### Verify Rollback

```bash
sleep 15
curl -sf https://api.cereja.cloud/health
docker compose -f infrastructure/docker/docker-compose.yml logs --tail=20 api
```

---

## 8. Scaling Services

### Scale API (requires external load balancer)

```bash
# Scale to N replicas (Docker Compose limitation: needs --scale flag)
docker compose -f infrastructure/docker/docker-compose.yml up -d --scale api=3

# Note: requires nginx upstream config update for load balancing
```

### Check Scaled Services

```bash
docker compose -f infrastructure/docker/docker-compose.yml ps
docker compose -f infrastructure/docker/docker-compose.yml logs --tail=5 api
```

### Scale Back to 1

```bash
docker compose -f infrastructure/docker/docker-compose.yml up -d --scale api=1
```

---

## 9. Redis Cache Operations

### Check Redis Status

```bash
# Ping
docker exec cereja-redis redis-cli ping

# Info
docker exec cereja-redis redis-cli info

# Key count
docker exec cereja-redis redis-cli dbsize

# List keys (small datasets)
docker exec cereja-redis redis-cli keys "*"
```

### Flush Redis Cache (Caution: clears sessions)

```bash
# Flush all databases
docker exec cereja-redis redis-cli FLUSHALL

# Flush current database
docker exec cereja-redis redis-cli FLUSHDB

# Selective key deletion
docker exec cereja-redis redis-cli DEL "session:123" "cache:456"
```

### Restart Redis

```bash
docker compose -f infrastructure/docker/docker-compose.yml restart redis
# Note: AOF persistence is enabled, data is preserved
```

---

## 10. Emergency Stop

### Stop All Services Quickly

```bash
# Graceful stop
docker compose -f infrastructure/docker/docker-compose.yml down

# Force kill all containers
docker kill $(docker ps -q)

# Remove all containers (clean slate)
docker rm -f $(docker ps -aq)
```

### Network Isolation (firewall level)

```bash
# Block all ingress (keep SSH)
sudo ufw deny in on eth0

# Block specific port
sudo ufw deny 8000/tcp

# Re-enable
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### Stopwatch (disable auto-updates)

```bash
# Disable watchtower during incident
docker compose -f infrastructure/docker/docker-compose.yml stop watchtower
```

---

## 11. Disk Space Management

### Check Disk Usage

```bash
# Overall
df -h

# Per directory
du -sh /opt/cereja-os/*
du -sh /opt/cereja-os/data/*
du -sh /opt/cereja-os/logs/*

# Docker space
docker system df
docker system df -v
```

### Docker Prune (safe cleanup)

```bash
# Remove stopped containers
docker container prune -f

# Remove unused images
docker image prune -f

# Remove unused volumes
docker volume prune -f

# Combined (aggressive)
docker system prune -f
```

### Full Cleanup

```bash
# Remove ALL unused (containers, networks, images, volumes)
docker system prune -a --volumes -f

# Warning: This removes ALL stopped containers and unused volumes
```

### Nginx Logs Cleanup

```bash
# Truncate nginx logs (keeps container running)
docker exec cereja-nginx sh -c '> /var/log/nginx/access.log'
docker exec cereja-nginx sh -c '> /var/log/nginx/error.log'

# Or set up logrotate
```

### Logrotate Configuration

```bash
# /etc/logrotate.d/cereja-os
/opt/cereja-os/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}

/var/lib/docker/volumes/cereja_os_nginx-logs/_data/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

---

## 12. Memory & CPU Monitoring

### Container Stats (real-time)

```bash
# Live stats for all containers
docker stats

# One-shot (non-streaming)
docker stats --no-stream

# Specific container
docker stats cereja-api cereja-redis --no-stream

# With CPU %, Memory, Network, Block I/O
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
```

### Host Resources

```bash
# CPU and load
top -bn1 | head -20
uptime

# Memory
free -h

# Disk I/O
iostat -x 1 5

# Process list
ps aux --sort=-%mem | head -15
```

### Docker Resource Limits

Check limits defined in docker-compose.yml:

```bash
grep -A5 "mem_limit\|cpus" infrastructure/docker/docker-compose.yml
```

### Set Resource Limits (runtime)

```bash
# Update API memory limit to 1GB
docker update --memory="1g" cereja-api

# Set CPU limit
docker update --cpus="1.0" cereja-api
```

### Cron: Daily Resource Report

```bash
# Add to crontab
0 8 * * * docker stats --no-stream >> /var/log/cereja-resources-$(date +\%Y\%m).log
```

---

## 13. Common Troubleshooting

### API returns 502 Bad Gateway

```bash
# 1. Check if API is healthy
curl -sf http://localhost:8000/health

# 2. Check nginx upstream config
docker compose -f infrastructure/docker/docker-compose.yml logs nginx | grep -i "upstream"

# 3. Restart API
docker compose -f infrastructure/docker/docker-compose.yml restart api

# 4. Check security (SELinux/AppArmor may block)
docker compose -f infrastructure/docker/docker-compose.yml logs api | grep -i "permission"
```

### Telegram Bot Not Responding

```bash
# 1. Check bot health
curl -sf http://localhost:8080/health

# 2. Check Telegram API connectivity
docker compose -f infrastructure/docker/docker-compose.yml logs telegram | grep -i "webhook\|telegram\|error"

# 3. Verify bot token
docker exec cereja-telegram env | grep BOT_TOKEN

# 4. Restart bot
docker compose -f infrastructure/docker/docker-compose.yml restart telegram

# 5. Check webhook registration
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo"
```

### Dashboard Returns 404 or Blank Page

```bash
# 1. Check dashboard health
curl -sf http://localhost:3000/api/health

# 2. Check Next.js build
docker compose -f infrastructure/docker/docker-compose.yml logs dashboard | grep -i "error\|warn"

# 3. Check nginx SPA fallback config
docker exec cereja-nginx cat /etc/nginx/conf.d/default.conf | grep -i "try_files\|spa"

# 4. Rebuild dashboard
docker compose -f infrastructure/docker/docker-compose.yml up -d --build dashboard
```

### Redis Connection Failures

```bash
# 1. Check Redis is running
docker compose -f infrastructure/docker/docker-compose.yml ps redis

# 2. Test connection from API container
docker exec cereja-api python -c "import redis; r = redis.from_url('redis://redis:6379'); print(r.ping())"

# 3. Check Redis logs
docker compose -f infrastructure/docker/docker-compose.yml logs redis

# 4. Restart Redis
docker compose -f infrastructure/docker/docker-compose.yml restart redis
```

### High Memory Usage

```bash
# Which container?
docker stats --no-stream --format "{{.Name}}: {{.MemUsage}}"

# API logs (possible memory leak)
docker compose -f infrastructure/docker/docker-compose.yml logs api | grep -i "memory\|leak"

# Restart affected service
docker compose -f infrastructure/docker/docker-compose.yml restart api
```

### SSL Certificate Errors

```bash
# Check cert files exist
ls -la /opt/cereja-os/infrastructure/docker/ssl/

# Verify cert matches domain
openssl x509 -in /opt/cereja-os/infrastructure/docker/ssl/fullchain.pem -noout -subject

# Check nginx SSL config
docker exec cereja-nginx cat /etc/nginx/conf.d/default.conf | grep -i ssl

# Reload nginx
docker compose -f infrastructure/docker/docker-compose.yml exec nginx nginx -s reload
```

### Watchtower Breaking Things

```bash
# Check what Watchtower updated
docker compose -f infrastructure/docker/docker-compose.yml logs watchtower | grep -i "stopping\|updating"

# Temporarily disable Watchtower
docker compose -f infrastructure/docker/docker-compose.yml stop watchtower

# Pin a specific image version to prevent auto-update
docker tag IMAGE:TAG ghcr.io/your-org/cereja-os/api:stable
# Then edit docker-compose.yml to use :stable tag
```

---

## 14. Incident Response

### Response Flow

```
1. IDENTIFY  → Which service is failing?
               docker compose ps
               docker compose logs <service>

2. CONTAIN  → Isolate the issue, prevent cascade
               docker compose restart <service>
               docker compose stop <service>  (if needed)

3. RESOLVE  → Apply fix from this runbook
               → If unknown: escalate to DevOps lead

4. NOTIFY   → Alert team if production impact
               ./infrastructure/monitoring/alerts.sh error "Service X is down"

5. DOCUMENT → Log incident in monitoring system
               → Record: what happened, when, resolution, duration
```

### Quick Diagnostic One-Liner

```bash
echo "=== Containers ===" && \
docker compose -f infrastructure/docker/docker-compose.yml ps && \
echo "=== API Health ===" && curl -sf http://localhost:8000/health && \
echo "=== Dashboard Health ===" && curl -sf http://localhost:3000/api/health && \
echo "=== Redis ===" && docker exec cereja-redis redis-cli ping && \
echo "=== Disk ===" && df -h / && \
echo "=== Docker Space ===" && docker system df --format '{{.Type}}: {{.Size}}'
```

### Alerting Commands

```bash
# Service down alert
./infrastructure/monitoring/alerts.sh service-down api

# Service recovered
./infrastructure/monitoring/alerts.sh service-recovered api

# Disk space warning
./infrastructure/monitoring/alerts.sh disk-space 90

# SSL expiring
./infrastructure/monitoring/alerts.sh ssl-expiring 14
```

### Cron Health Check with Alert

```bash
# Add to crontab (every 5 minutes)
*/5 * * * * /opt/cereja-os/infrastructure/monitoring/health_check.sh \
  >> /var/log/cereja-health.log 2>&1 || \
  /opt/cereja-os/infrastructure/monitoring/alerts.sh error "Health check failed on $(hostname)"
```

---

## Quick Reference Card

| Action | Command |
|--------|---------|
| Start all | `docker compose -f infrastructure/docker/docker-compose.yml up -d` |
| Stop all | `docker compose -f infrastructure/docker/docker-compose.yml down` |
| Restart API | `docker compose -f infrastructure/docker/docker-compose.yml restart api` |
| View logs | `docker compose -f infrastructure/docker/docker-compose.yml logs -f` |
| Health check | `curl -sf https://api.cereja.cloud/health` |
| Redis ping | `docker exec cereja-redis redis-cli ping` |
| SSL check | `certbot certificates` |
| Disk usage | `docker system df` |
| Container stats | `docker stats --no-stream` |
| Backup DB | `cp /opt/cereja-os/data/cereja.db /opt/cereja-os/backups/cereja_$(date +%Y%m%d_%H%M%S).db` |
| Restore DB | `cp /opt/cereja-os/backups/cereja_TIMESTAMP.db /opt/cereja-os/data/cereja.db` |

---

## Emergency Contacts

| Role | Contact | Escalation |
|------|---------|------------|
| DevOps Lead | (fill in) | — |
| Technical Lead | (fill in) | — |
| On-call | (fill in) | 24/7 |
| Cloud Provider | (fill in) | Support portal |

---

*Last reviewed: 2026-03-30*
