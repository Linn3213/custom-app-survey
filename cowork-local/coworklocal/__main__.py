"""Entry point: ``python -m coworklocal``."""

from __future__ import annotations

import argparse

import uvicorn

from .config import load_settings
from .server import create_app


def main() -> None:
    settings = load_settings()
    parser = argparse.ArgumentParser(description="Cowork Local — drive your computer from your phone.")
    parser.add_argument("--host", default=settings.host,
                        help="Bind address. Use 0.0.0.0 to allow other devices on your network.")
    parser.add_argument("--port", type=int, default=settings.port)
    args = parser.parse_args()

    settings.host = args.host
    settings.port = args.port
    app = create_app(settings)

    banner = "\n".join([
        "",
        "  Cowork Local is running.",
        f"  Local URL : http://{args.host}:{args.port}/",
        f"  Token     : {settings.token}",
        f"  Workspace : {', '.join(str(r) for r in settings.roots)}",
        "",
        "  Open the URL on this machine, or expose it to your phone with a",
        "  tunnel (e.g. `cloudflared tunnel --url http://localhost:%d`)." % args.port,
        "  Paste the token above when the page asks for it.",
        "",
    ])
    print(banner)

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
