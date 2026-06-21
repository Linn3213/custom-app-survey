import pytest

pytest.importorskip("fastapi")
pytest.importorskip("anthropic")

from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-dummy")
    monkeypatch.setenv("COWORK_TOKEN", "secret")
    monkeypatch.setenv("COWORK_ROOTS", str(tmp_path))
    from coworklocal.config import load_settings
    from coworklocal.server import create_app

    return TestClient(create_app(load_settings()))


def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200 and r.json() == {"ok": True}


def test_index_served(client):
    assert client.get("/").status_code == 200


def test_events_requires_token(client):
    assert client.get("/api/events").status_code == 401
    assert client.get("/api/events?token=wrong").status_code == 401


def test_message_requires_auth(client):
    assert client.post("/api/message", json={"text": "hi"}).status_code == 401
    assert client.post(
        "/api/message", headers={"Authorization": "Bearer wrong"}, json={"text": "hi"}
    ).status_code == 401


def test_empty_message_rejected(client):
    r = client.post("/api/message", headers={"Authorization": "Bearer secret"}, json={"text": "  "})
    assert r.status_code == 400


def test_settings_toggle(client):
    r = client.post(
        "/api/settings", headers={"Authorization": "Bearer secret"}, json={"auto_approve": True}
    )
    assert r.status_code == 200 and r.json()["auto_approve"] is True


def test_approve_unknown_pending_returns_404(client):
    r = client.post(
        "/api/approve",
        headers={"Authorization": "Bearer secret"},
        json={"id": "nope", "decision": "allow"},
    )
    assert r.status_code == 404


def test_approve_invalid_decision_rejected(client):
    r = client.post(
        "/api/approve",
        headers={"Authorization": "Bearer secret"},
        json={"id": "x", "decision": "maybe"},
    )
    assert r.status_code == 400
