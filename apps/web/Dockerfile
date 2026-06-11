FROM node:22-alpine AS base

RUN corepack enable

WORKDIR /app

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml turbo.json ./
COPY apps/web/package.json apps/web/

RUN pnpm install --frozen-lockfile

COPY . .

RUN pnpm --filter web build

FROM node:22-alpine

RUN corepack enable

WORKDIR /app

COPY --from=base /app .

EXPOSE 3000

CMD ["pnpm", "--filter", "web", "start"]