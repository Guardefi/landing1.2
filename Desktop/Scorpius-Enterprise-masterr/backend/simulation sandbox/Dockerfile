# Multi-stage build for optimized production image
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (including dev dependencies for build)
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY . .

# Remove development files
RUN rm -rf tests/ docs/ .git/ .github/

# Production stage
FROM node:18-alpine AS production

# Install security updates
RUN apk update && apk upgrade && apk add --no-cache \
    dumb-init \
    curl \
    git \
    python3 \
    make \
    g++ \
    && rm -rf /var/cache/apk/*

# Create non-root user
RUN addgroup -g 1001 -S scorpius && \
    adduser -S scorpius -u 1001 -G scorpius

# Set working directory
WORKDIR /app

# Copy built application from builder stage
COPY --from=builder --chown=scorpius:scorpius /app .

# Create necessary directories
RUN mkdir -p logs storage tmp && \
    chown -R scorpius:scorpius logs storage tmp

# Install Foundry for smart contract operations
RUN curl -L https://foundry.paradigm.xyz | bash && \
    ~/.foundry/bin/foundryup && \
    cp ~/.foundry/bin/* /usr/local/bin/

# Switch to non-root user
USER scorpius

# Expose port
EXPOSE 3002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3002/health || exit 1

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3002

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Start the application
CMD ["node", "src/index.js"]
