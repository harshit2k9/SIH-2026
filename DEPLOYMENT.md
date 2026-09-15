# SecureDocs SIH-2026 Deployment Guide

## Prerequisites
- Docker Engine 20.10+ or Docker Desktop
- Docker Compose v2.0+ (or docker-compose v1.29+)
- At least 4GB RAM available
- 10GB free disk space

## Quick Start Deployment

### Option 1: Using Docker Compose v2 (Recommended)
```bash
# Clone the repository
git clone https://github.com/harshit2k9/SIH-2026.git
cd SIH-2026

# Start all services
docker compose up -d --build

# View logs
docker compose logs -f
```

### Option 2: Using Docker Compose v1
```bash
# Clone the repository
git clone https://github.com/harshit2k9/SIH-2026.git
cd SIH-2026

# Start all services
docker-compose up -d --build

# View logs
docker-compose logs -f
```

## Services Overview

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 5173 | React + TypeScript UI |
| Backend API | 8000 | FastAPI REST API |
| PostgreSQL | 5432 | Primary database |
| MinIO | 9000/9001 | S3-compatible object storage |
| ClamAV | 3310 | Antivirus scanner |

## Access URLs

After successful deployment:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (login: minio_admin / minio_secure_password_2025)

## Health Checks

Verify all services are running:
```bash
docker compose ps
```

Check individual service health:
```bash
# Backend API
curl http://localhost:8000/health

# PostgreSQL
docker compose exec postgres pg_isready -U sddms_user -d sddms_db

# MinIO
curl http://localhost:9000/minio/health/live

# ClamAV
echo PING | nc localhost 3310
```

## Configuration

### Environment Variables (.env file)

Edit the `.env` file before deployment for production:

```env
# PostgreSQL Configuration
POSTGRES_USER=sddms_user
POSTGRES_PASSWORD=CHANGE_IN_PRODUCTION
POSTGRES_DB=sddms_db

# MinIO Configuration
MINIO_ROOT_USER=minio_admin
MINIO_ROOT_PASSWORD=CHANGE_IN_PRODUCTION
MINIO_BUCKET=legal-documents

# JWT Configuration
JWT_PRIVATE_KEY_PATH=/app/keys/private.pem
JWT_PUBLIC_KEY_PATH=/app/keys/public.pem

# Security
SIH26_SESSION_SECRET=CHANGE_IN_PRODUCTION
CORS_ORIGINS=https://yourdomain.com
```

### Production Security Checklist

- [ ] Change all default passwords in `.env`
- [ ] Generate new JWT keys (see below)
- [ ] Enable SSL for MinIO
- [ ] Enable ClamAV scanning
- [ ] Restrict CORS origins
- [ ] Use secure network configuration
- [ ] Enable firewall rules
- [ ] Set up backup strategy

## Generate JWT Keys (Production)

```bash
cd backend/keys

# Generate private key
openssl genrsa -out private.pem 2048

# Generate public key
openssl rsa -in private.pem -pubout -out public.pem

# Set permissions
chmod 600 private.pem
chmod 644 public.pem
```

## Database Initialization

The database is automatically initialized on first run with:
1. Schema from `database/SIH_DATABASE.sql`
2. Test data from `database/test_database.sql`

To reset the database:
```bash
docker compose down -v
docker compose up -d postgres
# Wait for initialization, then start other services
docker compose up -d backend frontend
```

## Managing Services

### Start all services
```bash
docker compose up -d
```

### Stop all services
```bash
docker compose down
```

### Stop and remove volumes (complete reset)
```bash
docker compose down -v
```

### View logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
```

### Restart a service
```bash
docker compose restart backend
```

### Update and redeploy
```bash
git pull
docker compose up -d --build
```

## Backup Strategy

### Database Backup
```bash
docker compose exec postgres pg_dump -U sddms_user sddms_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### MinIO Data Backup
```bash
tar -czf minio_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /var/lib/docker/volumes/sddms_miniodata/_data .
```

### Restore Database
```bash
cat backup_YYYYMMDD_HHMMSS.sql | docker compose exec -T postgres psql -U sddms_user -d sddms_db
```

## Troubleshooting

### Backend fails to start
```bash
# Check logs
docker compose logs backend

# Verify database is ready
docker compose logs postgres

# Restart backend
docker compose restart backend
```

### Database connection issues
```bash
# Check database health
docker compose exec postgres pg_isready -U sddms_user -d sddms_db

# Reset database volume
docker compose down -v
docker compose up -d postgres
```

### MinIO bucket not found
The application creates the bucket automatically on first run. If issues persist:
```bash
docker compose restart minio backend
```

### ClamAV not ready
ClamAV takes 2-3 minutes for initial virus database download:
```bash
docker compose logs clamav
# Wait until you see "ClamAV daemon process started and listening"
```

## Performance Tuning

### Increase PostgreSQL memory
Edit `docker-compose.yml`:
```yaml
environment:
  POSTGRES_SHARED_BUFFERS: 256MB
  POSTGRES_EFFECTIVE_CACHE_SIZE: 768MB
```

### MinIO Performance
For production, consider:
- Using SSD storage
- Enabling erasure coding
- Configuring lifecycle policies

## Monitoring

### Resource usage
```bash
docker compose stats
```

### Database connections
```bash
docker compose exec postgres psql -U sddms_user -d sddms_db -c "SELECT count(*) FROM pg_stat_activity;"
```

## Support

For issues and feature requests:
- GitHub Issues: https://github.com/harshit2k9/SIH-2026/issues
- Documentation: See README.md

## License

See LICENSE file for terms and conditions.
