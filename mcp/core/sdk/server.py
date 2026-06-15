"""MCP server implementation."""

from __future__ import annotations

import sys
from collections.abc import Awaitable, Callable
from enum import Enum
from typing import Any

import structlog

from core.sdk.codec import serialize_error, serialize_response
from core.sdk.errors import (
    INTERNAL_ERROR,
    MCP_NOT_INITIALIZED,
    MCPError,
    METHOD_NOT_FOUND,
)
from core.sdk.handlers.lifecycle import handle_initialize
from core.sdk.handlers.prompts import handle_prompts_list
from core.sdk.handlers.resources import handle_resources_list
from core.sdk.handlers.tools import handle_tools_call, handle_tools_list
from core.sdk.protocol import JsonRpcNotification, JsonRpcRequest
from core.sdk.tool_registry import ToolRegistry
from core.sdk.transports.stdio import StdioTransport
from core.sdk.types import InitializeParams, Implementation, ToolsCallParams

logger = structlog.get_logger(__name__)


class ServerState(str, Enum):
    UNINITIALIZED = "uninitialized"
    READY = "ready"


class MCPServer:
    def __init__(self, name: str, version: str = "0.1.0") -> None:
        self._info = Implementation(name=name, version=version)
        self._registry = ToolRegistry()
        self._state = ServerState.UNINITIALIZED

    @property
    def registry(self) -> ToolRegistry:
        return self._registry

    def tool(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any] | None = None,
    ) -> Callable[[Callable[..., Any | Awaitable[Any]]], Callable[..., Any | Awaitable[Any]]]:
        schema = input_schema or {"type": "object", "properties": {}}

        def decorator(
            handler: Callable[..., Any | Awaitable[Any]],
        ) -> Callable[..., Any | Awaitable[Any]]:
            self._registry.register(name, description, schema, handler)
            return handler

        return decorator

    async def _dispatch(self, request: JsonRpcRequest) -> Any:
        if request.method != "initialize" and self._state != ServerState.READY:
            raise MCPError("Server not initialized", code=MCP_NOT_INITIALIZED)

        if request.method == "initialize":
            params = InitializeParams.model_validate(request.params or {})
            self._state = ServerState.READY
            return handle_initialize(params, self._info).model_dump(exclude_none=True)

        if request.method == "tools/list":
            result = await handle_tools_list(self._registry)
            return result.model_dump(exclude_none=True)

        if request.method == "tools/call":
            params = ToolsCallParams.model_validate(request.params or {})
            result = await handle_tools_call(self._registry, params)
            return result.model_dump(exclude_none=True)

        if request.method == "resources/list":
            result = await handle_resources_list()
            return result.model_dump(exclude_none=True)

        if request.method == "prompts/list":
            result = await handle_prompts_list()
            return result.model_dump(exclude_none=True)

        if request.method == "ping":
            return {}

        raise MCPError(f"Method not found: {request.method}", code=METHOD_NOT_FOUND)

    async def _handle_notification(self, notification: JsonRpcNotification) -> None:
        if notification.method == "notifications/initialized":
            logger.debug("client_initialized")
            return
        logger.warning("unsupported_notification", method=notification.method)

    async def run(self, transport: StdioTransport | None = None) -> None:
        transport = transport or StdioTransport()
        logger.info("server_started", name=self._info.name, version=self._info.version)

        while True:
            try:
                message = await transport.read_message()
            except MCPError as exc:
                if exc.code == -32700:  # PARSE_ERROR
                    await transport.write_raw(serialize_error(None, exc))
                continue

            if message is None:
                break

            if isinstance(message, JsonRpcNotification):
                await self._handle_notification(message)
                continue

            try:
                result = await self._dispatch(message)
                await transport.write_raw(serialize_response(message.id, result))
            except MCPError as exc:
                await transport.write_raw(serialize_error(message.id, exc))
            except Exception as exc:
                logger.exception("request_failed", method=message.method)
                await transport.write_raw(
                    serialize_error(message.id, MCPError(str(exc), code=INTERNAL_ERROR))
                )

    async def run_stdio(self) -> None:
        await self.run(StdioTransport())


def main() -> None:
    """Default entrypoint placeholder for subclass servers."""
    raise NotImplementedError("Subclass MCPServer and provide a main() entrypoint")
