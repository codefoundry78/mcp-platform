"""MCP protocol type definitions."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

PROTOCOL_VERSION = "2025-06-18"


class Implementation(BaseModel):
    name: str
    version: str


class ClientCapabilities(BaseModel):
    model_config = ConfigDict(extra="allow")

    roots: dict[str, Any] | None = None
    sampling: dict[str, Any] | None = None


class ServerCapabilities(BaseModel):
    model_config = ConfigDict(extra="allow")

    tools: dict[str, Any] | None = None
    resources: dict[str, Any] | None = None
    prompts: dict[str, Any] | None = None
    logging: dict[str, Any] | None = None


class InitializeParams(BaseModel):
    protocolVersion: str
    capabilities: ClientCapabilities = Field(default_factory=ClientCapabilities)
    clientInfo: Implementation


class InitializeResult(BaseModel):
    protocolVersion: str = PROTOCOL_VERSION
    capabilities: ServerCapabilities
    serverInfo: Implementation


class Tool(BaseModel):
    name: str
    description: str
    inputSchema: dict[str, Any] = Field(default_factory=dict)


class ToolsListParams(BaseModel):
    cursor: str | None = None


class ToolsListResult(BaseModel):
    tools: list[Tool]
    nextCursor: str | None = None


class TextContent(BaseModel):
    type: Literal["text"] = "text"
    text: str


ContentBlock = TextContent


class ToolsCallParams(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolsCallResult(BaseModel):
    content: list[ContentBlock]
    isError: bool = False


class ResourcesListResult(BaseModel):
    resources: list[dict[str, Any]] = Field(default_factory=list)
    nextCursor: str | None = None


class PromptsListResult(BaseModel):
    prompts: list[dict[str, Any]] = Field(default_factory=list)
    nextCursor: str | None = None
