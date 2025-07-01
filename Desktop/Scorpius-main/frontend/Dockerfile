# syntax=docker/dockerfile:1

############################
# 1. Build stage
############################
FROM node:18-alpine AS build

WORKDIR /app
ENV PATH="/app/node_modules/.bin:${PATH}"

# ---- dependencies ----
COPY package*.json ./
RUN npm ci --legacy-peer-deps --no-audit --no-fund \
  && npm install -g rimraf@5.0.5 cross-env@7.0.3

# ---- project files ----
COPY tsconfig*.json ./
COPY vite.config.ts ./
COPY index.html ./
COPY src ./src
COPY public ./public

# ---- build ----
RUN rimraf dist \
  && cross-env NODE_ENV=production vite build   # produces /app/dist

############################
# 2. Runtime stage
############################
FROM nginx:alpine AS runtime

# Copy the bundle produced in the previous stage
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
HEALTHCHECK CMD curl -f http://localhost || exit 1

CMD ["nginx", "-g", "daemon off;"]
