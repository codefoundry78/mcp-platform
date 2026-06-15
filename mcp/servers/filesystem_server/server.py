"""Filesystem MCP server."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from core.sdk.errors import MCPError, MCP_PATH_NOT_ALLOWED
from core.sdk.server import MCPServer
from servers.filesystem_server.config import FilesystemConfig


def _resolve_path(root: Path, user_path: str) -> Path:
    candidate = (root / user_path).resolve()
    root_resolved = root.resolve()
    if not str(candidate).startswith(str(root_resolved)):
        raise MCPError(
            f"Path not allowed: {user_path}",
            code=MCP_PATH_NOT_ALLOWED,
        )
    return candidate


def create_server(config: FilesystemConfig | None = None) -> MCPServer:
    config = config or FilesystemConfig.from_env()
    root = config.root.resolve()
    root.mkdir(parents=True, exist_ok=True)

    server = MCPServer(name="filesystem-server", version="0.1.0")

    @server.tool(
        "list_directory",
        "List files and directories at a path relative to the sandbox root.",
        {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative path within sandbox"},
            },
            "required": ["path"],
        },
    )
    async def list_directory(path: str) -> str:
        target = _resolve_path(root, path)
        if not target.exists():
            raise MCPError(f"Path not found: {path}", code=MCP_PATH_NOT_ALLOWED)
        if not target.is_dir():
            raise MCPError(f"Not a directory: {path}", code=MCP_PATH_NOT_ALLOWED)

        entries = []
        for entry in sorted(target.iterdir()):
            entries.append(
                {
                    "name": entry.name,
                    "type": "directory" if entry.is_dir() else "file",
                }
            )
        return json.dumps(entries, indent=2)

    @server.tool(
        "read_file",
        "Read a text file relative to the sandbox root.",
        {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative path within sandbox"},
            },
            "required": ["path"],
        },
    )
    async def read_file(path: str) -> str:
        target = _resolve_path(root, path)
        if not target.is_file():
            raise MCPError(f"Not a file: {path}", code=MCP_PATH_NOT_ALLOWED)
        return target.read_text(encoding="utf-8")

    @server.tool(
        "stat",
        "Return metadata for a path relative to the sandbox root.",
        {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative path within sandbox"},
            },
            "required": ["path"],
        },
    )
    async def stat(path: str) -> str:
        target = _resolve_path(root, path)
        if not target.exists():
            raise MCPError(f"Path not found: {path}", code=MCP_PATH_NOT_ALLOWED)
        info = target.stat()
        payload = {
            "path": path,
            "is_file": target.is_file(),
            "is_dir": target.is_dir(),
            "size": info.st_size,
        }
        return json.dumps(payload, indent=2)

    return server


def main() -> None:
    asyncio.run(create_server().run_stdio())


if __name__ == "__main__":
    main()
