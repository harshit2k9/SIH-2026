# Render Deployment Guide - SDDMS

## Critical Fixes Applied

### 1. JWT Key Path Configuration
The backend now automatically detects Render environment and uses `/etc/secrets/` for JWT keys.

**Backend (`config.py`):**
- Automatically uses `/etc/secrets/private.pem` and `/etc/secrets/public.pem` when `RENDER=true`
- Falls back to `keys/` folder for local development

### 2. Frontend-Backend Communication
The frontend nginx now proxies to a configurable backend URL.

**Frontend (`nginx.conf` & `Dockerfile.prod`):**
- Uses `BACKEND_URL` environment variable for API proxying
- Supports environment variable substitution at runtime

---

## Render Setup Instructions

### Backend Service Configuration

#### 1. Environment Variables (Set in Render Dashboard)
```
RENDER=true
ENVIRONMENT=production
DATABASE_URL=<your-render-postgres-url>
CORS_ORIGINS=https://sddms-frontend.onrender.com,https://sddms-backend.onrender.com
JWT_ALGORITHM=RS256
JWT_AUDIENCE=sddms-api
JWT_ISSUER=sddms-auth-service

# MinIO Configuration (if using external S3)
MINIO_ENDPOINT_URL=<your-s3-endpoint>
MINIO_ROOT_USER=<your-access-key>
MINIO_ROOT_PASSWORD=<your-secret-key>
MINIO_BUCKET=legal-documents
MINIO_USE_SSL=true

# Disable ClamAV for free tier
ENABLE_AV_SCAN=false
CLAMAV_HOST=localhost
CLAMAV_PORT=3310
```

#### 2. Secret Files (Upload in Render Dashboard → Secret Files)
Upload these TWO files to your **backend service**:

**File 1: `private.pem`**
```
-----BEGIN PRIVATE KEY-----
<your-clean-private-key-without-conflict-markers>
-----END PRIVATE KEY-----
```

**File 2: `public.pem`**
```
-----BEGIN PUBLIC KEY-----
<your-clean-public-key>
-----END PUBLIC KEY-----
```

⚠️ **CRITICAL**: Ensure NO merge conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) in the keys!

To regenerate clean keys locally:
```bash
cd backend/keys
rm private.pem public.pem
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem
```

Then upload the clean files to Render Secret Files.

#### 3. Health Check Configuration
- **Health Check Path**: `/health`
- **Port**: 8000

#### 4. Liveness Check (for Render uptime monitoring)
- **Path**: `/api/liveness`
- This endpoint returns `{"status": "alive"}`

---

### Frontend Service Configuration

#### 1. Environment Variables (Set in Render Dashboard)
```
BACKEND_URL=sddms-backend.onrender.com
```

⚠️ **CRITICAL**: Set `BACKEND_URL` to your actual backend service URL (without https://)

#### 2. Build Settings
- **Build Command**: `npm install && npm run build`
- **Start Command**: Already defined in Dockerfile

#### 3. Docker Context
- Set to `frontend/` directory
- Use `Dockerfile.prod`

---

## Common Issues & Solutions

### Issue 1: 404 on /api/documents and /api/audit-logs
**Cause**: Frontend calling itself instead of backend

**Solution**: 
- Set `BACKEND_URL` environment variable in frontend service
- Value should be: `<your-backend-service-name>.onrender.com`

### Issue 2: JWT Authentication Fails
**Cause**: Corrupted PEM files with merge conflict markers

**Solution**:
1. Regenerate clean keys locally
2. Delete old secret files from Render
3. Upload fresh keys without any conflict markers

### Issue 3: CORS Errors
**Cause**: Missing or incorrect CORS_ORIGINS

**Solution**:
Set in backend environment variables:
```
CORS_ORIGINS=https://sddms-frontend.onrender.com,https://sddms-backend.onrender.com
```

### Issue 4: Database Connection Fails
**Cause**: Wrong DATABASE_URL format

**Solution**:
Use the full connection string from Render Postgres dashboard:
```
postgresql://user:password@hostname:port/database
```

---

## Verification Steps

After deployment:

1. **Test Backend Health**: 
   ```
   GET https://sddms-backend.onrender.com/health
   Expected: {"status": "healthy"}
   ```

2. **Test Liveness Endpoint**:
   ```
   GET https://sddms-backend.onrender.com/api/liveness
   Expected: {"status": "alive"}
   ```

3. **Test Frontend Loading**:
   ```
   GET https://sddms-frontend.onrender.com
   Should load React app without console errors
   ```

4. **Test API Calls from Browser Console**:
   Open DevTools → Console and verify no 404 errors for:
   - `/api/documents`
   - `/api/audit-logs`
   - `/api/liveness`

---

## File Locations Reference

| File | Local Path | Render Location |
|------|-----------|-----------------|
| Private Key | `backend/keys/private.pem` | `/etc/secrets/private.pem` |
| Public Key | `backend/keys/public.pem` | `/etc/secrets/public.pem` |
| Backend Config | `backend/config.py` | Auto-detects Render |
| Frontend Proxy | `frontend/nginx.conf` | Uses BACKEND_URL env var |

---

## Quick Deploy Checklist

- [ ] Regenerate clean JWT keys (no merge conflicts)
- [ ] Upload `private.pem` to Render backend Secret Files
- [ ] Upload `public.pem` to Render backend Secret Files
- [ ] Set `RENDER=true` in backend environment variables
- [ ] Set `DATABASE_URL` in backend environment variables
- [ ] Set `CORS_ORIGINS` in backend environment variables
- [ ] Set `BACKEND_URL` in frontend environment variables
- [ ] Configure backend health check path: `/health`
- [ ] Configure liveness check path: `/api/liveness`
- [ ] Rebuild and redeploy both services

---

## Architecture Note

On Render, the services are separate:
- **Frontend**: Static files served by nginx, proxies API calls to backend
- **Backend**: FastAPI application with PostgreSQL database

The frontend nginx uses `BACKEND_URL` to know where to proxy `/api/*` requests.

Example flow:
```
User → Frontend (sddms-frontend.onrender.com)
         ↓ (proxies /api/* to)
Backend (sddms-backend.onrender.com)
         ↓ (queries)
PostgreSQL (Render managed database)
```
