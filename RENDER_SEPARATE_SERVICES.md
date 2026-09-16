# Render Deployment Guide - Separate Services

This guide explains how to deploy the application as **separate frontend and backend services** on Render.

## Architecture

- **Backend Service**: FastAPI API server with PostgreSQL database
- **Frontend Service**: Static React/Vite app served via Nginx
- **Database**: Render PostgreSQL (managed service)

---

## Backend Service Setup

### 1. Create Backend Service on Render

1. Go to Render Dashboard → New → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `sddms-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**: 
     ```bash
     uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2
     ```
   - **Port**: `8000`
   - **Instance Type**: Free or Starter ($7/mo)

### 2. Environment Variables (Backend)

Add these in Render Dashboard → Environment:

```bash
# Database (Render will auto-inject DATABASE_URL when you attach PostgreSQL)
DATABASE_URL=<auto-injected by Render>

# JWT Keys (generate once and store as secrets)
JWT_PRIVATE_KEY_PATH=keys/private.pem
JWT_PUBLIC_KEY_PATH=keys/public.pem

# Generate JWT keys locally and upload as files, OR use these env vars:
JWT_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n..."
JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\n..."

# Security
SIH26_SESSION_SECRET=<generate-random-string-32-chars>

# MinIO (if using external storage)
MINIO_ENDPOINT_URL=https://your-minio-endpoint
MINIO_ROOT_USER=your-user
MINIO_ROOT_PASSWORD=your-password
MINIO_BUCKET=legal-documents
MINIO_USE_SSL=True
MINIO_ENABLE_SSE=True

# AV Scanning (optional)
ENABLE_AV_SCAN=False
CLAMAV_HOST=localhost
CLAMAV_PORT=3310

# CORS (add your frontend URL)
CORS_ORIGINS=https://sddms-frontend.onrender.com,https://your-domain.com

# Other settings
JWT_AUDIENCE=sddms-api
JWT_ISSUER=sddms-auth-service
MAX_FILE_SIZE_BYTES=2048576000
ENVIRONMENT=production
```

### 3. Attach PostgreSQL Database

1. In Render Dashboard → New → **PostgreSQL**
2. Configure:
   - **Name**: `sddms-db`
   - **Database Name**: `sddms`
   - **User**: `sddms_user`
   - **Password**: `<generate-strong-password>`
3. After creation, click **Connect** → **Add Service Connection** → Select your backend service
4. Render will automatically inject `DATABASE_URL` environment variable

### 4. Initialize Database

The backend will run migrations automatically on startup via `migrate_db.py`.

---

## Frontend Service Setup

### 1. Create Frontend Service on Render

1. Go to Render Dashboard → New → **Static Site**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `sddms-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: 
     ```bash
     npm install && npm run build
     ```
   - **Publish Directory**: `dist`

### 2. Environment Variables (Frontend)

Add these in Render Dashboard → Environment:

```bash
# Backend API URL (replace with your actual backend URL)
VITE_API_URL=https://sddms-backend.onrender.com
```

### 3. Update Frontend Configuration

Ensure your `frontend/.env.production` or Vite config uses the environment variable:

```typescript
// vite.config.ts
export default defineConfig({
  // ... other config
  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL)
  }
})
```

---

## Alternative: Docker Deployment

If you prefer Docker deployment:

### Backend Dockerfile (Already Updated)

The `backend/Dockerfile` now:
- ✅ Removes Node.js dependency (no frontend build)
- ✅ Generates JWT keys automatically if missing
- ✅ Runs database migrations on build
- ✅ Optimized for backend-only operation

### Frontend Dockerfile (Use Dockerfile.prod)

```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN apk add --no-cache gettext
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["sh", "-c", "envsubst '${BACKEND_URL}' < /etc/nginx/conf.d/default.conf > /etc/nginx/conf.d/default.conf.tmp && mv /etc/nginx/conf.d/default.conf.tmp /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
```

### Render Docker Configuration

**Backend:**
- **Docker Context**: `.`
- **Dockerfile Path**: `backend/Dockerfile`

**Frontend:**
- **Docker Context**: `./frontend`
- **Dockerfile Path**: `Dockerfile.prod`
- **Environment**: `BACKEND_URL=https://sddms-backend.onrender.com`

---

## Testing Deployment

### 1. Backend Health Check
```bash
curl https://sddms-backend.onrender.com/health
# Expected: {"status":"healthy"}
```

### 2. Frontend Load
Visit: `https://sddms-frontend.onrender.com`

### 3. API Integration
Check browser console for API calls to ensure they're hitting the correct backend URL.

---

## Troubleshooting

### Common Issues

**1. Database Connection Errors**
- Ensure PostgreSQL is attached to backend service
- Check `DATABASE_URL` is set correctly
- Verify database user has proper permissions

**2. CORS Errors**
- Add frontend URL to `CORS_ORIGINS` in backend
- Format: `https://sddms-frontend.onrender.com`

**3. JWT Key Errors**
- Either upload key files via Render Dashboard → Files
- Or set `JWT_PRIVATE_KEY` and `JWT_PUBLIC_KEY` as environment variables

**4. Frontend Can't Connect to Backend**
- Verify `VITE_API_URL` points to correct backend URL
- Check backend is running (not in sleep mode on free tier)

**5. Build Failures**
- Clear cache: Render Dashboard → Settings → Clear Build Cache
- Check logs for specific error messages

---

## Cost Optimization

- **Free Tier**: Backend may sleep after 15 minutes of inactivity
- **Starter Plan** ($7/mo): Prevents sleep, faster instances
- **Database**: Free tier available with 1GB storage

---

## Security Best Practices

1. ✅ Use Render Secrets for sensitive values
2. ✅ Enable HTTPS (automatic on Render)
3. ✅ Set strong `SIH26_SESSION_SECRET`
4. ✅ Use environment-specific CORS origins
5. ✅ Enable MinIO SSE for encrypted storage
6. ✅ Regular database backups (Render automatic)

---

## Monitoring

- **Logs**: Render Dashboard → Logs tab
- **Metrics**: Render Dashboard → Metrics tab
- **Alerts**: Configure via Render Dashboard → Alerts

---

## Next Steps

1. Deploy backend service
2. Create and attach PostgreSQL
3. Deploy frontend service
4. Test end-to-end functionality
5. Configure custom domain (optional)
6. Set up monitoring and alerts

For production deployments, consider upgrading to paid tiers for better performance and reliability.
