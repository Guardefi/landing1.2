# Node.js Simulation Sandbox Dockerfile
FROM node:18-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --omit=dev && npm cache clean --force

# Production stage
FROM node:18-alpine as production

# Install security updates
RUN apk update && apk upgrade && apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1001 -S scorpius && \
    adduser -S -D -H -u 1001 -s /sbin/nologin scorpius

# Set working directory
WORKDIR /app

# Copy built dependencies
COPY --from=builder /app/node_modules ./node_modules

# Copy application files
COPY . .

# Change ownership to non-root user
RUN chown -R scorpius:scorpius /app

# Switch to non-root user
USER scorpius

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "const http = require('http'); \
    const options = { hostname: 'localhost', port: 3001, path: '/health', timeout: 2000 }; \
    const req = http.request(options, (res) => { \
      if (res.statusCode === 200) process.exit(0); \
      else process.exit(1); \
    }); \
    req.on('error', () => process.exit(1)); \
    req.on('timeout', () => process.exit(1)); \
    req.end();"

# Start application
ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "server.js"]
