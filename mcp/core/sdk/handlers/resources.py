"""MCP resources/list handler."""

from __future__ import annotations

from core.sdk.types import ResourcesListResult


async def handle_resources_list() -> ResourcesListResult:
    return ResourcesListResult()
