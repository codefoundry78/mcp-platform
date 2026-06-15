"""Filesystem server integration tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from core.sdk.client import MCPClient


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    (tmp_path / "hello.txt").write_text("hello world", encoding="utf-8")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "note.txt").write_text("nested file", encoding="utf-8")
    return tmp_path


@pytest.mark.asyncio
async def test_full_stdio_session_with_filesystem_server(workspace: Path) -> None:
    client = MCPClient(name="test-client", version="0.1.0")
    command = [sys.executable, "-m", "servers.filesystem_server"]

    import os

    old_env = os.environ.get("MCP_FS_ROOT")
    os.environ["MCP_FS_ROOT"] = str(workspace)
    try:
        await client.connect_stdio(command)
        tools = await client.list_tools()
        tool_names = {tool.name for tool in tools}
        assert {"list_directory", "read_file", "stat"}.issubset(tool_names)

        result = await client.call_tool("read_file", {"path": "hello.txt"})
        assert result.content[0].text == "hello world"
    finally:
        await client.close()
        if old_env is None:
            os.environ.pop("MCP_FS_ROOT", None)
        else:
            os.environ["MCP_FS_ROOT"] = old_env


@pytest.mark.asyncio
async def test_rejects_path_outside_root(workspace: Path) -> None:
    from core.sdk.errors import MCPError

    client = MCPClient(name="test-client", version="0.1.0")
    command = [sys.executable, "-m", "servers.filesystem_server"]

    import os

    os.environ["MCP_FS_ROOT"] = str(workspace)
    try:
        await client.connect_stdio(command)
        with pytest.raises(MCPError):
            await client.call_tool("read_file", {"path": "../../../etc/passwd"})
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_list_directory_returns_entries(workspace: Path) -> None:
    client = MCPClient(name="test-client", version="0.1.0")
    command = [sys.executable, "-m", "servers.filesystem_server"]

    import os

    os.environ["MCP_FS_ROOT"] = str(workspace)
    try:
        await client.connect_stdio(command)
        result = await client.call_tool("list_directory", {"path": "."})
        assert "hello.txt" in result.content[0].text
        assert "nested" in result.content[0].text
    finally:
        await client.close()
