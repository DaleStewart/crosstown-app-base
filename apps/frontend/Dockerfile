FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --no-audit --no-fund
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
RUN addgroup -S app && adduser -S -G app app
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY docker-entrypoint.sh /docker-entrypoint.d/40-orchestrator-url.sh
RUN chmod +x /docker-entrypoint.d/40-orchestrator-url.sh \
 && chown -R app:app /usr/share/nginx/html /var/cache/nginx /var/run /var/log/nginx /etc/nginx
USER app
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
