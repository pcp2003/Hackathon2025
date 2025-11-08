# Frontend - React + Vite Docker Image
# Multi-stage build for optimized production image

# Stage 1: Builder - Build React app with Vite
FROM node:20-alpine as builder

WORKDIR /app

# Copy package file
COPY frontend/package.json ./

# Install dependencies
RUN npm install

# Copy frontend source code
COPY frontend/src ./src
COPY frontend/index.html ./
COPY frontend/vite.config.js ./
COPY frontend/vitest.config.js ./

# Build the application
RUN npm run build

# Stage 2: Runtime - Nginx serving built React app
FROM nginx:alpine

# Copy nginx config from source
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider https://localhost/ || wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Expose ports (HTTP and HTTPS)
EXPOSE 80
EXPOSE 443

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
