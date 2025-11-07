# Frontend - React + Vite Docker Image
# Multi-stage build for optimized production image

# Stage 1: Builder
FROM node:20-alpine as builder

WORKDIR /app

# Copy all frontend files first
COPY frontend/ .

# Install dependencies
RUN npm install --ignore-scripts

# Build the application
RUN npm run build

# Stage 2: Runtime - Nginx
FROM nginx:alpine

WORKDIR /app

# Copy nginx config from root
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
