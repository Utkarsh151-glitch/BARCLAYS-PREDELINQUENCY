# Multi-stage SPA build (vite)
FROM node:20-alpine AS builder
RUN apk add --no-cache python3 make g++ libc6-compat

WORKDIR /app
COPY . .

WORKDIR /app/frontend
RUN \\
  if [ -f ../yarn.lock ] || [ -f yarn.lock ]; then yarn install; \\
  elif [ -f ../pnpm-lock.yaml ] || [ -f pnpm-lock.yaml ]; then corepack enable pnpm && pnpm install; \\
  else npm install; \\
  fi

RUN npm run build

# Production stage — lightweight nginx to serve static files
FROM nginx:alpine AS runner

# SPA routing: fallback all routes to index.html
RUN echo 'server { \
  listen 80; \
  listen [::]:80; \
  root /usr/share/nginx/html; \
  index index.html; \
  location / { \
    try_files $uri $uri/ /index.html; \
  } \
}' > /etc/nginx/conf.d/default.conf

COPY --from=builder /app/frontend/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
