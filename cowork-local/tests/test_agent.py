"""End-to-end test of the agent loop against a mocked Anthropic client.

Drives a full turn (assistant streams text, requests a tool that needs
approval, we approve/deny, the tool runs, the agent finishes) without touching
the network — proving the agentic loop and the approval gate work together.
"""

import asyncio
from types import SimpleNamespace

from conftest import run

from coworklocal.agent import Agent
from coworklocal.config import Settings
from coworklocal.session import Session
from coworklocal.tools import Tools


class FakeStream:
    """Stands in for `client.messages.stream(...)` — async CM + async iterator."""

    def __init__(self, deltas, final):
        self._deltas = deltas
        self._final = final

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def __aiter__(self):
        for event in self._deltas:
            yield event

    async def get_final_message(self):
        return self._final


class FakeMessages:
    def __init__(self, turns):
        self._turns = list(turns)
        self.calls = []

    def stream(self, **kwargs):
        self.calls.append(kwargs)
        return self._turns.pop(0)


class FakeClient:
    def __init__(self, turns):
        self.messages = FakeMessages(turns)


def _text_delta(text):
    return SimpleNamespace(
        type="content_block_delta", delta=SimpleNamespace(type="text_delta", text=text)
    )


def _tool_use(tool_id, name, tool_input):
    return SimpleNamespace(type="tool_use", id=tool_id, name=name, input=tool_input)


def _msg(content, stop_reason):
    return SimpleNamespace(content=content, stop_reason=stop_reason)


async def _wait_for(session, event_type, timeout=2.0):
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        for event in session.bus._history:
            if event["type"] == event_type:
                return event
        await asyncio.sleep(0.01)
    raise AssertionError(f"event {event_type!r} never arrived")


def _build(tmp_path, turns):
    settings = Settings(token="t", roots=[tmp_path.resolve()])
    tools = Tools(settings)
    agent = Agent(settings, tools, FakeClient(turns))
    return settings, tools, agent, Session(settings)


def test_agent_runs_tool_after_approval(tmp_path):
    # Pre-create a file so write_file is an overwrite (requires approval).
    (tmp_path / "f.txt").write_text("OLD")

    turns = [
        FakeStream(
            [_text_delta("Updating the file")],
            _msg([_tool_use("tu_1", "write_file", {"path": "f.txt", "content": "NEW"})], "tool_use"),
        ),
        FakeStream([_text_delta("Done.")], _msg([SimpleNamespace(type="text")], "end_turn")),
    ]

    async def scenario():
        _, _, agent, session = _build(tmp_path, turns)
        await agent.handle_message(session, "update f.txt")
        approval = await _wait_for(session, "approval_required")
        assert approval["name"] == "write_file"
        session.resolve_approval(approval["id"], "allow")
        await session.task
        return session

    session = run(scenario())
    types = [e["type"] for e in session.bus._history]
    assert "approval_required" in types
    assert "approval_resolved" in types
    assert types[-1] == "done"
    assert (tmp_path / "f.txt").read_text() == "NEW"  # tool actually ran


def test_agent_skips_tool_when_denied(tmp_path):
    (tmp_path / "f.txt").write_text("OLD")

    turns = [
        FakeStream(
            [],
            _msg([_tool_use("tu_1", "write_file", {"path": "f.txt", "content": "NEW"})], "tool_use"),
        ),
        FakeStream([], _msg([SimpleNamespace(type="text")], "end_turn")),
    ]

    async def scenario():
        _, _, agent, session = _build(tmp_path, turns)
        await agent.handle_message(session, "update f.txt")
        approval = await _wait_for(session, "approval_required")
        session.resolve_approval(approval["id"], "deny")
        await session.task
        return session

    session = run(scenario())
    result = [e for e in session.bus._history if e["type"] == "tool_result"][-1]
    assert "Denied" in result["output"]
    assert (tmp_path / "f.txt").read_text() == "OLD"  # tool did NOT run


def test_agent_auto_runs_safe_tool_without_approval(tmp_path):
    turns = [
        FakeStream(
            [],
            _msg([_tool_use("tu_1", "run_shell", {"command": "echo hi"})], "tool_use"),
        ),
        FakeStream([], _msg([SimpleNamespace(type="text")], "end_turn")),
    ]

    async def scenario():
        _, _, agent, session = _build(tmp_path, turns)
        await agent.handle_message(session, "say hi")
        await session.task
        return session

    session = run(scenario())
    types = [e["type"] for e in session.bus._history]
    assert "approval_required" not in types  # safe command auto-ran
    result = [e for e in session.bus._history if e["type"] == "tool_result"][-1]
    assert "hi" in result["output"]
