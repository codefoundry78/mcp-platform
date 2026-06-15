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
COPY apps/web/package.json apps/web/package.json
COPY packages/shared-types/package.json packages/shared-types/package.json

RUN pnpm install --frozen-lockfile

# -------------------------
# Build
# -------------------------
FROM deps AS builder

COPY packages/shared-types packages/shared-types
COPY apps/web apps/web

RUN pnpm --filter @mcp-platform/shared-types build
RUN pnpm --filter @mcp-platform/web build

# -------------------------
# Runtime
# -------------------------
FROM node:22-alpine AS runner

RUN corepack enable
WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/apps/web/dist ./dist
COPY --from=builder /app/apps/web/package.json ./package.json

RUN npm install -g serve

EXPOSE 3000

CMD ["serve", "-s", "dist", "-l", "3000"]
