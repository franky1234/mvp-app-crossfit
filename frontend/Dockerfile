# --- Build stage ---
FROM node:18-alpine AS build
WORKDIR /app

# install dependencies
COPY package.json package-lock.json* ./
RUN npm ci || npm install

# copy source and build
COPY . .
RUN npm run build

# --- Production runner using 'serve' ---
FROM node:18-alpine AS runner
WORKDIR /app

# install a tiny static server
RUN npm install -g serve@14.2.0

# copy built static files
COPY --from=build /app/dist ./dist

EXPOSE 90
CMD ["serve", "-s", "dist", "-l", "90"]
