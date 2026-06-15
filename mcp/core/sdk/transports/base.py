"""Transport abstractions for MCP message exchange."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.sdk.codec import IncomingMessage


class Transport(ABC):
    @abstractmethod
    async def read_message(self) -> IncomingMessage | None:
        """Read the next message. Return None when the transport is closed."""

    @abstractmethod
    async def write_raw(self, payload: str) -> None:
        """Write a serialized JSON-RPC payload."""

    async def close(self) -> None:
        return None
