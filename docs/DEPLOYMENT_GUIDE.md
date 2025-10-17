# Deployment Guide - Aura Sentient Interactive Studio

## Overview

This guide covers deploying the Aura Sentient Interactive Studio in various environments, from local development to production cloud deployment.

## Quick Start (Development)

```bash
# 1. Clone the repository
git clone https://github.com/elliotttmiller/aura.git
cd aura

# 2. Set up environment
cp .env.example .env
# Edit .env with your configuration

# 3. Install backend dependencies
pip install -r requirements.txt

# 4. Install frontend dependencies
cd frontend/static
npm install

# 5. Start the application
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload --port 8001

# Terminal 2 - Frontend
cd frontend/static
npm run dev
```

Access the application at http://localhost:5173

## Docker Deployment

### Basic Docker Deployment

```bash
# Build the image
docker build -t aura-studio:latest .

# Run the container
docker run -p 8001:8001 \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  aura-studio:latest
```

### Docker Compose Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# With database
docker-compose --profile with-db up -d

# With nginx (production)
docker-compose --profile production up -d
```

## Production Deployment

### Prerequisites

- Docker and Docker Compose
- Domain name with SSL certificate
- 4GB+ RAM recommended
- (Optional) Redis for caching
- (Optional) PostgreSQL for persistent storage

### Step 1: Environment Configuration

```bash
# Create production .env
cp .env.example .env

# Configure production settings
nano .env
```

Key production settings:
```bash
ENVIRONMENT=production
DEBUG_MODE=false
LOG_LEVEL=INFO
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8001

# Security
SESSION_TIMEOUT_MINUTES=60
RATE_LIMIT_REQUESTS_PER_MINUTE=60

# Database (optional)
DATABASE_URL=postgresql://user:pass@db:5432/aura

# Redis (recommended)
REDIS_URL=redis://redis:6379/0
```

### Step 2: SSL/TLS Setup

For production with HTTPS:

```bash
# Create SSL directory
mkdir -p ssl

# Add your SSL certificates
# ssl/fullchain.pem
# ssl/privkey.pem

# Or use Let's Encrypt (recommended)
certbot certonly --standalone -d your-domain.com
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/
```

### Step 3: Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream aura_backend {
        server aura-app:8001;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        client_max_body_size 50M;

        location / {
            proxy_pass http://aura_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # Serve static files directly
        location /static/ {
            alias /app/frontend/static/dist/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Health check endpoint
        location /health {
            access_log off;
            proxy_pass http://aura_backend/health;
        }
    }
}
```

### Step 4: Deploy

```bash
# Build and start services
docker-compose --profile production up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f aura-app

# Test health endpoint
curl https://your-domain.com/health
```

## Cloud Platform Deployment

### AWS Elastic Container Service (ECS)

1. **Create ECR Repository**
```bash
aws ecr create-repository --repository-name aura-studio
```

2. **Build and Push Image**
```bash
# Build for multi-architecture
docker buildx build --platform linux/amd64,linux/arm64 -t aura-studio:latest .

# Tag and push
docker tag aura-studio:latest YOUR_ECR_URL/aura-studio:latest
docker push YOUR_ECR_URL/aura-studio:latest
```

3. **Create Task Definition**
```json
{
  "family": "aura-studio",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "aura-app",
      "image": "YOUR_ECR_URL/aura-studio:latest",
      "portMappings": [
        {
          "containerPort": 8001,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"},
        {"name": "LOG_LEVEL", "value": "INFO"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/aura-studio",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Run

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT/aura-studio

# Deploy to Cloud Run
gcloud run deploy aura-studio \
  --image gcr.io/YOUR_PROJECT/aura-studio \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2
```

### Azure Container Instances

```bash
# Create resource group
az group create --name aura-rg --location eastus

# Create container registry
az acr create --resource-group aura-rg --name auraregistry --sku Basic

# Build and push
az acr build --registry auraregistry --image aura-studio:latest .

# Deploy
az container create \
  --resource-group aura-rg \
  --name aura-studio \
  --image auraregistry.azurecr.io/aura-studio:latest \
  --cpu 2 \
  --memory 4 \
  --registry-login-server auraregistry.azurecr.io \
  --ip-address Public \
  --ports 8001
```

## Kubernetes Deployment

### Basic Kubernetes Manifest

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aura-studio
spec:
  replicas: 2
  selector:
    matchLabels:
      app: aura-studio
  template:
    metadata:
      labels:
        app: aura-studio
    spec:
      containers:
      - name: aura-app
        image: aura-studio:latest
        ports:
        - containerPort: 8001
        env:
        - name: ENVIRONMENT
          value: "production"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: aura-studio-service
spec:
  selector:
    app: aura-studio
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8001
  type: LoadBalancer
```

Deploy:
```bash
kubectl apply -f deployment.yaml
```

## Monitoring and Maintenance

### Health Checks

```bash
# Check application health
curl http://localhost:8001/health

# Expected response:
{
  "status": "healthy",
  "services": {
    "lm_studio": "healthy",
    "blender": "healthy",
    "disk": "healthy"
  }
}
```

### Logs

```bash
# Docker Compose
docker-compose logs -f aura-app

# Docker
docker logs -f aura-studio

# Kubernetes
kubectl logs -f deployment/aura-studio
```

### Backup

```bash
# Backup output files
tar -czf aura-backup-$(date +%Y%m%d).tar.gz output/ models/ logs/

# Backup to S3
aws s3 cp aura-backup-$(date +%Y%m%d).tar.gz s3://your-bucket/backups/
```

### Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Zero-downtime rolling update (Kubernetes)
kubectl set image deployment/aura-studio aura-app=aura-studio:new-version
```

## Scaling

### Horizontal Scaling

```bash
# Docker Compose (manual)
docker-compose up -d --scale aura-app=3

# Kubernetes
kubectl scale deployment aura-studio --replicas=5

# Auto-scaling (Kubernetes)
kubectl autoscale deployment aura-studio --min=2 --max=10 --cpu-percent=70
```

### Vertical Scaling

Adjust resources in docker-compose.yml:
```yaml
services:
  aura-app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## Troubleshooting

### Common Issues

1. **Container won't start**
```bash
# Check logs
docker-compose logs aura-app

# Common causes:
# - Missing environment variables
# - Port conflicts
# - Missing volumes
```

2. **High memory usage**
```bash
# Monitor usage
docker stats aura-studio

# Solutions:
# - Increase memory limit
# - Enable Redis caching
# - Reduce concurrent requests
```

3. **Slow AI responses**
```bash
# Check LM Studio connection
curl http://localhost:1234/v1/models

# Solutions:
# - Use faster model
# - Increase timeout
# - Add Redis caching
```

### Debug Mode

Enable debug mode temporarily:
```bash
docker-compose stop aura-app
docker-compose run --rm aura-app \
  -e DEBUG_MODE=true \
  -e LOG_LEVEL=DEBUG \
  uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

## Security Best Practices

1. **Use HTTPS in production**
   - Always use SSL/TLS certificates
   - Redirect HTTP to HTTPS

2. **Secure environment variables**
   - Use Docker secrets or vault
   - Never commit .env files

3. **Rate limiting**
   - Configure appropriate rate limits
   - Use API keys for authentication

4. **Regular updates**
   - Keep dependencies updated
   - Monitor security advisories

5. **Network security**
   - Use firewall rules
   - Restrict access to admin endpoints

## Performance Optimization

1. **Enable caching**
   - Use Redis for session storage
   - Cache AI responses

2. **CDN for static assets**
   - Serve frontend via CDN
   - Enable gzip compression

3. **Database connection pooling**
   - Configure appropriate pool sizes
   - Use read replicas for scaling

4. **Load balancing**
   - Use nginx or cloud load balancer
   - Distribute traffic across instances

## Support

For issues and questions:
- GitHub Issues: https://github.com/elliotttmiller/aura/issues
- Documentation: See README.md and other guides

---

**Last Updated**: October 17, 2025
**Version**: 1.0.0
