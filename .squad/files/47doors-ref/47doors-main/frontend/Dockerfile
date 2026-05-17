# Frontend Dockerfile for Front Door Support Agent
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application (vite handles TS transpilation via esbuild;
# tsc type-checking runs in CI/local dev, not Docker builds)
RUN npx vite build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration as template (envsubst resolves BACKEND_URL at startup)
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Default backend URL for local docker-compose; overridden in Azure
ENV BACKEND_URL=http://backend:8000

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

# envsubst only BACKEND_URL (preserve nginx variables like $host, $uri, etc.)
CMD ["/bin/sh", "-c", "envsubst '${BACKEND_URL}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
