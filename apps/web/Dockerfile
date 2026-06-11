# -------------------------
# 1. Base image
# -------------------------
FROM node:22-alpine AS base

RUN corepack enable
WORKDIR /app

# -------------------------
# 2. Install dependencies
# -------------------------
FROM base AS deps

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml turbo.json ./
COPY apps/web/package.json apps/web/

RUN pnpm install --frozen-lockfile

# -------------------------
# 3. Build stage
# -------------------------
FROM deps AS builder

COPY . .

RUN pnpm --filter web build

# -------------------------
# 4. Production runtime
# -------------------------
FROM node:22-alpine AS runner

RUN corepack enable
WORKDIR /app

ENV NODE_ENV=production

# Copy only built output
COPY --from=builder /app/apps/web/.next /app/apps/web/.next
COPY --from=builder /app/apps/web/public /app/apps/web/public
COPY --from=builder /app/apps/web/package.json /app/apps/web/package.json
COPY --from=builder /app/node_modules /app/node_modules

EXPOSE 3000

CMD ["pnpm", "--filter", "web", "start"]