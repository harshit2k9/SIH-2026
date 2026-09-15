# SecureDocs Deployment - Quick Reference

## 🚀 One-Command Deployment

```bash
./deploy.sh
```

Or using Make:
```bash
make deploy
```

## 📋 Essential Commands

### Start All Services
```bash
docker compose up -d
# or
make up
```

### Stop All Services
```bash
docker compose down
# or
make down
```

### View Logs
```bash
docker compose logs -f
# or
make logs
```

### Check Health
```bash
make health
```

## 🌐 Access URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | - |
| Backend API | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| MinIO Console | http://localhost:9001 | minio_admin / minio_secure_password_2025 |
| PostgreSQL | localhost:5432 | sddms_user / sddms_secure_password_2025 |

## 🔧 Common Tasks

### Restart a Service
```bash
docker compose restart backend
```

### Rebuild After Code Changes
```bash
docker compose up -d --build
```

### Full Reset (Clean + Rebuild)
```bash
make reset
```

### Database Backup
```bash
make backup
```

### Open Database Shell
```bash
make shell-db
```

### Open Backend Shell
```bash
make shell-backend
```

## 🛠️ Troubleshooting

### Backend Not Starting
```bash
docker compose logs backend
docker compose restart backend
```

### Database Connection Issues
```bash
docker compose logs postgres
docker compose restart postgres
```

### Check All Services Status
```bash
docker compose ps
# or
make status
```

## 📖 Documentation

- **Full Deployment Guide**: `DEPLOYMENT.md`
- **Production Setup**: `PRODUCTION_DEPLOYMENT.md`
- **Main README**: `README.md`

## 💡 Tips

1. **First Run**: Initial startup may take 3-5 minutes due to image downloads and database initialization
2. **ClamAV**: Takes 2-3 minutes for initial virus database download
3. **Port Conflicts**: Ensure ports 5173, 8000, 5432, 9000, 9001 are available
4. **Memory**: Allocate at least 4GB RAM to Docker for smooth operation

## 🆘 Need Help?

```bash
make help
```

Or visit: https://github.com/harshit2k9/SIH-2026/issues
