# Cereja OS — Operations Runbook

**Version:** 1.0  
**Last Updated:** 2026-03-30  
**Environment:** Production / Staging

---

## Table of Contents

1. [Health Check](#1-health-check)
2. [Service Restart](#2-service-restart)
3. [Service Logs](#3-service-logs)
4. [Database Backup](#4-database-backup)
5. [Database Restore](#5-database-restore)
6. [SSL Certificate Renewal](#6-ssl-certificate-renewal)
7. [Rollback to Previous Version](#7-rollback-to-previous-version)
8. [Scaling Services](#8-scaling-services)
9. [Redis Cache Flush](#9-redis-cache-flush)
10. [Emergency Stop](#10-emergency-stop)
11. [Disk Space Cleanup](#11-disk-space-cleanup)
12. [Memory & CPU Monitoring](#12-memory--cpu-monitoring)

---

## 1. Health Check

Check if all services are healthy.

```bash
# Run the health check script
./infrastructure/monitoring/health_check.sh

# Or manually:
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/health

# Docker status
docker compose -f infrastructure/docker/docker-compose.yml ps
```

**Expected:** All endpoints return HTTP 200 with `{"status":"ok"}`

---

## 2. Service Restart

Restart a specific service or all services.

```bash
# Restart all services
docker compose -f infrastructure/docker/docker-compose.yml restart

# Restart specific service
docker compose -f infrastructure/docker/docker-compose.yml restart api
docker compose -f infrastructure/docker/docker-compose.yml restart telegram
docker compose -f infrastructure/docker/docker-compose.yml restart nginx

# Full stop and start
docker compose -f infrastructure/docker/docker-compose.yml down
docker compose -f infrastructure/docker/docker-compose.yml up -d
```

---

## 3. Service Logs

View logs for troubleshooting.

```bash
# All services
docker compose -f infrastructure/docker/docker-compose.yml logs -f

# Specific service
docker compose -f infrastructure/docker/docker-compose.yml logs -f api
docker compose -f infrastructure/docker/docker-compose.yml logs -f telegram
docker compose -f infrastructure/docker/docker-compose.yml logs -f nginx

# Last N lines
docker compose -f infrastructure/docker/docker-compose.yml logs --tail=100 api

# Logs with timestamps
docker compose -f infrastructure/docker/docker-compose.yml logs -t api
```

---

## 4. Database Backup

Backup the SQLite database.

```bash
# Create backup directory
mkdir -p /opt/cereja-os/backups

# Backup with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
cp /opt/cereja-os/data/cereja.db /opt/cereja-os/backups/cereja_$TIMESTAMP.db

# Compress backup
gzip /opt/cereja-os/backups/cereja_$TIMESTAMP.db

# List backups
ls -lah /opt/cereja-os/backups/

# Automated backup (add to crontab)
# 0 2 * * * /opt/cereja-os/infrastructure/scripts/backup.sh
```

---

## 5. Database Restore

Restore from a backup.

```bash
# Stop services
docker compose -f infrastructure/docker/docker-compose.yml stop api

# Restore (replace TIMESTAMP with actual file)
gunzip /opt/cereja-os/backups/cereja_TIMESTAMPhere.db.gz
cp /opt/cereja-os/backups/cereja_TIMESTAMPhere.db /opt/cereja-os/data/cereja.db

# Start services
docker compose -f infrastructure/docker/docker-compose.yml start api

# Verify
curl http://localhost:8000/health
```

---

## 6. SSL Certificate Renewal

Renew Let's Encrypt SSL certificates.

```bash
# Check certificate status
certbot certificates

# Manual renewal
sudo certbot renew --force-renewal

# Or via certbot standalone (requires port 80 free)
sudo certbot certonly --standalone -d api.cereja.cloud -d dashboard.cereja.cloud

# Copy certificates to nginx volume
sudo cp /etc/letsencrypt/live/cereja.cloud/fullchain.pem /opt/cereja-os/infrastructure/docker/ssl/
sudo cp /etc/letsencrypt/live/cereja.cloud/privkey.pem /opt/cereja-os/infrastructure/docker/ssl/

# Reload nginx
docker compose -f infrastructure/docker/docker-compose.yml exec nginx nginx -s reload
```

---

## 7. Rollback to Previous Version

Rollback to a previous deployment.

```bash
# Check available images
docker images | grep cereja

# Tag current image as backup
docker tag cereja-os/api:latest cereja-os/api:rollback-$(date +%Y%m%d)

# Pull specific previous version
# Replace SHA with actual image tag
docker pull ghcr.io/your-org/cereja-os/api:SHA

# Update docker-compose to use specific tag
# Edit infrastructure/docker/docker-compose.yml

# Restart services
docker compose -f infrastructure/docker/docker-compose.yml up -d api

# Verify
curl http://localhost:8000/health
```

---

## 8. Scaling Services

Scale API or other services.

```bash
# Scale API to 3 replicas (requires load balancer)
docker compose -f infrastructure/docker/docker-compose.yml up -d --scale api=3

# Check scaled services
docker compose -f infrastructure/docker/docker-compose.yml ps

# Scale back to 1
docker compose -f infrastructure/docker/docker-compose.yml up -d --scale api=1
```

---

## 9. Redis Cache Flush

Clear Redis cache (use with caution).

```bash
# Connect to Redis
docker exec -it cereja-redis redis-cli

# Inside redis-cli:
AUTH your_redis_password  # if configured
FLUSHALL                 # Clear all data
FLUSHDB                  # Clear current database
INFO keyspace            # Check keys

# Or one-liner (bypass interactive)
docker exec cereja-redis redis-cli FLUSHALL
```

---

## 10. Emergency Stop

Stop all services immediately.

```bash
# Stop everything
docker compose -f infrastructure/docker/docker-compose.yml down

# Kill all containers (force)
docker kill $(docker ps -q)

# Remove all containers
docker rm -f $(docker ps -aq)

# Stop docker daemon (on host)
sudo systemctl stop docker

# Firewall block all traffic (on host)
sudo ufw deny in on eth0
```

---

## 11. Disk Space Cleanup

Free up disk space.

```bash
# Docker system prune
docker system prune -a

# Remove unused volumes
docker volume prune

# Remove stopped containers
docker container prune

# Clean up old images
docker image prune -a

# Full cleanup
docker system prune -a --volumes

# Check disk usage
df -h
du -sh /opt/cereja-os/*
```

---

## 12. Memory & CPU Monitoring

Monitor resource usage.

```bash
# Container stats
docker stats

# All containers (non-streaming)
docker stats --no-stream

# Specific container
docker stats cereja-api --no-stream

# Host resources
free -h
df -h
top -bn1 | head -20

# Docker system df
docker system df

# Container resource limits (check docker-compose.yml)
```

---

## Quick Reference

| Action | Command |
|--------|---------|
| Start | `docker compose -f infrastructure/docker/docker-compose.yml up -d` |
| Stop | `docker compose -f infrastructure/docker/docker-compose.yml down` |
| Restart | `docker compose -f infrastructure/docker/docker-compose.yml restart` |
| Logs | `docker compose -f infrastructure/docker/docker-compose.yml logs -f` |
| Health | `./infrastructure/monitoring/health_check.sh` |
| Status | `docker compose -f infrastructure/docker/docker-compose.yml ps` |

## Emergency Contacts

- **DevOps Lead:** [contact]
- **Technical Lead:** [contact]
- **On-call:** [contact]

## Incident Response

1. **Identify** — Check which service is failing: `docker compose ps`
2. **Contain** — Isolate the issue: `docker compose logs <service>`
3. **Resolve** — Apply fix from this runbook
4. **Notify** — Alert team if production impact
5. **Document** — Log incident in monitoring system
