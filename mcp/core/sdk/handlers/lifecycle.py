"""MCP lifecycle handlers."""

from __future__ import annotations

from core.sdk.types import (
    PROTOCOL_VERSION,
    InitializeParams,
    InitializeResult,
    Implementation,
    ServerCapabilities,
)


def handle_initialize(params: InitializeParams, server_info: Implementation) -> InitializeResult:
    return InitializeResult(
        protocolVersion=PROTOCOL_VERSION,
        capabilities=ServerCapabilities(tools={"listChanged": True}),
        serverInfo=server_info,
    )
