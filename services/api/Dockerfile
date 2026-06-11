# -------------------------
# Base
# -------------------------
FROM node:22-alpine AS base

RUN corepack enable
WORKDIR /app

# -------------------------
# Dependencies (cached layer)
# -------------------------
FROM base AS deps

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml turbo.json ./
COPY services/api/package.json services/api/package.json

RUN pnpm install --frozen-lockfile

# -------------------------
# Build stage
# -------------------------
FROM deps AS builder

COPY . .

RUN pnpm --filter api build

# -------------------------
# Runtime (clean NestJS production image)
# -------------------------
FROM node:22-alpine AS runner

RUN corepack enable
WORKDIR /app

ENV NODE_ENV=production

# Only compiled output
COPY --from=builder /app/services/api/dist ./dist
COPY --from=builder /app/services/api/package.json ./package.json

# Install ONLY production dependencies
COPY --from=builder /app/pnpm-lock.yaml ./
COPY --from=builder /app/pnpm-workspace.yaml ./

RUN pnpm install --prod --frozen-lockfile

EXPOSE 3001

CMD ["node", "dist/main.js"]