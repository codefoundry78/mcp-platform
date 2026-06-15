"""JSON-RPC 2.0 message envelopes for MCP."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

JSONRPC_VERSION = "2.0"


class JsonRpcError(BaseModel):
    code: int
    message: str
    data: Any | None = None


class JsonRpcRequest(BaseModel):
    jsonrpc: Literal["2.0"] = JSONRPC_VERSION
    id: str | int
    method: str
    params: dict[str, Any] | None = None


class JsonRpcNotification(BaseModel):
    jsonrpc: Literal["2.0"] = JSONRPC_VERSION
    method: str
    params: dict[str, Any] | None = None
    id: None = None

    @model_validator(mode="before")
    @classmethod
    def reject_id(cls, data: Any) -> Any:
        if isinstance(data, dict) and "id" in data:
            msg = "Notifications must not include an id field"
            raise ValueError(msg)
        return data


class JsonRpcResponse(BaseModel):
    jsonrpc: Literal["2.0"] = JSONRPC_VERSION
    id: str | int
    result: Any | None = None
    error: JsonRpcError | None = None

    @model_validator(mode="after")
    def validate_result_or_error(self) -> JsonRpcResponse:
        if (self.result is None) == (self.error is None):
            msg = "Response must include exactly one of result or error"
            raise ValueError(msg)
        return self
