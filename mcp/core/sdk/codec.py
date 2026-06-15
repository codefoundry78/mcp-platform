"""JSON-RPC message parsing and serialization."""

from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from core.sdk.errors import INVALID_REQUEST, MCPError, PARSE_ERROR
from core.sdk.protocol import (
    JSONRPC_VERSION,
    JsonRpcError,
    JsonRpcNotification,
    JsonRpcRequest,
    JsonRpcResponse,
)

IncomingMessage = JsonRpcRequest | JsonRpcNotification


def parse_message(raw: str) -> IncomingMessage:
    """Parse a single JSON-RPC message from a transport line."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise MCPError("Parse error", code=PARSE_ERROR, data=str(exc)) from exc

    if not isinstance(data, dict):
        raise MCPError("Invalid Request", code=INVALID_REQUEST)

    if data.get("jsonrpc") != JSONRPC_VERSION:
        raise MCPError("Invalid Request", code=INVALID_REQUEST)

    if "method" not in data:
        raise MCPError("Invalid Request", code=INVALID_REQUEST)

    try:
        if "id" in data:
            if data["id"] is None:
                raise MCPError("Invalid Request: id must not be null", code=INVALID_REQUEST)
            return JsonRpcRequest.model_validate(data)
        return JsonRpcNotification.model_validate(data)
    except (ValidationError, ValueError) as exc:
        raise MCPError("Invalid Request", code=INVALID_REQUEST, data=str(exc)) from exc


def serialize_response(request_id: str | int, result: Any) -> str:
    response = JsonRpcResponse(id=request_id, result=result)
    return response.model_dump_json(exclude_none=True)


def serialize_error(request_id: str | int | None, error: JsonRpcError | MCPError) -> str:
    if isinstance(error, MCPError):
        rpc_error = JsonRpcError(**error.to_json_rpc_error())
    else:
        rpc_error = error

    if request_id is None:
        # Parse errors have no request id in JSON-RPC
        payload: dict[str, Any] = {
            "jsonrpc": JSONRPC_VERSION,
            "error": rpc_error.model_dump(exclude_none=True),
            "id": None,
        }
        return json.dumps(payload)

    response = JsonRpcResponse(id=request_id, error=rpc_error)
    return response.model_dump_json(exclude_none=True)


def serialize_notification(method: str, params: dict[str, Any] | None = None) -> str:
    notification = JsonRpcNotification(method=method, params=params)
    return notification.model_dump_json(exclude_none=True)
