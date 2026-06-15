"""JSON-RPC and MCP error codes."""

from __future__ import annotations

from typing import Any

# Standard JSON-RPC 2.0 error codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603

# MCP-specific
MCP_TOOL_NOT_FOUND = -32001
MCP_TOOL_EXECUTION_ERROR = -32002
MCP_NOT_INITIALIZED = -32003
MCP_PATH_NOT_ALLOWED = -32004


class MCPError(Exception):
    """Raised when an MCP operation fails."""

    def __init__(
        self,
        message: str,
        *,
        code: int = INTERNAL_ERROR,
        data: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.data = data

    def to_json_rpc_error(self) -> dict[str, Any]:
        error: dict[str, Any] = {"code": self.code, "message": str(self)}
        if self.data is not None:
            error["data"] = self.data
        return error
