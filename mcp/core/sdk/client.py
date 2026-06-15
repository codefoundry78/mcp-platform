"""MCP client implementation."""

from __future__ import annotations

from typing import Any

from core.sdk.transports.stdio_client import StdioClientTransport
from core.sdk.types import (
    PROTOCOL_VERSION,
    ClientCapabilities,
    Implementation,
    Tool,
    ToolsCallResult,
)


class MCPClient:
    def __init__(self, name: str, version: str = "0.1.0") -> None:
        self._info = Implementation(name=name, version=version)
        self._transport: StdioClientTransport | None = None
        self._initialized = False

    async def connect_stdio(self, command: list[str]) -> None:
        self._transport = StdioClientTransport(command)
        await self._transport.start()
        await self._initialize()

    async def _initialize(self) -> None:
        if self._transport is None:
            raise RuntimeError("Client not connected")

        result = await self._transport.request(
            "initialize",
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": ClientCapabilities().model_dump(exclude_none=True),
                "clientInfo": self._info.model_dump(),
            },
        )
        if not result:
            raise RuntimeError("Initialize returned empty result")

        await self._transport.notify("notifications/initialized")
        self._initialized = True

    async def list_tools(self) -> list[Tool]:
        self._ensure_ready()
        assert self._transport is not None
        result = await self._transport.request("tools/list")
        tools_data = result.get("tools", []) if isinstance(result, dict) else []
        return [Tool.model_validate(item) for item in tools_data]

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> ToolsCallResult:
        self._ensure_ready()
        assert self._transport is not None
        result = await self._transport.request(
            "tools/call",
            {"name": name, "arguments": arguments or {}},
        )
        return ToolsCallResult.model_validate(result)

    async def close(self) -> None:
        if self._transport:
            await self._transport.close()
            self._transport = None
        self._initialized = False

    def _ensure_ready(self) -> None:
        if not self._initialized or self._transport is None:
            raise RuntimeError("Client is not connected and initialized")
