# Standard Node builder
FROM node:20-alpine
# Add build tools for native dependencies
RUN apk add --no-cache python3 make g++ libc6-compat

WORKDIR /app
COPY . .

WORKDIR /app/frontend

RUN \
  if [ -f ../yarn.lock ] || [ -f yarn.lock ]; then yarn install; \
  elif [ -f ../pnpm-lock.yaml ] || [ -f pnpm-lock.yaml ]; then corepack enable pnpm && pnpm install; \
  else npm install; \
  fi

# Run build if present for generic TS apps
RUN npm run build --if-present

ENV NODE_ENV=production
EXPOSE 3000
ENV PORT=3000

CMD ["npm", "start"]
