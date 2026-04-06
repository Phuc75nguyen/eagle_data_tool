# Step 1: Build source code React using Node 22 (To meet Vite requirements)
FROM node:22-slim AS build
WORKDIR /app

# Install pnpm tool
RUN npm install -g pnpm

# Copy package configuration files
COPY package.json pnpm-lock.yaml* ./

# Install libraries using pnpm
RUN pnpm install

# Copy all code
COPY . .

# Set environment variables
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Build project
RUN pnpm run build

# Step 2: Run web using Nginx server
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]