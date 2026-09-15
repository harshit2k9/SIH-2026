# Render Deployment Configuration Guide

## Problem Diagnosis
Your frontend is making API calls to relative paths (`/api/documents`, `/api/audit-logs`) which are being handled by the frontend nginx. The nginx config proxies these to `$BACKEND_URL:8000`, but this environment variable must be set in Render.

## Required Render Configuration

### 1. Backend Service Settings

#### Environment Variables (Add in Render Dashboard > Backend Service > Environment)
```bash
RENDER=true
ENVIRONMENT=production
DATABASE_URL=<your-render-postgres-connection-string>
CORS_ORIGINS=https://sddms-frontend.onrender.com,https://sddms-backend.onrender.com
MINIO_ROOT_USER=<your-minio-username>
MINIO_ROOT_PASSWORD=<your-minio-password>
```

#### Secret Files (Upload in Render Dashboard > Backend Service > Secret Files)
Upload these files to `/etc/secrets/`:

**private.pem** - RSA Private Key (2048-bit or higher)
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA... (your actual private key content)
-----END RSA PRIVATE KEY-----
```

**public.pem** - RSA Public Key
```
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA... (your actual public key content)
-----END PUBLIC KEY-----
```

⚠️ **CRITICAL**: Ensure PEM files do NOT contain:
- Git merge conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
- Extra whitespace or line breaks
- Any corruption

To regenerate clean keys if needed:
```bash
cd backend/keys
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem
```

Then upload the clean files as Secret Files in Render.

#### Health Check Configuration
- **Health Check Path**: `/health`
- **Liveness Check Path**: `/api/liveness`

---

### 2. Frontend Service Settings

#### Environment Variables (Add in Render Dashboard > Frontend Service > Environment)
```bash
BACKEND_URL=sddms-backend.onrender.com
```

⚠️ **IMPORTANT**: 
- Do NOT include `https://` or `http://` prefix
- Do NOT include the port number
- Use ONLY the hostname: `sddms-backend.onrender.com`

This will make nginx proxy requests to: `http://sddms-backend.onrender.com:8000`

---

## Verification Steps

### 1. Verify Backend is Running
Visit: `https://sddms-backend.onrender.com/health`
Expected response: `{"status": "healthy"}`

### 2. Verify Liveness Endpoint
Visit: `https://sddms-backend.onrender.com/api/liveness`
Expected response: `{"status": "alive"}`

### 3. Verify CORS Headers
The backend should accept requests from `https://sddms-frontend.onrender.com`

### 4. Test API Endpoints Directly
- `https://sddms-backend.onrender.com/api/documents`
- `https://sddms-backend.onrender.com/api/audit-logs`

These may require authentication, but should NOT return 404.

---

## Common Issues & Solutions

### Issue: 404 on /api/documents and /api/audit-logs
**Cause**: Frontend nginx not proxying to backend correctly
**Solution**: 
1. Verify `BACKEND_URL` environment variable is set in frontend service
2. Check frontend logs for nginx startup errors
3. Redeploy frontend after setting the variable

### Issue: JWT Authentication Fails
**Cause**: Corrupted PEM files or wrong paths
**Solution**:
1. Regenerate clean PEM keys without merge conflicts
2. Upload as Secret Files to backend service
3. Verify `RENDER=true` is set so backend uses `/etc/secrets/` path

### Issue: CORS Errors
**Cause**: Backend not allowing frontend origin
**Solution**:
1. Set `CORS_ORIGINS` environment variable in backend
2. Include both frontend and backend URLs: `https://sddms-frontend.onrender.com,https://sddms-backend.onrender.com`

### Issue: Database Connection Errors
**Cause**: Missing or incorrect DATABASE_URL
**Solution**:
1. Get PostgreSQL connection string from Render dashboard
2. Add as `DATABASE_URL` environment variable in backend service

---

## Deployment Order

1. **First**: Deploy backend service with all environment variables and secret files
2. **Verify**: Backend health check passes (`/health` returns 200)
3. **Then**: Deploy frontend service with `BACKEND_URL` environment variable
4. **Verify**: Frontend can access backend APIs

---

## Testing After Deployment

1. Open `https://sddms-frontend.onrender.com`
2. Check browser console for any errors
3. Navigate to Dashboard - should load documents and audit logs
4. If errors persist, check:
   - Browser Network tab for failed requests
   - Render logs for both services
   - Verify environment variables are correctly set

---

## Quick Fix Checklist

- [ ] Backend has `RENDER=true` environment variable
- [ ] Backend has clean `private.pem` and `public.pem` as Secret Files
- [ ] Backend has valid `DATABASE_URL`
- [ ] Backend has `CORS_ORIGINS` including frontend URL
- [ ] Frontend has `BACKEND_URL=sddms-backend.onrender.com` environment variable
- [ ] Backend health check path is `/health`
- [ ] Backend liveness check path is `/api/liveness`
- [ ] Both services are deployed and running
- [ ] No merge conflict markers in any files
