FROM node:22-alpine AS development
ENV NODE_ENV development

# Install curl for health checks
RUN apk add --no-cache curl

WORKDIR /app

# Install exactly what the lockfile pins
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY . .

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

CMD [ "npm", "run", "dev" ]
