"""Codec unit tests."""

import json

import pytest

from core.sdk.codec import (
    parse_message,
    serialize_notification,
    serialize_response,
)
from core.sdk.errors import INVALID_REQUEST, MCPError, PARSE_ERROR
from core.sdk.protocol import JsonRpcNotification, JsonRpcRequest


def test_parses_initialize_request() -> None:
    raw = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "0.1.0"},
            },
        }
    )
    message = parse_message(raw)
    assert isinstance(message, JsonRpcRequest)
    assert message.method == "initialize"
    assert message.id == 1


def test_rejects_request_with_null_id() -> None:
    raw = json.dumps({"jsonrpc": "2.0", "id": None, "method": "initialize"})
    with pytest.raises(MCPError) as exc:
        parse_message(raw)
    assert exc.value.code == INVALID_REQUEST


def test_serializes_tools_list_response() -> None:
    payload = serialize_response(2, {"tools": [{"name": "read_file"}]})
    data = json.loads(payload)
    assert data["id"] == 2
    assert data["result"]["tools"][0]["name"] == "read_file"


def test_parses_notification_without_id() -> None:
    raw = json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"})
    message = parse_message(raw)
    assert isinstance(message, JsonRpcNotification)
    assert message.method == "notifications/initialized"


def test_parse_error_on_invalid_json() -> None:
    with pytest.raises(MCPError) as exc:
        parse_message("{not-json")
    assert exc.value.code == PARSE_ERROR


def test_serialize_notification() -> None:
    payload = serialize_notification("notifications/initialized")
    data = json.loads(payload)
    assert data["method"] == "notifications/initialized"
    assert "id" not in data
