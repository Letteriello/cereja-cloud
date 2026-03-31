# Cereja OS — Infrastructure

Infrastructure as code for Cereja OS deployment.

## Structure

```
infrastructure/
├── docker/
│   ├── docker-compose.yml      # Production stack
│   ├── nginx.conf               # Reverse proxy (API + Dashboard + Telegram)
│   ├── nginx-dashboard.conf     # Vue SPA fallback config
│   └── ssl/                     # SSL certificates (generated on VPS)
├── monitoring/
│   ├── health_check.sh          # Health monitoring script
│   ├── alerts.sh                # Alerting system
│   ├── ssl-renew.sh             # SSL auto-renewal check
│   └── runbook.md               # Operations runbook (12 procedures)
├── env/
│   └── .env.example              # Environment variables template
├── vps-setup.sh                  # Fresh VPS provisioning script
├── ssl-setup.sh                  # SSL certificate generation
└── ufw-firewall.sh               # Firewall configuration
```

## Fresh VPS Setup (one-time)

On a new Ubuntu 22.04+ VPS:

```bash
# As root, run the provisioning script:
curl -fsSL https://your-repo/vps-setup.sh | bash

# Or clone repo and run manually:
git clone <repo> /opt/cereja-os
cd /opt/cereja-os
sudo bash infrastructure/vps-setup.sh

# Then edit environment:
nano /opt/cereja-os/.env
```

### Firewall (standalone, if not using vps-setup.sh)

```bash
sudo bash infrastructure/ufw-firewall.sh
```

### SSL Certificates (standalone, if not using vps-setup.sh)

```bash
# Requires DNS pointing to server
sudo bash infrastructure/ssl-setup.sh admin@cereja.cloud \
    api.cereja.cloud dashboard.cereja.cloud cereja.cloud telegram.cereja.cloud
```

## Quick Start

### 1. Configure Environment

```bash
cp infrastructure/env/.env.example .env
nano .env  # Fill in real values
```

### 2. Deploy Stack

```bash
docker compose -f infrastructure/docker/docker-compose.yml up -d
```

### 3. Verify Deployment

```bash
# Health check
./infrastructure/monitoring/health_check.sh

# Or manual
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/health
```

## Services

| Service | Domain | Description |
|---------|--------|-------------|
| API | api.cereja.cloud:443 | FastAPI backend |
| Dashboard | dashboard.cereja.cloud:443 | Vue 3 SPA |
| Telegram | telegram.cereja.cloud:443 | Telegram bot webhook |
| Redis | internal:6379 | Cache & sessions |
| Nginx | *:80/443 | Reverse proxy + SSL |

## Domains Covered

- `api.cereja.cloud` — API (FastAPI)
- `dashboard.cereja.cloud` — Frontend (Vue SPA)
- `cereja.cloud` — Redirect to HTTPS
- `telegram.cereja.cloud` — Telegram webhook

## Health Monitoring

```bash
# Run health check
./infrastructure/monitoring/health_check.sh

# Setup cron (every 5 minutes)
*/5 * * * * /opt/cereja-os/infrastructure/monitoring/health_check.sh >> /var/log/cereja-health.log 2>&1
```

## SSL Certificate Auto-Renewal

Certbot renews automatically. Verify with:

```bash
certbot renew --dry-run
```

## Operations

See [monitoring/runbook.md](monitoring/runbook.md) for 12 operational procedures:

1. Health Check
2. Service Restart
3. Service Logs
4. Database Backup
5. Database Restore
6. SSL Certificate Renewal
7. Rollback to Previous Version
8. Scaling Services
9. Redis Cache Flush
10. Emergency Stop
11. Disk Space Cleanup
12. Memory & CPU Monitoring

## GitHub Actions CI/CD

The CI/CD pipeline is configured in `.github/workflows/ci-cd.yml`:

- **Lint & Type Check** — on PR and push
- **Unit Tests** — after lint
- **Build Docker Images** — after tests (on push to main/develop)
- **Deploy to Staging** — on push to develop
- **Deploy to Production** — on push to main
- **Health Check** — post-deployment verification

### Required Secrets

```bash
STAGING_HOST, STAGING_USER, STAGING_SSH_KEY
PROD_HOST, PROD_USER, PROD_SSH_KEY
```

## Troubleshooting

```bash
# Check all services
docker compose -f infrastructure/docker/docker-compose.yml ps

# View logs
docker compose -f infrastructure/docker/docker-compose.yml logs -f api

# Restart all
docker compose -f infrastructure/docker/docker-compose.yml restart

# Check SSL
certbot certificates
openssl s_client -connect api.cereja.cloud:443 -servername api.cereja.cloud

# Check firewall
ufw status numbered
```
