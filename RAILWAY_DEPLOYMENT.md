# Docker Build & Railway Deployment Guide

## Files Created/Updated for Monolithic Deployment

### 1. **frontend/nginx.conf**
- Serves the React frontend on port 3000
- Proxies API requests (upload, ask, ask-llm, etc.) to backend on port 8000
- Handles SPA routing with fallback to index.html
- Caches static assets

### 2. **Dockerfile** (Updated)
- Multi-stage build: Frontend first (Node), then Backend (Python)
- Stage 1: Builds React app with Vite
- Stage 2: Installs Python dependencies, runs FastAPI + Nginx
- Exposes both ports 3000 (Nginx/Frontend) and 8000 (FastAPI/Backend)
- Uses single CMD to start both services

### 3. **.dockerignore** (Enhanced)
- Excludes build artifacts, cache, and unnecessary files
- Reduces Docker image size

### 4. **frontend/src/api.js** (Updated)
- Automatically detects environment
- Production: Uses relative paths (routed by Nginx)
- Development: Uses localhost:7999
- Supports VITE_API_URL environment variable for external deployments

## How It Works

```
User (Browser) 
    ↓
Nginx (Port 3000)
    ├→ /upload, /ask, /ask-llm, etc. → FastAPI (Port 8000)
    └→ / → React Frontend + Static Assets
```

## Local Testing

```bash
# Build the image
docker build -t faiss-rag .

# Run the container
docker run -p 3000:3000 -p 8000:8000 \
  -e PINECONE_API_KEY=your_key \
  -e PINECONE_INDEX_NAME=document-qa \
  -e GEMINI_API_KEY=your_key \
  faiss-rag

# Access
# Frontend: http://localhost:3000
# Backend Docs: http://localhost:8000/docs
```

## Railway Deployment

### Option A: Single Service (Monolithic - Recommended)

```bash
railway login
railway init
railway variables set PINECONE_API_KEY=your_key
railway variables set PINECONE_INDEX_NAME=document-qa
railway variables set GEMINI_API_KEY=your_key
railway up
```

Railway will:
1. Detect Dockerfile
2. Build the image
3. Expose port 3000 as the main entry point
4. Backend API accessible internally via Nginx proxy

### Option B: Two Separate Services

If you prefer separate frontend/backend services:
- Use `Dockerfile.frontend` for frontend
- Use original `Dockerfile` for backend
- Deploy as two separate Railway services
- Configure VITE_API_URL pointing to backend service URL

## Key Differences: Monolithic vs Two Services

| Aspect | Monolithic | Separate Services |
|--------|-----------|------------------|
| Deployment | One Container | Two Containers |
| Scalability | Limited | Independent |
| Cost | Lower (smaller image) | Higher (two services) |
| Ease of Setup | Simpler | More Complex |
| Debugging | Unified logs | Separate logs |
| Update Speed | Together | Independent |

## Troubleshooting

### Build Error: "nginx.conf not found"
→ Already fixed! The file is now in `frontend/nginx.conf`

### "Connection refused" when accessing API
→ Check Nginx logs in container: `docker logs <container_id>`

### Frontend can't reach backend
→ Verify Nginx proxy config is running (it should route /upload, /ask, etc. to port 8000)

### Railway Port Issues
→ Railway automatically maps container port 3000 to external HTTPS URL
→ Access frontend at https://your-app.up.railway.app
→ Backend API accessible at https://your-app.up.railway.app/upload, etc.

## Next Steps

1. ✅ Created `frontend/nginx.conf`
2. ✅ Updated `Dockerfile` with correct syntax
3. ✅ Updated `frontend/src/api.js` for environment-aware API URLs
4. ✅ Enhanced `.dockerignore`

Ready to deploy!

```bash
# Final deployment
railway up

# Or if already initialized:
railway deploy
```
