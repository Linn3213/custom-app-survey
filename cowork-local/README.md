# Cowork Local

A small, self-hosted app that does what Claude **Cowork + Dispatch** do — send a
task from your phone, have it run on your own computer against your local files
and shell — but built on the **Claude API** and run entirely by you.

It runs a local web server on your machine, serves a mobile-friendly UI, and uses
an agentic Claude loop (Opus 4.8) to carry out tasks. Risky actions pause for your
approval; read-only inspection runs on its own. Because the loop runs in the
server process on your computer, you keep Dispatch's core idea — *kick off work
from your phone, come back to a finished result* — without depending on the
desktop app being awake in any particular state.

## How it compares

| | Cowork + Dispatch | **Cowork Local** |
|---|---|---|
| Runs the agent loop | Anthropic's apps | **Your machine** (this server) |
| Reaches local files / shell | ✅ | ✅ (confined to a workspace) |
| Drive from phone | ✅ | ✅ (web UI + tunnel) |
| Approval gate for risky actions | ✅ | ✅ |
| You own/host it | ❌ | ✅ |
| Needs a Max subscription | ✅ | ❌ — uses an Anthropic API key |

## Safety model

- **Workspace confinement.** Every file read/write and the shell working
  directory are restricted to the directories in `COWORK_ROOTS`
  (default `~/CoworkLocal`). Paths outside are rejected.
- **Confirmation gate.** Non-trivial shell commands, file overwrites, and edits
  pause for an Allow/Deny decision in the UI. Read-only commands (`ls`, `cat`,
  `git status`, …) and new-file writes run automatically.
- **Hard blocks.** A few catastrophic patterns (`rm -rf /`, fork bombs, `mkfs`,
  `shutdown`, …) are refused outright, even if you would have approved them.
- **Token auth.** The UI must present a shared token. Bind to `127.0.0.1` by
  default; only expose it deliberately (see below).
- **`auto-approve`** is available as a toggle for power users — it skips the
  confirmation gate. Leave it off unless you're running in a throwaway sandbox.

> This grants an LLM access to run commands on your computer. Treat it like
> giving someone shell access. Keep the workspace narrow, leave auto-approve off,
> and don't expose it to the public internet without a tunnel that adds auth.

## Setup

```bash
cd cowork-local
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then add your ANTHROPIC_API_KEY
python -m coworklocal
```

The console prints a local URL and an access token. Open the URL, paste the
token, and start sending tasks.

## Using it from your phone

The server binds to `127.0.0.1` by default. To reach it from your phone, either:

1. **Tunnel (recommended).** With the server running locally:
   ```bash
   cloudflared tunnel --url http://localhost:8765
   ```
   Open the printed `https://…trycloudflare.com` URL on your phone and paste the
   token. (Any tunnel works — ngrok, Tailscale Funnel, etc.)
2. **Same Wi-Fi.** Start with `python -m coworklocal --host 0.0.0.0` and browse
   to `http://<your-computer-ip>:8765` from your phone. Only do this on a network
   you trust.

The event stream replays on reconnect, so the phone can drop off Wi-Fi and pick
the session back up where it left off.

## Configuration

All optional, via `.env` or environment variables — see `.env.example`.

| Variable | Default | Meaning |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | **Required.** Your API key. |
| `COWORK_TOKEN` | random | Access token the UI must present. |
| `COWORK_ROOTS` | `~/CoworkLocal` | `:`-separated workspace roots. |
| `COWORK_MODEL` | `claude-opus-4-8` | Model id. |
| `COWORK_EFFORT` | `high` | Reasoning effort (`low`–`max`). |
| `COWORK_MAX_TOKENS` | `32000` | Max output tokens per turn. |
| `COWORK_SHELL_TIMEOUT` | `120` | Per-command timeout (seconds). |
| `COWORK_AUTO_APPROVE` | `0` | Start with the approval gate off. |

## Architecture

```
coworklocal/
  config.py    settings from env / .env
  safety.py    shell-command classification (safe / confirm / block)
  tools.py     file + shell tools, workspace confinement, tool schemas
  session.py   event bus (with replay) + per-session state
  agent.py     Claude streaming agentic loop + approval gating
  server.py    FastAPI: SSE stream, message/approve/interrupt endpoints
  static/      mobile web UI (vanilla JS + EventSource)
```

The agent uses adaptive thinking and a manual tool-use loop so each risky tool
call can be intercepted and gated before it runs.
