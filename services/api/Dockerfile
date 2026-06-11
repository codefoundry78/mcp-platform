FROM node:22-alpine AS base

RUN corepack enable

WORKDIR /app

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml turbo.json ./
COPY services/api/package.json services/api/

RUN pnpm install --frozen-lockfile

COPY . .

RUN pnpm --filter api build

FROM node:22-alpine

RUN corepack enable

WORKDIR /app

COPY --from=base /app .

EXPOSE 3001

CMD ["pnpm", "--filter", "api", "start:prod"]