"""Configuration loaded from the environment (and an optional .env file)."""

from __future__ import annotations

import os
import secrets
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # python-dotenv is optional
    pass


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _resolve_roots(raw: str | None) -> list[Path]:
    if raw:
        parts = [p for p in raw.split(os.pathsep) if p.strip()]
    else:
        parts = [str(Path.home() / "CoworkLocal")]
    roots: list[Path] = []
    for part in parts:
        root = Path(part).expanduser().resolve()
        root.mkdir(parents=True, exist_ok=True)
        roots.append(root)
    return roots


@dataclass
class Settings:
    model: str = "claude-opus-4-8"
    effort: str = "high"
    max_tokens: int = 32000
    shell_timeout: int = 120
    max_read_bytes: int = 200_000
    host: str = "127.0.0.1"
    port: int = 8765
    token: str = ""
    roots: list[Path] = field(default_factory=list)
    auto_approve_default: bool = False

    @property
    def default_root(self) -> Path:
        return self.roots[0]


def load_settings() -> Settings:
    roots = _resolve_roots(os.environ.get("COWORK_ROOTS"))
    token = os.environ.get("COWORK_TOKEN", "").strip() or secrets.token_urlsafe(24)
    return Settings(
        model=os.environ.get("COWORK_MODEL", "claude-opus-4-8"),
        effort=os.environ.get("COWORK_EFFORT", "high"),
        max_tokens=int(os.environ.get("COWORK_MAX_TOKENS", "32000")),
        shell_timeout=int(os.environ.get("COWORK_SHELL_TIMEOUT", "120")),
        host=os.environ.get("COWORK_HOST", "127.0.0.1"),
        port=int(os.environ.get("COWORK_PORT", "8765")),
        token=token,
        roots=roots,
        auto_approve_default=_env_bool("COWORK_AUTO_APPROVE", False),
    )
