"""MCP tools/list and tools/call handlers."""

from __future__ import annotations

from core.sdk.tool_registry import ToolRegistry
from core.sdk.types import ToolsCallParams, ToolsCallResult, ToolsListResult


async def handle_tools_list(registry: ToolRegistry) -> ToolsListResult:
    return ToolsListResult(tools=registry.list_tools())


async def handle_tools_call(registry: ToolRegistry, params: ToolsCallParams) -> ToolsCallResult:
    return await registry.call(params.name, params.arguments)
