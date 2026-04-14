FROM node:18 AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.13-slim
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y \
    build-essential nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY pinecone_manager.py main.py ./

# Copy frontend dist from build stage
COPY --from=frontend-build /frontend/dist /app/frontend/dist

# Copy nginx config
COPY frontend/nginx.conf /etc/nginx/sites-available/default

EXPOSE 8000 3000

# Start both services
CMD ["sh", "-c", "nginx -g 'daemon off;' & uvicorn main:app --host 0.0.0.0 --port 8000"]