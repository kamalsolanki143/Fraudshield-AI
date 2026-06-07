# FraudShield Bot Module — Deployment Guide

## 1. Local Development Setup

### Prerequisites

- Python 3.11+
- Redis 7+ (`brew install redis` on macOS)
- MongoDB Atlas account (or local MongoDB 6+)
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))

### Clone and Install

```bash
git clone <repo-url>
cd fraudshield

python3.11 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```bash
TELEGRAM_BOT_TOKEN=8775040576:AAEVMo6Rizx7xD9bm-4dhhu84myofb1XQTM
MONGODB_URI=mongodb+srv://user:pass@cluster0.xxxxx.mongodb.net/fraudshield
MONGODB_DB_NAME=fraudshield
REDIS_URL=redis://localhost:6379
ANALYSIS_API_URL=https://teammate-cloudrun-url/analyse
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
NPCI_EMAIL=helpdesk@npci.org.in
CERT_IN_EMAIL=incident@cert-in.org.in
RAZORPAY_PRO_PLAN_LINK=https://razorpay.com/your-plan-link
ENVIRONMENT=development
```

### Run Redis Locally

```bash
redis-server
```

Verify: `redis-cli ping` → `PONG`

### Run the Bot

```bash
python backend/bot/telegram_bot.py
```

Expected output:
```
INFO [__main__] Starting FraudShield bot...
INFO [database.mongo] MongoDB initialized successfully | db=fraudshield
INFO [database.redis] Redis connected: redis://localhost:6379
INFO [services.alert_service] APScheduler configured: daily 03:30 UTC, Monday 03:30 UTC
INFO [__main__] Starting polling (drop_pending_updates=True)...
```

### Running with Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "backend/bot/telegram_bot.py"]
```

```bash
docker build -t fraudshield-bot .
docker run --env-file .env fraudshield-bot
```

### Docker Compose

```yaml
# docker-compose.yml
version: "3.9"
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  bot:
    build: .
    env_file: .env
    depends_on:
      - redis
    environment:
      REDIS_URL: redis://redis:6379
```

```bash
docker compose up
```

---

## 2. Google Cloud Run Deployment

### Prerequisites

- Google Cloud SDK installed and authenticated
- Docker installed
- Artifact Registry repository created
- Cloud Run enabled

### Build and Push Docker Image

```bash
# Set project
PROJECT_ID="your-project-id"
REGION="asia-south1"
REPO_NAME="fraudshield"
IMAGE_NAME="bot"

# Configure Docker for Artifact Registry
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Build
docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:latest .

# Push
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:latest
```

### Deploy to Cloud Run

```bash
gcloud run deploy fraudshield-bot \
  --image=${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:latest \
  --region=${REGION} \
  --platform=managed \
  --no-allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=1 \
  --concurrency=80 \
  --timeout=300 \
  --set-env-vars="MONGODB_DB_NAME=fraudshield,REDIS_URL=redis://10.0.0.3:6379,ENVIRONMENT=production" \
  --set-secrets="TELEGRAM_BOT_TOKEN=telegram-bot-token:latest,MONGODB_URI=mongodb-uri:latest"
```

> **Note:** Use Secret Manager for sensitive env vars. Create secrets via:
> ```bash
> echo -n "your-bot-token" | gcloud secrets create telegram-bot-token --data-file=-
> ```

### Scaling Notes

- Set `--min-instances=0` for cost savings (bot is event-driven)
- Set `--max-instances=1` to avoid duplicate polling
- `--concurrency=80` allows handling multiple Telegram updates concurrently

---

## 3. MongoDB Atlas Setup

### Create Cluster

1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Create a new cluster (M0 free tier is sufficient)
3. Under Security → Network Access → Add IP whitelist
4. Under Security → Database Access → Create database user

### Connection String

Format:
```
mongodb+srv://<username>:<password>@<cluster>.mongodb.net/fraudshield?retryWrites=true&w=majority
```

### Collections

The bot auto-creates collections and indexes on first run (`MongoClient.initialize()`). Required collections:

| Collection | Index | Unique |
|-----------|-------|--------|
| users | telegram_id | Yes |
| fraud_upi_ids | upi_id | Yes |
| fraud_phone_numbers | phone | Yes |
| scam_patterns | active | No |
| advisories | pushed_to_users | No |
| community_reports | (reported_by, status) | No |
| critical_reports | case_id | Yes |
| analysis_history | user_id | No |

You can verify indexes in Atlas UI or via shell:
```bash
mongosh "mongodb+srv://user:pass@cluster.mongodb.net/fraudshield"
> db.users.getIndexes()
```

### Seed Script (Optional)

```python
# scripts/seed_patterns.py
from database.mongo import MongoClient
import asyncio

async def seed():
    db = MongoClient()
    await db.initialize()

    patterns = [
        {
            "name": "Fake KYC",
            "trigger_phrases_en": ["kyc", "expire", "update", "block"],
            "trigger_phrases_hi": ["केवाईसी", "समाप्त", "अपडेट", "ब्लॉक"],
            "description_en": "Fraudsters send fake KYC expiry messages with phishing links.",
            "description_hi": "धोखेबाज फिशिंग लिंक के साथ नकली KYC एक्सपायरी संदेश भेजते हैं।",
            "active": True,
            "reported_cities": []
        },
        {
            "name": "Collect Request",
            "trigger_phrases_en": ["collect", "request", "accept", "approve"],
            "trigger_phrases_hi": ["कलेक्ट", "अनुरोध", "स्वीकार", "अप्रूव"],
            "description_en": "Scammers send UPI collect requests to trick victims into sending money.",
            "description_hi": "ठग पैसे भेजने के लिए पीड़ितों को UPI कलेक्ट रिक्वेस्ट भेजते हैं।",
            "active": True,
            "reported_cities": []
        },
        {
            "name": "Lottery Scam",
            "trigger_phrases_en": ["lottery", "won", "prize", "processing fee"],
            "trigger_phrases_hi": ["लॉटरी", "जीता", "पुरस्कार", "प्रोसेसिंग फीस"],
            "description_en": "Fake lottery winnings that require a processing fee to claim.",
            "description_hi": "नकली लॉटरी जीत जो दावा करने के लिए प्रोसेसिंग फीस मांगती है।",
            "active": True,
            "reported_cities": []
        },
    ]

    for p in patterns:
        await db.scam_patterns.update_one(
            {"name": p["name"]},
            {"$setOnInsert": p},
            upsert=True,
        )
        print(f"Seeded pattern: {p['name']}")

    await db.close()

asyncio.run(seed())
```

---

## 4. Redis Setup (Cloud Memorystore)

### Create Memorystore Instance

```bash
gcloud redis instances create fraudshield-redis \
  --size=1 \
  --region=asia-south1 \
  --redis-version=redis_7_0 \
  --network=default \
  --connect-mode=private-service-access
```

Get the IP:
```bash
gcloud redis instances describe fraudshield-redis --region=asia-south1 --format="value(host)"
```

### Connect Cloud Run to VPC

Since Memorystore requires VPC access, Cloud Run must use VPC egress:

```bash
gcloud run services update fraudshield-bot \
  --region=asia-south1 \
  --add-cloudsql-instances="" \
  --vpc-connector=fraudshield-connector \
  --vpc-egress=private-ranges-only
```

> **Note:** Create a [Serverless VPC Access connector](https://cloud.google.com/vpc/docs/configure-serverless-vpc-access) first.

### Redis as Optional Dependency

The bot treats Redis as a cache — if Redis is down, it logs a warning and continues operating without caching. All Redis operations fail silently.

---

## 5. Telegram Bot Setup

### Create Bot with BotFather

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot`
3. Choose a name (e.g., `FraudShield`)
4. Choose a username (e.g., `FraudShieldBot`)
5. Save the API token

### Set Bot Commands

Send these commands to BotFather to configure the menu:

```
/help
/check - Analyse a screenshot or UPI ID
/lookup <id> - Search fraud database
/report <id> - Report a scammer
/status - View your account
/tip - Get a fraud safety tip
/start - Setup your profile
/help - Show all commands
```

Or use the API directly:
```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setMyCommands" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      {"command": "start", "description": "Setup your profile"},
      {"command": "check", "description": "Analyse a screenshot or UPI ID"},
      {"command": "lookup", "description": "Search fraud database"},
      {"command": "report", "description": "Report a scammer"},
      {"command": "status", "description": "View your account"},
      {"command": "tip", "description": "Get a fraud safety tip"},
      {"command": "help", "description": "Show all commands"}
    ]
  }'
```

### Webhook vs Polling

**Polling** (recommended for single-instance deployment, used here):
```python
await app.run_polling(drop_pending_updates=True)
```
Simple, no HTTPS requirement. Must use `--max-instances=1`.

**Webhook** (for production multi-instance):
```python
await app.run_webhook(
    listen="0.0.0.0",
    port=8080,
    url_path=TELEGRAM_BOT_TOKEN,
    webhook_url=f"https://your-domain.com/{TELEGRAM_BOT_TOKEN}",
)
```
To switch to webhook mode, update `telegram_bot.py` and set the webhook:
```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://your-domain.com/<TOKEN>"
```

### Rate Limits

Telegram restricts bots to ~30 messages/second. The `AlertService` enforces a 1/30s delay between batch sends. For high-volume alerts, consider:
- Using `sendMediaGroup` for grouped messages
- Implementing message priority queues
- Distributing sends across multiple bot instances (one per shard)

---

## 6. Monitoring & Logging

### Cloud Logging (Google Cloud Run)

Logs are automatically collected by Cloud Logging. View via:
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=fraudshield-bot" --limit=10
```

### Alerts

Set up uptime monitoring and alert on `CRITICAL` log entries (e.g., email send failures).

### Redis Monitoring

```bash
gcloud redis instances describe fraudshield-redis --region=asia-south1
# Check: connectedClients, keyspaceHitRate, cpuUtilization
```

### MongoDB Monitoring

Enable monitoring in Atlas UI:
- Alerts on CPU > 80%
- Alerts on connections > 80%
- Slow query profiler

---

## 7. Production Checklist

- [ ] Use Secret Manager for all secrets (not `.env` files)
- [ ] Enable VPC connector for Redis access
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure MongoDB Atlas IP whitelist (Cloud Run egress IPs or VPC)
- [ ] Set `--max-instances=1` for polling mode
- [ ] Switch to webhook mode for multi-instance HA
- [ ] Set up uptime monitoring
- [ ] Configure Cloud Logging alerts for ERROR-level logs
- [ ] Test critical alert email delivery
- [ ] Verify APScheduler jobs run on schedule
