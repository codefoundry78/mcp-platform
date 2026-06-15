"""Server lifecycle unit tests."""

import io
import json
from typing import TextIO

import pytest

from core.sdk.server import MCPServer
from core.sdk.transports.stdio import StdioTransport


class MemoryTransport(StdioTransport):
    def __init__(self, inputs: list[str]) -> None:
        self._inputs = inputs
        self._index = 0
        self.outputs: list[str] = []
        super().__init__(writer=self._capture_writer())

    def _capture_writer(self) -> TextIO:
        buffer = io.StringIO()

        class Writer:
            def write(self, data: str) -> int:
                buffer.write(data)
                self_ref.outputs.append(data.rstrip("\n"))
                return len(data)

            def flush(self) -> None:
                return None

        self_ref = self
        return Writer()  # type: ignore[return-value]

    async def read_message(self):
        if self._index >= len(self._inputs):
            return None
        line = self._inputs[self._index]
        self._index += 1
        from core.sdk.codec import parse_message

        return parse_message(line)


def _initialize_request(request_id: int = 1) -> str:
    return json.dumps(
        {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "0.1.0"},
            },
        }
    )


@pytest.mark.asyncio
async def test_initialize_returns_capabilities() -> None:
    server = MCPServer(name="test-server", version="1.0.0")
    transport = MemoryTransport([_initialize_request()])
    await server.run(transport)
    response = json.loads(transport.outputs[0])
    assert response["result"]["serverInfo"]["name"] == "test-server"
    assert response["result"]["capabilities"]["tools"]["listChanged"] is True


@pytest.mark.asyncio
async def test_tools_call_before_initialize_returns_error() -> None:
    server = MCPServer(name="test-server")
    server.tool("echo", "echo input", {"type": "object", "properties": {}})(lambda text="": text)

    transport = MemoryTransport(
        [
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {"name": "echo", "arguments": {}},
                }
            )
        ]
    )
    await server.run(transport)
    response = json.loads(transport.outputs[0])
    assert "error" in response
    assert response["error"]["code"] == -32003


@pytest.mark.asyncio
async def test_tools_list_returns_registered_tools() -> None:
    server = MCPServer(name="test-server")
    server.tool(
        "echo",
        "echo text",
        {"type": "object", "properties": {"text": {"type": "string"}}},
    )(lambda text: text)

    transport = MemoryTransport(
        [
            _initialize_request(1),
            json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
        ]
    )
    await server.run(transport)
    tools_response = json.loads(transport.outputs[1])
    assert tools_response["result"]["tools"][0]["name"] == "echo"
