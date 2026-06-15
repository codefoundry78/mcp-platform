#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> Installing Node dependencies"
corepack enable
pnpm install

echo "==> Installing Python MCP SDK"
python3 -m pip install -e "./mcp[dev]"

if [[ ! -f .env ]]; then
  echo "==> Creating .env from .env.example"
  cp .env.example .env
fi

echo "==> Starting infrastructure services"
docker compose up -d postgres redis

echo "Bootstrap complete."
echo "  Python tests:  cd mcp && pytest tests -v"
echo "  Node build:    pnpm build"
echo "  Filesystem:    MCP_FS_ROOT=/tmp/workspace mcp-filesystem-server"
