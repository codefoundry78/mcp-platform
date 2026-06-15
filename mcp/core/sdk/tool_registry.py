"""Tool registration and dispatch."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import ValidationError

from core.sdk.errors import INVALID_PARAMS, MCP_TOOL_NOT_FOUND, MCPError
from core.sdk.types import TextContent, Tool, ToolsCallResult


ToolHandler = Callable[..., Any | Awaitable[Any]]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}
        self._handlers: dict[str, ToolHandler] = {}

    def register(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        handler: ToolHandler,
    ) -> None:
        self._tools[name] = Tool(
            name=name,
            description=description,
            inputSchema=input_schema,
        )
        self._handlers[name] = handler

    def list_tools(self) -> list[Tool]:
        return list(self._tools.values())

    async def call(self, name: str, arguments: dict[str, Any]) -> ToolsCallResult:
        if name not in self._handlers:
            raise MCPError(f"Unknown tool: {name}", code=MCP_TOOL_NOT_FOUND)

        handler = self._handlers[name]
        try:
            result = handler(**arguments)
            if inspect.isawaitable(result):
                result = await result
        except TypeError as exc:
            raise MCPError("Invalid tool arguments", code=INVALID_PARAMS, data=str(exc)) from exc
        except MCPError:
            raise
        except Exception as exc:
            from core.sdk.errors import MCP_TOOL_EXECUTION_ERROR

            return ToolsCallResult(
                content=[TextContent(text=str(exc))],
                isError=True,
            )

        if isinstance(result, ToolsCallResult):
            return result
        return ToolsCallResult(content=[TextContent(text=str(result))])
