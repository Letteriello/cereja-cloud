# Telegram Bot Dockerfile - Cereja OS
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements_telegram.txt .
RUN pip install --no-cache-dir -r requirements_telegram.txt

# Copy application code
COPY bot_config.py .
COPY bot_main.py .

# Environment variables (set at runtime)
ENV BOT_TOKEN=""
ENV WEBHOOK_MODE="true"
ENV WEBHOOK_HOST=""
ENV WEBHOOK_PATH="/webhook/telegram"
ENV SERVER_HOST="0.0.0.0"
ENV SERVER_PORT="8080"
# Optional: TENANT_MAP="123456:tenant1,789012:tenant2"

# Expose webhook port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run the bot
CMD ["python", "bot_main.py"]
