"""MCP prompts/list handler."""

from __future__ import annotations

from core.sdk.types import PromptsListResult


async def handle_prompts_list() -> PromptsListResult:
    return PromptsListResult()
