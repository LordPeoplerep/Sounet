# Souent Deployment Guide

## Table of Contents
1. [Quick Start (Development)](#quick-start-development)
2. [Docker Deployment](#docker-deployment)
3. [Production Deployment](#production-deployment)
4. [Environment Variables](#environment-variables)
5. [Troubleshooting](#troubleshooting)

---

## Quick Start (Development)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis (optional)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Initialize database
python -m app.core.init_db

# Run server
uvicorn app.main:app --reload
```

Backend runs at: http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with backend URL

# Run development server
npm run dev
```

Frontend runs at: http://localhost:5173

---

## Docker Deployment

### Prerequisites
- Docker
- Docker Compose

### Steps

1. **Create environment file:**
```bash
cp .env.example .env
# Edit .env with your configuration
```

2. **Build and run:**
```bash
docker-compose up -d
```

3. **Access:**
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

4. **Stop services:**
```bash
docker-compose down
```

---

## Production Deployment

### Option 1: Docker (Recommended)

Use the docker-compose setup with production settings:

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    # ... (same as docker-compose.yml)
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - LOG_LEVEL=WARNING
```

Deploy:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Option 2: Traditional VPS

#### Backend (Ubuntu/Debian)

1. **Install dependencies:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv nginx redis-server
```

2. **Setup application:**
```bash
cd /var/www/souent
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Create systemd service:**
```ini
# /etc/systemd/system/souent.service
[Unit]
Description=Souent Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/souent/backend
Environment="PATH=/var/www/souent/backend/venv/bin"
ExecStart=/var/www/souent/backend/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

4. **Enable and start:**
```bash
sudo systemctl enable souent
sudo systemctl start souent
```

#### Frontend (Nginx)

1. **Build frontend:**
```bash
cd frontend
npm run build
```

2. **Copy to web root:**
```bash
sudo cp -r dist/* /var/www/souent/public/
```

3. **Configure Nginx:**
```nginx
# /etc/nginx/sites-available/souent
server {
    listen 80;
    server_name your-domain.com;
    
    # Frontend
    location / {
        root /var/www/souent/public;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

4. **Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/souent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 3: AWS/GCP/Azure

#### AWS Elastic Beanstalk

1. Install EB CLI:
```bash
pip install awsebcli
```

2. Initialize:
```bash
cd backend
eb init -p python-3.11 souent-backend
```

3. Create environment:
```bash
eb create souent-prod
```

4. Deploy:
```bash
eb deploy
```

#### Google Cloud Run

1. Build container:
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/souent-backend
```

2. Deploy:
```bash
gcloud run deploy souent --image gcr.io/PROJECT_ID/souent-backend --platform managed
```

#### Azure App Service

1. Create resource group:
```bash
az group create --name souent-rg --location eastus
```

2. Create app service plan:
```bash
az appservice plan create --name souent-plan --resource-group souent-rg --sku B1 --is-linux
```

3. Create web app:
```bash
az webapp create --resource-group souent-rg --plan souent-plan --name souent-backend --runtime "PYTHON|3.11"
```

4. Deploy:
```bash
az webapp up --name souent-backend
```

---

## Environment Variables

### Backend (.env)

```bash
# Required
AI_PROVIDER=openai|anthropic
AI_API_KEY=your-api-key-here
AI_MODEL=gpt-4|claude-3-opus-20240229

# Optional
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=generate-random-secret
ALLOWED_ORIGINS=https://yourdomain.com
MEMORY_STORAGE_TYPE=redis
REDIS_URL=redis://localhost:6379/0
ADMIN_API_KEY=your-admin-key
```

### Frontend (.env)

```bash
VITE_API_URL=https://api.yourdomain.com
VITE_APP_NAME=Souent
```

---

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Set strong ADMIN_API_KEY and ADVISORY_API_KEY
- [ ] Enable HTTPS (use Let's Encrypt)
- [ ] Configure CORS properly (ALLOWED_ORIGINS)
- [ ] Set DEBUG=false in production
- [ ] Enable rate limiting
- [ ] Regular security updates
- [ ] Backup canon memory and user data

---

## Monitoring

### Health Checks

Backend health endpoint:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "app_name": "Souent",
  "version": "1.0.0"
}
```

### Logs

Docker:
```bash
docker-compose logs -f backend
```

Systemd:
```bash
journalctl -u souent -f
```

---

## Backup Strategy

### Critical Data

1. **Canon Memory:**
```bash
cp backend/data/canon_memory.json backups/canon_memory_$(date +%Y%m%d).json
```

2. **User Preferences:**
```bash
tar -czf backups/preferences_$(date +%Y%m%d).tar.gz backend/data/user_preferences/
```

3. **Redis (if using):**
```bash
redis-cli SAVE
cp /var/lib/redis/dump.rdb backups/redis_$(date +%Y%m%d).rdb
```

### Automated Backups

Create a cron job:
```bash
# /etc/cron.daily/souent-backup
#!/bin/bash
BACKUP_DIR=/backups/souent
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/souent_$(date +%Y%m%d).tar.gz /var/www/souent/backend/data
# Keep last 30 days
find $BACKUP_DIR -mtime +30 -delete
```

---

## Troubleshooting

### Backend won't start

1. Check logs:
```bash
docker-compose logs backend
# or
journalctl -u souent
```

2. Common issues:
- Missing API key: Set AI_API_KEY in .env
- Port conflict: Change port in docker-compose.yml
- Redis connection: Check REDIS_URL

### Frontend can't connect to backend

1. Check CORS settings in backend .env:
```bash
ALLOWED_ORIGINS=http://localhost:5173
```

2. Check API URL in frontend .env:
```bash
VITE_API_URL=http://localhost:8000
```

### Memory issues

1. Check Redis connection:
```bash
redis-cli ping
```

2. Fallback to file storage:
```bash
MEMORY_STORAGE_TYPE=file
```

### Rate limiting errors

Adjust limits in backend .env:
```bash
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

---

## Scaling

### Horizontal Scaling

1. Load balancer (Nginx):
```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

2. Shared Redis for session state

3. Shared storage for user preferences and canon memory

### Vertical Scaling

Increase resources in docker-compose.yml:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

---

## Support

For issues and questions:
- Email: support@velaplex.systems
- Documentation: /docs
- API Reference: http://localhost:8000/docs
