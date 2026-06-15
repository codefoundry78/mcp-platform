# MCP Platform

Monorepo for an MCP (Model Context Protocol) platform with a Python SDK, reference servers, and Node services.

## Phase 1 status

- Python MCP SDK (`mcp/core/sdk`) with stdio transport
- Reference servers: filesystem (sandboxed), GitHub (`list_repos`)
- Shared TypeScript types (`packages/shared-types`)
- Minimal API and web app scaffolds

## Quick start

```bash
./scripts/bootstrap.sh
cd mcp && pytest tests -v
pnpm build
```

## Filesystem server

```bash
cd mcp
pip install -e .
MCP_FS_ROOT=/tmp/workspace mcp-filesystem-server
```

## API health check

```bash
pnpm --filter @mcp-platform/api start
curl http://localhost:3001/health
```
