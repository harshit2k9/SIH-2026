# Production Deployment Guide - SecureDocs SIH-2026

## 🚀 Best Free Deployment Options for Your Prototype

### **Option 1: Render.com (RECOMMENDED)**
**Best for**: Full-stack apps with database
- ✅ Free PostgreSQL database (90 days, then $7/month)
- ✅ Free web services (750 hours/month)
- ✅ Automatic HTTPS/SSL
- ✅ Custom domain support
- ✅ Easy GitHub integration

**Limitations**: 
- Database becomes paid after 90 days
- Services spin down after 15 minutes of inactivity (free tier)

---

### **Option 2: Railway.app**
**Best for**: Quick prototyping
- ✅ $5 free credit monthly
- ✅ PostgreSQL included
- ✅ One-click deploys from GitHub
- ✅ Custom domains

**Limitations**: 
- Usage-based pricing after free credits

---

### **Option 3: GitHub Pages + Render (FRONTEND ONLY - RECOMMENDED FOR PROTOTYPES)**
**Best for**: Displaying prototypes completely FREE
- ✅ Frontend: GitHub Pages (100% free forever)
- ✅ Backend: Render free tier
- ✅ No database needed if using mock data
- ✅ Perfect for demos and prototypes

---

### **Option 4: Vercel + Neon**
**Best for**: Modern frontend with serverless backend
- ✅ Frontend: Vercel (unlimited free projects)
- ✅ Database: Neon (free PostgreSQL, serverless)
- ✅ Backend: Vercel Serverless Functions or Render
- ✅ Best performance and DX

---

## 📋 Recommended Deployment Strategy for Your Prototype

### For DEMO/PROTOTYPE Purposes (100% FREE):

```
┌─────────────────────────────────────────────────────┐
│  FRONTEND (React/Vite)                              │
│  → Deploy to: GitHub Pages / Vercel / Netlify      │
│  → Cost: FREE forever                               │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│  BACKEND (FastAPI)                                  │
│  → Deploy to: Render.com free tier                  │
│  → Cost: FREE (750 hours/month)                     │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│  DATABASE                                           │
│  → Option A: Render PostgreSQL (90 days free)       │
│  → Option B: Neon.tech (FREE forever, serverless)   │
│  → Option C: Supabase (FREE 500MB)                  │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│  FILE STORAGE                                       │
│  → Option A: Cloudinary (FREE 25GB)                 │
│  → Option B: Backblaze B2 (FREE 10GB)               │
│  → Option C: Keep MinIO on Render volume            │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Step-by-Step Deployment Instructions

### **Option A: Simplest - Frontend Only Demo (GitHub Pages)**

If you just want to **display your prototype UI**:

#### Step 1: Build Frontend for Production
```bash
cd frontend
npm run build
```

#### Step 2: Deploy to GitHub Pages
```bash
# Install gh-pages
npm install --save-dev gh-pages

# Add to package.json scripts:
# "predeploy": "npm run build",
# "deploy": "gh-pages -d dist"

# Deploy
npm run deploy
```

#### Step 3: Configure GitHub Pages
1. Go to your repo Settings → Pages
2. Source: Deploy from branch → `gh-pages`
3. Your site will be live at: `https://yourusername.github.io/SIH-2026/`

**Note**: You'll need to update `VITE_API_URL` to point to your deployed backend.

---

### **Option B: Full Stack on Render.com**

#### Step 1: Prepare Your Repository
Ensure your code is pushed to GitHub with proper structure.

#### Step 2: Deploy Database (Neon.tech - FREE)
1. Go to https://neon.tech
2. Sign up with GitHub
3. Create new project → Get connection string
4. Example: `postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/dbname`

#### Step 3: Deploy Backend to Render
1. Go to https://render.com
2. New → Web Service
3. Connect your GitHub repo
4. Configuration:
   ```
   Name: sddms-backend
   Region: Singapore (closest to India)
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
   ```
5. Environment Variables:
   ```
   DATABASE_URL=<your-neon-connection-string>
   JWT_PRIVATE_KEY_PATH=/app/keys/private.pem
   JWT_PUBLIC_KEY_PATH=/app/keys/public.pem
   CORS_ORIGINS=https://your-frontend.vercel.app,https://yourdomain.com
   ENVIRONMENT=production
   SIH26_SESSION_SECRET=<generate-new-secret>
   MINIO_ENDPOINT_URL=<cloudinary-or-backblaze-url>
   ENABLE_AV_SCAN=false  # Disable for free tier
   ```

#### Step 4: Deploy Frontend to Vercel
1. Go to https://vercel.com
2. Import your GitHub repo
3. Framework Preset: Vite
4. Root Directory: `frontend`
5. Environment Variables:
   ```
   VITE_API_URL=https://sddms-backend.onrender.com
   ```
6. Deploy!

---

### **Option C: Docker-Based Deployment (Render/Railway)**

Use the existing `docker-compose.yml` with modifications:

#### Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: ${DATABASE_URL}
      CORS_ORIGINS: ${CORS_ORIGINS}
      ENVIRONMENT: production
    ports:
      - "8000:8000"
    volumes:
      - ./backend/keys:/app/keys:ro
      - uploads:/app/uploads
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    environment:
      - VITE_API_URL=${API_URL}
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  uploads:
```

#### Create `frontend/Dockerfile.prod`:
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
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## 🔐 Pre-Deployment Security Checklist

### 1. Generate Production JWT Keys
```bash
cd backend/keys
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem
chmod 600 private.pem
chmod 644 public.pem
# Add to .gitignore!
```

### 2. Update `.env.production`
```env
# NEVER commit this file!
POSTGRES_PASSWORD=<strong-random-password>
MINIO_ROOT_PASSWORD=<strong-random-password>
SIH26_SESSION_SECRET=<random-64-char-string>
CORS_ORIGINS=https://yourdomain.com
ENVIRONMENT=production
ENABLE_AV_SCAN=true  # Enable in production
MINIO_USE_SSL=true
```

### 3. Update CORS Origins
In your backend config, ensure only your production domains are allowed:
```python
CORS_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
    "https://your-app.vercel.app"
]
```

### 4. Database Migration
Run migrations before going live:
```bash
python migrate_db.py
python create_admin.py  # Create admin user
```

---

## 🌐 Custom Domain Setup

### For Vercel (Frontend):
1. Go to Project Settings → Domains
2. Add your domain: `yourdomain.com`
3. Update DNS records as shown:
   ```
   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com
   ```

### For Render (Backend):
1. Go to Service Settings → Custom Domains
2. Add: `api.yourdomain.com`
3. Update DNS:
   ```
   Type: CNAME
   Name: api
   Value: your-service.onrender.com
   ```

### For GitHub Pages:
1. Settings → Pages → Custom domain
2. Add: `yourdomain.com`
3. DNS Records:
   ```
   Type: A
   Name: @
   Value: 185.199.108.153
   
   Type: CNAME
   Name: www
   Value: yourusername.github.io
   ```

---

## 📊 Monitoring & Maintenance

### Health Check Endpoints
- Backend: `https://api.yourdomain.com/health`
- Frontend: Just visit the homepage

### Logs
- **Render**: Dashboard → Logs tab
- **Vercel**: Project → Deployments → View logs
- **Neon**: Dashboard → Settings → Logs

### Backups
```bash
# Database backup (run weekly)
pg_dump <connection-string> > backup_$(date +%Y%m%d).sql

# Store backups in Google Drive or another cloud storage
```

---

## 💰 Cost Breakdown (Monthly)

| Service | Free Tier | Paid (if needed) |
|---------|-----------|------------------|
| **Frontend (Vercel)** | ✅ FREE unlimited | $20/pro (team features) |
| **Backend (Render)** | ✅ 750 hrs/month | $7/month (always-on) |
| **Database (Neon)** | ✅ 0.5 GB FREE | $19/month (larger) |
| **Storage (Cloudinary)** | ✅ 25 GB FREE | $99/month (more) |
| **Domain (.com)** | ❌ | ~$12/year |
| **TOTAL** | **$0** | **~$8-30/month** |

---

## 🎯 My Recommendation for YOUR Prototype

### For Demo/Presentation Purposes:
1. **Frontend**: Deploy to **Vercel** (FREE, fastest, best DX)
2. **Backend**: Deploy to **Render** (FREE tier sufficient for demos)
3. **Database**: Use **Neon.tech** (FREE, serverless PostgreSQL)
4. **File Storage**: Use **Cloudinary** FREE tier (25GB is plenty for demos)
5. **Disable**: ClamAV scanning (not needed for prototype)

### Total Cost: **$0/month** ✨

### For Production (After Validation):
- Upgrade Render to always-on: $7/month
- Consider upgrading database if needed: $19/month
- Buy custom domain: $12/year

---

## 🆘 Troubleshooting

### Frontend can't connect to backend:
```bash
# Check CORS settings in backend
# Ensure VITE_API_URL points to correct backend URL
# Verify backend is running (visit /health endpoint)
```

### Database connection errors:
```bash
# Check DATABASE_URL format
# Ensure IP whitelist includes Render/Neon IPs
# Verify database is initialized with migrations
```

### Build failures:
```bash
# Clear cache and rebuild
npm run clean && npm run build  # Frontend
pip cache purge && pip install -r requirements.txt  # Backend
```

---

## 📞 Support Resources

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Neon Docs**: https://neon.tech/docs
- **Your Repo Issues**: https://github.com/harshit2k9/SIH-2026/issues

---

**Ready to deploy?** Start with Option B (Vercel + Render + Neon) for the best free experience!
