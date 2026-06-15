"""Stdio transport for MCP servers."""

from __future__ import annotations

import asyncio
import sys
from typing import TextIO

from core.sdk.codec import IncomingMessage, parse_message
from core.sdk.transports.base import Transport


class StdioTransport(Transport):
    """Read/write newline-delimited JSON-RPC over stdin/stdout."""

    def __init__(
        self,
        reader: asyncio.StreamReader | None = None,
        writer: TextIO | None = None,
    ) -> None:
        self._reader = reader
        self._writer = writer or sys.stdout
        self._write_lock = asyncio.Lock()

    async def read_message(self) -> IncomingMessage | None:
        if self._reader is None:
            line = await asyncio.to_thread(sys.stdin.readline)
        else:
            line_bytes = await self._reader.readline()
            if not line_bytes:
                return None
            line = line_bytes.decode("utf-8")

        if not line:
            return None
        return parse_message(line.strip())

    async def write_raw(self, payload: str) -> None:
        async with self._write_lock:
            await asyncio.to_thread(self._writer.write, payload + "\n")
            await asyncio.to_thread(self._writer.flush)

    async def close(self) -> None:
        if self._reader is None:
            return
        self._reader.feed_eof()
