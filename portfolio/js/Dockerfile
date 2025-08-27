FROM node:21.7-alpine AS development
ENV NODE_ENV development

# Install curl for health checks
RUN apk add --no-cache curl

# Add a work directory
WORKDIR /app

# Cache and Install dependencies
COPY package.json .
RUN npm install

# Copy app files
COPY . .

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start the app
CMD [ "npm", "run", "dev" ]