# -------------------------
# Base
# -------------------------
FROM node:22-alpine AS base

RUN corepack enable
WORKDIR /app

# -------------------------
# Dependencies
# -------------------------
FROM base AS deps

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml turbo.json ./
COPY services/api/package.json services/api/package.json
COPY packages/shared-types/package.json packages/shared-types/package.json

RUN pnpm install --frozen-lockfile

# -------------------------
# Build
# -------------------------
FROM deps AS builder

COPY packages/shared-types packages/shared-types
COPY services/api services/api

RUN pnpm --filter @mcp-platform/shared-types build
RUN pnpm --filter @mcp-platform/api build

# -------------------------
# Runtime
# -------------------------
FROM node:22-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/services/api/dist ./dist
COPY --from=builder /app/services/api/package.json ./package.json
COPY --from=builder /app/node_modules ./node_modules

EXPOSE 3001

CMD ["node", "dist/main.js"]
