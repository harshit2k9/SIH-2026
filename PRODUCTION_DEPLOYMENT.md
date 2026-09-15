# Production Deployment Configuration

## Overview
This directory contains production-ready deployment configurations for SecureDocs SIH-2026.

## Deployment Options

### 1. Docker Compose (Recommended for Small-Medium Deployments)

**Best for:**
- Development environments
- Small to medium production deployments
- Single-server setups
- Quick prototyping

**Requirements:**
- Docker Engine 20.10+
- Docker Compose v2.0+
- 4GB RAM minimum
- 10GB disk space

**Quick Start:**
```bash
# Using the deployment script
./deploy.sh

# Or manually
docker compose up -d --build
```

### 2. Kubernetes (For Large-Scale Deployments)

**Best for:**
- Enterprise deployments
- High availability requirements
- Auto-scaling needs
- Multi-cluster setups

**See:** `kubernetes/` directory for K8s manifests (to be created)

### 3. Cloud Platform Deployments

#### AWS Deployment
- Use ECS with Fargate for container orchestration
- RDS PostgreSQL for database
- S3 instead of MinIO for object storage
- Elastic Load Balancer for traffic distribution

#### Azure Deployment
- Azure Container Instances or AKS
- Azure Database for PostgreSQL
- Azure Blob Storage
- Azure Load Balancer

#### GCP Deployment
- Google Cloud Run or GKE
- Cloud SQL for PostgreSQL
- Google Cloud Storage
- Cloud Load Balancing

## Pre-Deployment Checklist

### Security
- [ ] Change all default passwords in `.env`
- [ ] Generate new JWT keys (see below)
- [ ] Enable SSL/TLS for all services
- [ ] Configure firewall rules
- [ ] Enable ClamAV scanning
- [ ] Set up network segmentation
- [ ] Review CORS origins
- [ ] Enable audit logging

### Performance
- [ ] Configure PostgreSQL memory settings
- [ ] Set up connection pooling
- [ ] Configure MinIO erasure coding
- [ ] Enable caching layers
- [ ] Set up CDN for static assets

### Monitoring & Logging
- [ ] Configure log aggregation
- [ ] Set up health check alerts
- [ ] Enable metrics collection
- [ ] Configure backup automation
- [ ] Set up disaster recovery plan

### Compliance
- [ ] Review data retention policies
- [ ] Enable encryption at rest
- [ ] Configure access controls
- [ ] Document audit procedures
- [ ] Test backup restoration

## JWT Key Generation (Production)

```bash
cd backend/keys

# Generate secure private key
openssl genrsa -out private.pem 4096

# Extract public key
openssl rsa -in private.pem -pubout -out public.pem

# Set secure permissions
chmod 600 private.pem
chmod 644 public.pem

# Verify keys
openssl rsa -in private.pem -check
openssl rsa -in public.pem -pubin -text
```

## Environment Configuration

### Development (.env.development)
```env
ENVIRONMENT=development
POSTGRES_PASSWORD=dev_password_change_in_prod
MINIO_ROOT_PASSWORD=dev_minio_password
SIH26_SESSION_SECRET=dev_secret_change_in_prod
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
ENABLE_AV_SCAN=false
LOG_LEVEL=DEBUG
```

### Production (.env.production)
```env
ENVIRONMENT=production
POSTGRES_PASSWORD=<STRONG_RANDOM_PASSWORD>
MINIO_ROOT_PASSWORD=<STRONG_RANDOM_PASSWORD>
SIH26_SESSION_SECRET=<STRONG_RANDOM_SECRET_64_CHARS>
CORS_ORIGINS=https://yourdomain.com
ENABLE_AV_SCAN=true
LOG_LEVEL=INFO
JWT_PRIVATE_KEY_PATH=/app/keys/private.pem
JWT_PUBLIC_KEY_PATH=/app/keys/public.pem
```

## Scaling Guidelines

### Horizontal Scaling
- Backend: Stateless, can scale horizontally easily
- Frontend: Serve static files via CDN
- PostgreSQL: Read replicas for read-heavy workloads
- MinIO: Distributed mode for high availability

### Vertical Scaling
- PostgreSQL: Increase shared_buffers, effective_cache_size
- MinIO: Add more drives, enable erasure coding
- Backend: Increase worker threads, memory limits

### Recommended Resource Limits

#### PostgreSQL
```yaml
resources:
  limits:
    cpu: "4"
    memory: "8Gi"
  requests:
    cpu: "2"
    memory: "4Gi"
```

#### Backend
```yaml
resources:
  limits:
    cpu: "2"
    memory: "4Gi"
  requests:
    cpu: "1"
    memory: "2Gi"
```

#### MinIO
```yaml
resources:
  limits:
    cpu: "4"
    memory: "8Gi"
  requests:
    cpu: "2"
    memory: "4Gi"
```

## Backup Strategy

### Automated Backups

Create a cron job for daily backups:

```bash
#!/bin/bash
# /usr/local/bin/sddms-backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/sddms/$DATE"
mkdir -p $BACKUP_DIR

# Database backup
docker compose exec postgres pg_dump -U sddms_user sddms_db > $BACKUP_DIR/database.sql

# MinIO backup
tar -czf $BACKUP_DIR/minio.tar.gz -C /var/lib/docker/volumes/sddms_miniodata/_data .

# Keep last 7 days
find /backups/sddms -type d -mtime +7 -exec rm -rf {} \;
```

### Disaster Recovery

1. **Restore Database:**
```bash
cat backup_YYYYMMDD_HHMMSS.sql | docker compose exec -T postgres psql -U sddms_user -d sddms_db
```

2. **Restore MinIO Data:**
```bash
tar -xzf minio_backup.tar.gz -C /var/lib/docker/volumes/sddms_miniodata/_data
docker compose restart minio
```

3. **Full System Restore:**
```bash
docker compose down -v
docker compose up -d postgres
# Wait for DB init, restore backup
docker compose up -d minio
# Restore MinIO data
docker compose up -d backend frontend
```

## Monitoring Setup

### Health Endpoints
- Backend: `http://localhost:8000/health`
- PostgreSQL: `pg_isready` command
- MinIO: `http://localhost:9000/minio/health/live`
- ClamAV: TCP port 3310

### Metrics to Monitor
- API response times
- Database connection pool usage
- Disk space utilization
- Memory usage per service
- Request rates and error rates
- Virus scan queue length

### Alerting Thresholds
- CPU usage > 80% for 5 minutes
- Memory usage > 85% for 5 minutes
- Disk usage > 90%
- API error rate > 5%
- Database connections > 80% of max
- Backup failures

## Troubleshooting

### Common Issues

**Backend won't start:**
```bash
docker compose logs backend
# Check database connectivity
docker compose logs postgres
```

**Database connection errors:**
```bash
docker compose exec postgres pg_isready -U sddms_user -d sddms_db
docker compose restart postgres
```

**MinIO bucket issues:**
```bash
docker compose restart minio
docker compose logs minio
```

**ClamAV not ready:**
```bash
# Wait for initial virus DB download (2-3 minutes)
docker compose logs clamav
```

### Log Analysis

View all logs:
```bash
docker compose logs -f
```

Search for errors:
```bash
docker compose logs | grep -i error
```

## Support & Maintenance

### Regular Maintenance Tasks
- Weekly: Check disk space, review logs
- Monthly: Update virus definitions, rotate logs
- Quarterly: Security updates, performance review
- Annually: Full security audit, capacity planning

### Getting Help
- Documentation: See DEPLOYMENT.md
- GitHub Issues: https://github.com/harshit2k9/SIH-2026/issues
- Emergency Contact: See your organization's on-call rotation

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-09-15 | Initial production release |

## License

See LICENSE file for terms and conditions.
