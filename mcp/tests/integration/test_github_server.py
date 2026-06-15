"""GitHub server integration tests."""

from __future__ import annotations

import json
import sys

import httpx
import pytest
import respx

from core.sdk.client import MCPClient


@pytest.mark.asyncio
@respx.mock
async def test_list_repos_returns_repo_names() -> None:
    respx.get("https://api.github.com/user/repos").mock(
        return_value=httpx.Response(
            200,
            json=[{"name": "alpha", "full_name": "user/alpha"}],
        )
    )

    client = MCPClient(name="test-client", version="0.1.0")
    command = [sys.executable, "-m", "servers.github_server"]

    import os

    os.environ["GITHUB_TOKEN"] = "test-token"
    try:
        await client.connect_stdio(command)
        result = await client.call_tool("list_repos", {})
        repos = json.loads(result.content[0].text)
        assert repos[0]["name"] == "alpha"
    finally:
        await client.close()
        os.environ.pop("GITHUB_TOKEN", None)


@pytest.mark.asyncio
async def test_missing_token_returns_clear_error() -> None:
    from core.sdk.errors import MCPError

    client = MCPClient(name="test-client", version="0.1.0")
    command = [sys.executable, "-m", "servers.github_server"]

    import os

    os.environ.pop("GITHUB_TOKEN", None)
    await client.connect_stdio(command)
    with pytest.raises(MCPError) as exc:
        await client.call_tool("list_repos", {})
    assert "GITHUB_TOKEN" in str(exc.value)
    await client.close()
