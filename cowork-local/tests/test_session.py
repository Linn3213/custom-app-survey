from conftest import run

from coworklocal.session import EventBus, Session


def test_eventbus_emit_assigns_incrementing_ids():
    bus = EventBus()
    a = bus.emit("status", status="idle")
    b = bus.emit("user", text="hi")
    assert a["id"] == 1 and b["id"] == 2
    assert b["type"] == "user" and b["text"] == "hi"


def test_eventbus_replays_history_from_last_id():
    bus = EventBus()
    bus.emit("a")
    bus.emit("b")
    bus.emit("c")

    async def collect_backlog(last_id, count):
        gen = bus.subscribe(last_id)
        out = [await anext(gen) for _ in range(count)]
        await gen.aclose()
        return out

    # From the start: all three replay.
    events = run(collect_backlog(0, 3))
    assert [e["type"] for e in events] == ["a", "b", "c"]

    # From id=2: only the third event replays.
    events = run(collect_backlog(2, 1))
    assert [e["type"] for e in events] == ["c"]


def test_eventbus_live_delivery():
    bus = EventBus()

    async def scenario():
        gen = bus.subscribe(0)
        bus.emit("live", n=1)
        event = await anext(gen)
        await gen.aclose()
        return event

    event = run(scenario())
    assert event["type"] == "live" and event["n"] == 1


def test_session_status_emits_event(settings):
    session = Session(settings)
    session.set_status("running")
    assert session.status == "running"
    assert session.bus._history[-1] == {"id": 1, "type": "status", "status": "running"}


def test_resolve_approval(settings):
    session = Session(settings)

    async def scenario():
        import asyncio

        fut = asyncio.get_event_loop().create_future()
        session.pending["tool-1"] = fut
        assert session.resolve_approval("tool-1", "allow") is True
        assert await fut == "allow"
        # Unknown id returns False.
        assert session.resolve_approval("missing", "deny") is False

    run(scenario())
