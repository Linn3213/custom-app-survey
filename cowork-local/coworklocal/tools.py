"""Tool definitions and implementations, confined to the workspace roots.

Each tool returns ``(output_text, is_error)``. File operations and the shell
working directory are confined to the configured roots so the agent cannot
wander across the whole filesystem.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from .config import Settings
from .safety import classify_command

# JSON-schema tool definitions handed to the Claude API.
TOOL_SCHEMAS = [
    {
        "name": "list_directory",
        "description": "List the entries in a directory within the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path, relative to the workspace root or absolute within it."}
            },
            "required": ["path"],
        },
    },
    {
        "name": "read_file",
        "description": "Read a UTF-8 text file within the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to read."}
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Create or overwrite a text file within the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to write."},
                "content": {"type": "string", "description": "Full file contents."},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "edit_file",
        "description": "Replace the first exact occurrence of old_string with new_string in a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old_string": {"type": "string", "description": "Exact text to find (must be unique enough to match once)."},
                "new_string": {"type": "string", "description": "Replacement text."},
            },
            "required": ["path", "old_string", "new_string"],
        },
    },
    {
        "name": "run_shell",
        "description": "Run a shell command. The working directory is confined to the workspace. Destructive commands require user approval.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The shell command to run."},
                "workdir": {"type": "string", "description": "Optional working directory within the workspace."},
            },
            "required": ["command"],
        },
    },
]


class Workspace:
    def __init__(self, roots: list[Path]):
        self.roots = [r.resolve() for r in roots]
        self.default_root = self.roots[0]

    def resolve(self, path: str) -> Path:
        raw = Path(path).expanduser()
        candidate = raw if raw.is_absolute() else (self.default_root / raw)
        candidate = candidate.resolve()
        for root in self.roots:
            if candidate == root or root in candidate.parents:
                return candidate
        raise PermissionError(
            f"Path '{path}' is outside the allowed workspace roots."
        )


class Tools:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.workspace = Workspace(settings.roots)

    async def execute(self, name: str, args: dict) -> tuple[str, bool]:
        try:
            if name == "list_directory":
                return await asyncio.to_thread(self._list_directory, args["path"])
            if name == "read_file":
                return await asyncio.to_thread(self._read_file, args["path"])
            if name == "write_file":
                return await asyncio.to_thread(self._write_file, args["path"], args["content"])
            if name == "edit_file":
                return await asyncio.to_thread(
                    self._edit_file, args["path"], args["old_string"], args["new_string"]
                )
            if name == "run_shell":
                return await self._run_shell(args["command"], args.get("workdir"))
            return (f"Unknown tool: {name}", True)
        except Exception as exc:  # surfaced back to the model as a tool error
            return (f"{type(exc).__name__}: {exc}", True)

    # -- file tools --------------------------------------------------------

    def _list_directory(self, path: str) -> tuple[str, bool]:
        target = self.workspace.resolve(path)
        if not target.exists():
            return (f"No such directory: {path}", True)
        if not target.is_dir():
            return (f"Not a directory: {path}", True)
        entries = []
        for child in sorted(target.iterdir()):
            suffix = "/" if child.is_dir() else ""
            try:
                size = child.stat().st_size
            except OSError:
                size = 0
            entries.append(f"{child.name}{suffix}\t{size}")
        return ("\n".join(entries) or "(empty)", False)

    def _read_file(self, path: str) -> tuple[str, bool]:
        target = self.workspace.resolve(path)
        if not target.exists() or not target.is_file():
            return (f"No such file: {path}", True)
        data = target.read_bytes()[: self.settings.max_read_bytes]
        text = data.decode("utf-8", errors="replace")
        if target.stat().st_size > self.settings.max_read_bytes:
            text += "\n... [truncated]"
        return (text, False)

    def _write_file(self, path: str, content: str) -> tuple[str, bool]:
        target = self.workspace.resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        existed = target.exists()
        target.write_text(content, encoding="utf-8")
        verb = "Overwrote" if existed else "Created"
        return (f"{verb} {target} ({len(content)} bytes).", False)

    def _edit_file(self, path: str, old: str, new: str) -> tuple[str, bool]:
        target = self.workspace.resolve(path)
        if not target.exists() or not target.is_file():
            return (f"No such file: {path}", True)
        text = target.read_text(encoding="utf-8")
        count = text.count(old)
        if count == 0:
            return ("old_string not found in file.", True)
        if count > 1:
            return (f"old_string matched {count} times; make it more specific.", True)
        target.write_text(text.replace(old, new, 1), encoding="utf-8")
        return (f"Edited {target}.", False)

    # -- shell tool --------------------------------------------------------

    async def _run_shell(self, command: str, workdir: str | None) -> tuple[str, bool]:
        if classify_command(command) == "block":
            return ("This command is blocked by the safety policy.", True)
        cwd = self.workspace.resolve(workdir) if workdir else self.settings.default_root
        if not cwd.is_dir():
            return (f"Working directory does not exist: {workdir}", True)
        proc = await asyncio.create_subprocess_shell(
            command,
            cwd=str(cwd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env={**os.environ, "GIT_PAGER": "cat", "PAGER": "cat"},
        )
        try:
            stdout, _ = await asyncio.wait_for(
                proc.communicate(), timeout=self.settings.shell_timeout
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            return (f"Command timed out after {self.settings.shell_timeout}s.", True)
        output = stdout.decode("utf-8", errors="replace")
        if len(output) > self.settings.max_read_bytes:
            output = output[: self.settings.max_read_bytes] + "\n... [truncated]"
        footer = f"\n[exit code: {proc.returncode}]"
        return (output + footer, proc.returncode != 0)


def needs_confirmation(name: str, tool_input: dict, settings: Settings, workspace: Workspace) -> bool:
    """Decide whether a non-shell tool call must be confirmed by the user."""
    if name in {"read_file", "list_directory"}:
        return False
    if name == "write_file":
        # Confirm overwrites of existing files; allow creating new ones.
        try:
            return workspace.resolve(tool_input.get("path", "")).exists()
        except PermissionError:
            return True
    if name == "edit_file":
        return True
    return True
