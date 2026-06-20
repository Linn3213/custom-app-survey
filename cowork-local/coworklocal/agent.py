"""The Claude agentic loop: stream a turn, run tools, gate risky ones, repeat."""

from __future__ import annotations

import asyncio
from typing import Any

from anthropic import AsyncAnthropic

from .config import Settings
from .safety import classify_command, describe_risk
from .session import Session
from .tools import TOOL_SCHEMAS, Tools, needs_confirmation

SYSTEM_PROMPT = """You are Cowork Local, an assistant that operates the user's own \
computer to complete tasks they send from their phone.

You work through tools: list_directory, read_file, write_file, edit_file, and \
run_shell. All file access and shell commands are confined to a fixed workspace; \
paths outside it are rejected, so stay inside it.

Risky actions (overwriting files, editing files, and non-trivial shell commands) \
pause for the user to approve in the app. Read-only inspection runs automatically. \
Plan briefly, act, and verify your own work (e.g. read a file back, check an exit \
code). For minor choices, pick a sensible option and note it rather than asking. \
When the task is done, give a short, plain-language summary of what changed — the \
user has been away and this is their first look at the result."""


class Agent:
    def __init__(self, settings: Settings, tools: Tools, client: AsyncAnthropic):
        self.settings = settings
        self.tools = tools
        self.client = client

    async def handle_message(self, session: Session, text: str) -> None:
        if session.task and not session.task.done():
            session.bus.emit("error", message="The agent is busy. Interrupt it first.")
            return
        session.bus.emit("user", text=text)
        session.messages.append({"role": "user", "content": text})
        session.task = asyncio.create_task(self._run(session))

    async def _run(self, session: Session) -> None:
        try:
            session.set_status("running")
            while True:
                message = await self._stream_turn(session)
                session.messages.append({"role": "assistant", "content": message.content})

                if message.stop_reason != "tool_use":
                    session.set_status("idle")
                    session.bus.emit("done", stop_reason=message.stop_reason)
                    return

                results: list[dict[str, Any]] = []
                for block in message.content:
                    if getattr(block, "type", None) == "tool_use":
                        results.append(await self._exec_tool(session, block))
                session.messages.append({"role": "user", "content": results})
        except asyncio.CancelledError:
            session.set_status("idle")
            session.bus.emit("error", message="Interrupted.")
            raise
        except Exception as exc:
            session.set_status("error")
            session.bus.emit("error", message=f"{type(exc).__name__}: {exc}")

    async def _stream_turn(self, session: Session):
        session.set_status("thinking")
        async with self.client.messages.stream(
            model=self.settings.model,
            max_tokens=self.settings.max_tokens,
            system=SYSTEM_PROMPT,
            thinking={"type": "adaptive", "display": "summarized"},
            output_config={"effort": self.settings.effort},
            tools=TOOL_SCHEMAS,
            messages=session.messages,
        ) as stream:
            async for event in stream:
                if event.type == "content_block_delta":
                    delta = event.delta
                    if delta.type == "text_delta":
                        session.bus.emit("assistant_delta", text=delta.text)
                    elif delta.type == "thinking_delta":
                        session.bus.emit("thinking_delta", text=delta.thinking)
                elif event.type == "content_block_stop":
                    session.bus.emit("block_stop")
            return await stream.get_final_message()

    async def _exec_tool(self, session: Session, block: Any) -> dict[str, Any]:
        name = block.name
        tool_input = block.input or {}
        tool_id = block.id

        if name == "run_shell":
            verdict = classify_command(tool_input.get("command", ""))
            if verdict == "block":
                session.bus.emit("tool_result", id=tool_id, name=name,
                                 output="Blocked by safety policy.", is_error=True)
                return self._result(tool_id, "This command is blocked by the safety policy.", True)
            need = verdict == "confirm"
        else:
            need = needs_confirmation(name, tool_input, self.settings, self.tools.workspace)

        if session.auto_approve:
            need = False

        session.bus.emit("tool_use", id=tool_id, name=name, input=tool_input,
                         decision="pending" if need else "auto")

        if need:
            decision = await self._await_approval(session, tool_id, name, tool_input)
            if decision != "allow":
                session.bus.emit("tool_result", id=tool_id, name=name,
                                 output="Denied by user.", is_error=False)
                return self._result(
                    tool_id,
                    "The user denied this action. Do not retry it; consider another approach.",
                    False,
                )

        output, is_error = await self.tools.execute(name, tool_input)
        session.bus.emit("tool_result", id=tool_id, name=name, output=output, is_error=is_error)
        return self._result(tool_id, output, is_error)

    async def _await_approval(self, session: Session, tool_id: str, name: str, tool_input: dict) -> str:
        future: asyncio.Future = asyncio.get_event_loop().create_future()
        session.pending[tool_id] = future
        session.set_status("awaiting_approval")
        session.bus.emit("approval_required", id=tool_id, name=name,
                         input=tool_input, risk=describe_risk(name, tool_input))
        try:
            decision = await future
        finally:
            session.pending.pop(tool_id, None)
        session.bus.emit("approval_resolved", id=tool_id, decision=decision)
        session.set_status("running")
        return decision

    @staticmethod
    def _result(tool_use_id: str, content: str, is_error: bool) -> dict[str, Any]:
        return {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": content,
            "is_error": is_error,
        }
