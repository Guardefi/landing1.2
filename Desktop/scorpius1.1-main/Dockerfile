# Multi-stage build for Scorpius demo stack

# ----- Stage 1: Frontend build -----
FROM node:18-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci --legacy-peer-deps --no-audit --no-fund
COPY frontend/ .
RUN npm run build

# ----- Stage 2: API build -----
FROM python:3.11-slim AS api-build
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY services/api-gateway/requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
COPY packages/core ./packages/core
RUN pip install --no-cache-dir ./packages/core
COPY services/api-gateway/ .

# ----- Stage 3: Runtime -----
FROM python:3.11-slim
WORKDIR /app

# install nginx for static frontend
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

COPY --from=api-build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=api-build /usr/local/bin /usr/local/bin
COPY --from=api-build /app /app
COPY --from=frontend-build /frontend/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/nginx.conf
COPY docker-start.sh /docker-start.sh
RUN chmod +x /docker-start.sh

EXPOSE 8000 80

CMD ["/docker-start.sh"]
