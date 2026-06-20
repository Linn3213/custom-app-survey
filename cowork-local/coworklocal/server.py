"""FastAPI server: static UI, SSE event stream, message + approval endpoints."""

from __future__ import annotations

import json
from pathlib import Path

from anthropic import AsyncAnthropic
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

from .agent import Agent
from .config import Settings, load_settings
from .session import SessionManager
from .tools import Tools

STATIC_DIR = Path(__file__).parent / "static"


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    client = AsyncAnthropic()
    tools = Tools(settings)
    agent = Agent(settings, tools, client)
    manager = SessionManager(settings)

    app = FastAPI(title="Cowork Local")

    def check_token(provided: str | None) -> None:
        if not provided or provided != settings.token:
            raise HTTPException(status_code=401, detail="Invalid or missing token.")

    def bearer(authorization: str | None) -> str | None:
        if authorization and authorization.lower().startswith("bearer "):
            return authorization[7:].strip()
        return None

    @app.get("/")
    async def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/healthz")
    async def healthz() -> dict:
        return {"ok": True}

    @app.get("/api/events")
    async def events(request: Request, token: str | None = None):
        check_token(token)
        session = manager.session
        last_event_id = request.headers.get("last-event-id")
        last_id = int(last_event_id) if last_event_id and last_event_id.isdigit() else 0

        async def stream():
            # Snapshot first so a fresh client knows the current state.
            snapshot = {
                "type": "snapshot",
                "status": session.status,
                "auto_approve": session.auto_approve,
                "roots": [str(r) for r in settings.roots],
                "model": settings.model,
            }
            yield f"data: {json.dumps(snapshot)}\n\n"
            async for event in session.bus.subscribe(last_id):
                yield f"id: {event['id']}\ndata: {json.dumps(event)}\n\n"

        return StreamingResponse(
            stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    @app.post("/api/message")
    async def message(request: Request, authorization: str | None = Header(default=None)):
        check_token(bearer(authorization))
        body = await request.json()
        text = (body.get("text") or "").strip()
        if not text:
            raise HTTPException(status_code=400, detail="Empty message.")
        await agent.handle_message(manager.session, text)
        return {"ok": True}

    @app.post("/api/approve")
    async def approve(request: Request, authorization: str | None = Header(default=None)):
        check_token(bearer(authorization))
        body = await request.json()
        tool_use_id = body.get("id")
        decision = body.get("decision")
        if decision not in {"allow", "deny"}:
            raise HTTPException(status_code=400, detail="decision must be allow or deny.")
        ok = manager.session.resolve_approval(tool_use_id, decision)
        if not ok:
            raise HTTPException(status_code=404, detail="No such pending approval.")
        return {"ok": True}

    @app.post("/api/interrupt")
    async def interrupt(authorization: str | None = Header(default=None)):
        check_token(bearer(authorization))
        await manager.session.interrupt()
        return {"ok": True}

    @app.post("/api/settings")
    async def update_settings(request: Request, authorization: str | None = Header(default=None)):
        check_token(bearer(authorization))
        body = await request.json()
        session = manager.session
        if "auto_approve" in body:
            session.auto_approve = bool(body["auto_approve"])
            session.bus.emit("settings", auto_approve=session.auto_approve)
        return {"ok": True, "auto_approve": session.auto_approve}

    return app
