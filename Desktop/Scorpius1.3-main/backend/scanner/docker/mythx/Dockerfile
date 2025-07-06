# MythX Docker Image for Scorpius Vulnerability Scanner
FROM node:18-alpine

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    build-base \
    git

# Install MythX CLI
RUN npm install -g mythxjs

# Install Python dependencies for additional tools
RUN pip3 install --break-system-packages \
    requests \
    fastapi \
    uvicorn \
    python-multipart \
    pythx

# Create workspace directories
RUN mkdir -p /workspace/contracts /workspace/reports

# Copy API service
COPY app.py /workspace/app.py

# Create non-root user for security (use available UID)
RUN adduser -D mythx && \
    chown -R mythx:mythx /workspace

USER mythx
WORKDIR /workspace

# Set environment variables
ENV NODE_ENV=production

# Expose API port
EXPOSE 8084

# Default command starts the API server
CMD ["python3", "/workspace/app.py"]
