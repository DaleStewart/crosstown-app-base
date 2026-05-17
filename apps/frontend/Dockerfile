FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --no-audit --no-fund
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
RUN apk add --no-cache curl
RUN addgroup -S app && adduser -S -G app app
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY docker-entrypoint.sh /docker-entrypoint.d/40-orchestrator-url.sh
RUN chmod +x /docker-entrypoint.d/40-orchestrator-url.sh \
 && sed -i 's|^pid .*|pid /tmp/nginx.pid;|' /etc/nginx/nginx.conf \
 && chown -R app:app /usr/share/nginx/html /var/cache/nginx /var/run /run /var/log/nginx /etc/nginx
USER app
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl --fail --silent --max-time 4 http://localhost:80/api/health || exit 1
CMD ["nginx", "-g", "daemon off;"]
