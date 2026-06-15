"""Filesystem server configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FilesystemConfig:
    root: Path

    @classmethod
    def from_env(cls) -> FilesystemConfig:
        root = Path(os.environ.get("MCP_FS_ROOT", "./workspace"))
        return cls(root=root)
