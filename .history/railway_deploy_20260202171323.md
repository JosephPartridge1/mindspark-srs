# Railway.app Deployment Guide

## Prerequisites
1. GitHub repository created ✅ (this script did it)
2. Railway.app account (free)

## Deployment Steps

### OPTION A: Web Dashboard (Recommended)
1. Go to https://railway.app
2. Login with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub"
5. Choose "mindspark-srs" repository
6. Railway will auto-detect Flask app
7. Wait 2-5 minutes for deployment
8. Get your public URL: `https://[project-name].up.railway.app`

### OPTION B: CLI Deployment
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize
railway init

# Deploy
railway up
```

## Environment Variables (Auto-set by Railway)
- `PORT` (auto)
- `DATABASE_URL` (if you add PostgreSQL database)
- `RAILWAY_ENVIRONMENT` = "production"

## Post-Deployment
1. Visit your URL
2. Test the app
3. Check admin: `/admin`
4. Monitor logs in Railway dashboard
