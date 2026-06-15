"""Stdio transport for MCP clients."""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Any

from core.sdk.codec import IncomingMessage, parse_message, serialize_notification
from core.sdk.errors import MCPError
from core.sdk.protocol import JsonRpcRequest, JsonRpcResponse
from core.sdk.transports.base import Transport


class StdioClientTransport(Transport):
    """Spawn a subprocess and exchange newline-delimited JSON-RPC messages."""

    def __init__(self, command: list[str]) -> None:
        self._command = command
        self._process: asyncio.subprocess.Process | None = None
        self._reader_task: asyncio.Task[None] | None = None
        self._pending: dict[str | int, asyncio.Future[JsonRpcResponse]] = {}
        self._incoming: asyncio.Queue[IncomingMessage | None] = asyncio.Queue()
        self._closed = False
        self._next_id = 0

    async def start(self) -> None:
        self._process = await asyncio.create_subprocess_exec(
            *self._command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=sys.stderr,
        )
        assert self._process.stdout is not None
        self._reader_task = asyncio.create_task(self._read_loop(self._process.stdout))

    async def _read_loop(self, stdout: asyncio.StreamReader) -> None:
        try:
            while True:
                line_bytes = await stdout.readline()
                if not line_bytes:
                    break
                line = line_bytes.decode("utf-8").strip()
                if not line:
                    continue

                data = json.loads(line)
                if "id" in data and ("result" in data or "error" in data):
                    response = JsonRpcResponse.model_validate(data)
                    future = self._pending.pop(response.id, None)
                    if future and not future.done():
                        future.set_result(response)
                    continue

                message = parse_message(line)
                await self._incoming.put(message)
        finally:
            self._closed = True
            await self._incoming.put(None)
            for future in self._pending.values():
                if not future.done():
                    future.set_exception(ConnectionError("Transport closed"))
            self._pending.clear()

    def next_id(self) -> int:
        self._next_id += 1
        return self._next_id

    async def request(self, method: str, params: dict[str, Any] | None = None) -> Any:
        if self._process is None or self._process.stdin is None:
            raise RuntimeError("Transport not started")

        request_id = self.next_id()
        payload = JsonRpcRequest(id=request_id, method=method, params=params)
        future: asyncio.Future[JsonRpcResponse] = asyncio.get_running_loop().create_future()
        self._pending[request_id] = future

        line = payload.model_dump_json(exclude_none=True) + "\n"
        self._process.stdin.write(line.encode("utf-8"))
        await self._process.stdin.drain()

        response = await future
        if response.error is not None:
            raise MCPError(
                response.error.message,
                code=response.error.code,
                data=response.error.data,
            )
        return response.result

    async def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        if self._process is None or self._process.stdin is None:
            raise RuntimeError("Transport not started")
        line = serialize_notification(method, params) + "\n"
        self._process.stdin.write(line.encode("utf-8"))
        await self._process.stdin.drain()

    async def read_message(self) -> IncomingMessage | None:
        return await self._incoming.get()

    async def write_raw(self, payload: str) -> None:
        raise NotImplementedError("Client transport uses request/notify instead")

    async def close(self) -> None:
        if self._process is None:
            return
        if self._process.stdin:
            self._process.stdin.close()
            await self._process.stdin.wait_closed()
        self._process.terminate()
        await self._process.wait()
        if self._reader_task:
            await self._reader_task
