"""Lightweight mobile discovery sidecar.

Starts a minimal HTTP server (discover + ws placeholder) and UDP broadcast
in a daemon thread. Works independently of the channel system so the Android
app can always find the host, even in interactive mode.
"""

from __future__ import annotations

import asyncio
import json
import logging
import secrets
import socket
import threading
from typing import TYPE_CHECKING

from aiohttp import web

if TYPE_CHECKING:
    from ...config.settings import RxscientistConfig

logger = logging.getLogger(__name__)

_sidecar_thread: threading.Thread | None = None


def start_mobile_sidecar(config: RxscientistConfig) -> str | None:
    """Start the mobile sidecar in a daemon thread. Returns the token used."""
    global _sidecar_thread
    if _sidecar_thread is not None and _sidecar_thread.is_alive():
        return None

    host = config.mobile_host or "0.0.0.0"
    port = int(config.mobile_port or 8765)
    token = config.mobile_token or secrets.token_urlsafe(16)
    broadcast_port = 8766

    def _run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_serve(host, port, token, broadcast_port))
        except Exception:
            logger.exception("Mobile sidecar crashed")

    _sidecar_thread = threading.Thread(target=_run, daemon=True, name="mobile-sidecar")
    _sidecar_thread.start()
    return token


async def _serve(host: str, port: int, token: str, broadcast_port: int):
    app = web.Application()

    async def _discover(request: web.Request) -> web.StreamResponse:
        base_url = f"http://{request.host}"
        return web.json_response({
            "service": "rxsci-mobile",
            "name": "RxSci Mobile Channel",
            "version": "1",
            "base_url": base_url,
            "host": host,
            "port": port,
            "token": token,
            "ws_path": "/mobile/ws",
        })

    async def _ws_placeholder(request: web.Request) -> web.WebSocketResponse:
        auth = request.query.get("token", "")
        if auth != token:
            raise web.HTTPUnauthorized(text="bad token")
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        await ws.send_json({"type": "connected", "message": "sidecar mode"})
        async for msg in ws:
            pass
        return ws

    app.router.add_get("/mobile/discover", _discover)
    app.router.add_get("/mobile/ws", _ws_placeholder)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    logger.info("Mobile sidecar started on %s:%s (token=%s…)", host, port, token[:8])

    broadcast_payload = json.dumps({
        "service": "rxsci-mobile",
        "name": "RxSci Mobile Channel",
        "version": "1",
        "port": port,
        "ws_path": "/mobile/ws",
        "token": token,
    }).encode("utf-8")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setblocking(False)

    try:
        while True:
            try:
                sock.sendto(broadcast_payload, ("255.255.255.255", broadcast_port))
            except OSError:
                pass
            await asyncio.sleep(2.0)
    except asyncio.CancelledError:
        pass
    finally:
        sock.close()
        await runner.cleanup()
