"""GitHub MCP server."""

from __future__ import annotations

import asyncio
import json
import os

import httpx

from core.sdk.errors import MCPError, INTERNAL_ERROR
from core.sdk.server import MCPServer


def create_server(token: str | None = None) -> MCPServer:
    github_token = token or os.environ.get("GITHUB_TOKEN")
    server = MCPServer(name="github-server", version="0.1.0")

    @server.tool(
        "list_repos",
        "List repositories for the authenticated user or an organization.",
        {
            "type": "object",
            "properties": {
                "org": {
                    "type": "string",
                    "description": "Optional GitHub organization login",
                },
            },
        },
    )
    async def list_repos(org: str | None = None) -> str:
        if not github_token:
            raise MCPError("GITHUB_TOKEN is not configured", code=INTERNAL_ERROR)

        headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        url = (
            f"https://api.github.com/orgs/{org}/repos"
            if org
            else "https://api.github.com/user/repos"
        )

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code >= 400:
                raise MCPError(
                    f"GitHub API error: {response.status_code}",
                    code=INTERNAL_ERROR,
                    data=response.text,
                )
            repos = [{"name": item["name"], "full_name": item["full_name"]} for item in response.json()]
            return json.dumps(repos, indent=2)

    return server


def main() -> None:
    asyncio.run(create_server().run_stdio())


if __name__ == "__main__":
    main()
