"""Classify shell commands and describe the risk of an action.

Three outcomes for a shell command:
  - "safe"    : read-only / informational — runs without asking
  - "confirm" : anything else — requires explicit approval in the UI
  - "block"   : obviously destructive — refused outright, even with approval
"""

from __future__ import annotations

import re
import shlex

# Patterns that are refused no matter what. Keep this conservative: it is a
# backstop against catastrophic mistakes, not a substitute for the confirm gate.
_ALWAYS_BLOCK = [
    re.compile(r"\brm\b[^|;&]*\s-\w*[rf]\w*\s+(/|~|\$HOME)(\s|/|$)"),
    re.compile(r":\s*\(\s*\)\s*\{"),          # fork bomb :(){ :|:& };:
    re.compile(r"\bmkfs\.\w+"),
    re.compile(r"\bdd\b[^|;&]*\bof=/dev/"),
    re.compile(r">\s*/dev/(sd|nvme|disk)"),
    re.compile(r"\b(shutdown|reboot|halt|poweroff)\b"),
    re.compile(r"\bchmod\b\s+-R\s+0?00\s+/"),
]

# First tokens that are read-only / safe to run unattended.
_SAFE_COMMANDS = {
    "ls", "pwd", "echo", "cat", "head", "tail", "wc", "stat", "file",
    "find", "grep", "rg", "tree", "du", "df", "date", "whoami", "id",
    "uname", "hostname", "which", "type", "basename", "dirname", "realpath",
    "cut", "sort", "uniq", "diff", "sed", "awk", "jq", "md5sum", "sha256sum",
    "python", "python3", "node", "ruby", "go", "cargo", "npm", "pip", "pip3",
}

# Subcommands that are safe for tools that have both read and write modes.
_SAFE_SUBCOMMANDS = {
    "git": {"status", "log", "diff", "show", "branch", "remote", "rev-parse",
            "describe", "blame", "config", "ls-files", "shortlog", "tag"},
    "npm": {"ls", "list", "view", "outdated", "test"},
    "pip": {"list", "show", "freeze"},
    "pip3": {"list", "show", "freeze"},
    "cargo": {"tree", "metadata", "check"},
    "go": {"version", "env", "list", "vet"},
}

# Shell metacharacters that mean "this is more than a single simple command".
_HAS_SHELL_OPS = re.compile(r"[|&;><`]|\$\(")


def classify_command(command: str) -> str:
    text = (command or "").strip()
    if not text:
        return "confirm"

    for pattern in _ALWAYS_BLOCK:
        if pattern.search(text):
            return "block"

    # Anything with pipes/redirects/substitution is not auto-safe.
    if _HAS_SHELL_OPS.search(text):
        return "confirm"

    try:
        tokens = shlex.split(text)
    except ValueError:
        return "confirm"
    if not tokens:
        return "confirm"

    head = tokens[0]
    sub = next((t for t in tokens[1:] if not t.startswith("-")), None)

    if head in _SAFE_SUBCOMMANDS:
        return "safe" if sub in _SAFE_SUBCOMMANDS[head] else "confirm"
    if head in _SAFE_COMMANDS:
        # `python -c "..."` / `--version` etc. can do anything, so only treat a
        # plain version/help probe or a script read as safe.
        if head in {"python", "python3", "node", "ruby"}:
            flags = {t for t in tokens[1:] if t.startswith("-")}
            if flags & {"-c", "-m", "-e"} or "-" in tokens[1:]:
                return "confirm"
            return "safe"
        return "safe"
    return "confirm"


def describe_risk(tool_name: str, tool_input: dict) -> str:
    if tool_name == "run_shell":
        return f"Run shell command: {tool_input.get('command', '')}"
    if tool_name == "write_file":
        return f"Overwrite file: {tool_input.get('path', '')}"
    if tool_name == "edit_file":
        return f"Edit file: {tool_input.get('path', '')}"
    return f"{tool_name}: {tool_input}"
