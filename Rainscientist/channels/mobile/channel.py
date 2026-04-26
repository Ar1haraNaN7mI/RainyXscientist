from __future__ import annotations

import json
import logging
import mimetypes
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from aiohttp import WSMsgType, web

from ...paths import MEDIA_DIR
from ..base import Channel, ChannelError, RawIncoming
from ..bus.events import InboundMessage, OutboundMessage
from ..capabilities import MOBILE as MOBILE_CAPS
from ..config import BaseChannelConfig

logger = logging.getLogger(__name__)


@dataclass
class MobileConfig(BaseChannelConfig):
    host: str = "0.0.0.0"
    port: int = 8765
    token: str = ""
    public_base_url: str = ""
    text_chunk_limit: int = 32_000


@dataclass
class _ClientState:
    client_id: str
    device_name: str
    connected_at: str
    subscribe_all: bool = True


class MobileChannel(Channel):
    name = "mobile"
    capabilities = MOBILE_CAPS
    _ready_attrs = ("_runner",)

    def __init__(self, config: MobileConfig):
        super().__init__(config)
        self._runner: web.AppRunner | None = None
        self._site: web.TCPSite | None = None
        self._clients: dict[web.WebSocketResponse, _ClientState] = {}
        self._uploads: dict[str, dict[str, Any]] = {}
        self._files: dict[str, dict[str, Any]] = {}
        self._sessions: dict[str, dict[str, Any]] = {}
        self._session_events: dict[str, deque[dict[str, Any]]] = defaultdict(
            lambda: deque(maxlen=200)
        )

    async def start(self) -> None:
        if not self.config.token:
            raise ChannelError("Mobile channel token is required")

        app = web.Application(client_max_size=64 * 1024**2)
        app.router.add_get("/mobile/discover", self._handle_discover)
        app.router.add_get("/mobile/ws", self._handle_ws)
        app.router.add_post("/mobile/upload", self._handle_upload)
        app.router.add_get("/mobile/files/{file_id}", self._handle_file_download)

        self._runner = web.AppRunner(app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, self.config.host, self.config.port)
        await self._site.start()
        logger.info(
            "Mobile channel started on %s:%s",
            self.config.host,
            self.config.port,
        )

    async def _cleanup(self) -> None:
        clients = list(self._clients.keys())
        for ws in clients:
            try:
                await ws.close(code=1001, message=b"server shutdown")
            except Exception:
                pass
        self._clients.clear()

        if self._site is not None:
            await self._site.stop()
            self._site = None
        if self._runner is not None:
            await self._runner.cleanup()
            self._runner = None

    async def _send_chunk(
        self,
        chat_id: str,
        formatted_text: str,
        raw_text: str,
        reply_to: str | None,
        metadata: dict,
    ) -> None:
        session_id = self._session_id(self.name, chat_id)
        payload = self._build_message_event(
            source_channel=self.name,
            chat_id=chat_id,
            role="assistant",
            content=raw_text or formatted_text,
            metadata=metadata,
            reply_to=reply_to,
            session_id=session_id,
        )
        await self._publish_event(payload)

    async def _send_media_impl(
        self,
        recipient: str,
        file_path: str,
        caption: str = "",
        metadata: dict | None = None,
    ) -> bool:
        session_id = self._session_id(self.name, recipient)
        attachment = self._register_file(file_path)
        payload = self._build_message_event(
            source_channel=self.name,
            chat_id=recipient,
            role="assistant",
            content=caption,
            metadata=metadata or {},
            session_id=session_id,
            attachments=[attachment],
        )
        await self._publish_event(payload)
        return True

    async def mirror_inbound_event(self, msg: InboundMessage) -> None:
        payload = self._build_message_event(
            source_channel=msg.channel,
            chat_id=msg.chat_id,
            role="user",
            content=msg.content,
            metadata=msg.metadata,
            session_id=msg.session_key,
            attachments=self._attachments_from_paths(msg.media, msg.metadata),
            server_message_id=msg.message_id or "",
        )
        await self._publish_event(payload)

    async def mirror_outbound_event(self, msg: OutboundMessage) -> None:
        session_id = self._session_id(msg.channel, msg.chat_id)
        payload = self._build_message_event(
            source_channel=msg.channel,
            chat_id=msg.chat_id,
            role="assistant",
            content=msg.content,
            metadata=msg.metadata,
            reply_to=msg.reply_to,
            session_id=session_id,
            attachments=self._attachments_from_paths(msg.media, msg.metadata),
        )
        await self._publish_event(payload)

    async def mirror_status_event(
        self,
        *,
        source_channel: str,
        chat_id: str,
        status_type: str,
        content: str,
        metadata: dict | None = None,
    ) -> None:
        session_id = self._session_id(source_channel, chat_id)
        session = self._ensure_session(
            session_id=session_id,
            source_channel=source_channel,
            chat_id=chat_id,
            writable=source_channel == self.name,
        )
        payload = {
            "type": status_type,
            "session": session,
            "event_id": uuid.uuid4().hex,
            "timestamp": self._now(),
            "content": content,
        }
        self._remember_event(session_id, payload)
        await self._broadcast(payload)

    async def mirror_media_event(
        self,
        *,
        source_channel: str,
        chat_id: str,
        file_path: str,
        metadata: dict | None = None,
    ) -> None:
        session_id = self._session_id(source_channel, chat_id)
        payload = self._build_message_event(
            source_channel=source_channel,
            chat_id=chat_id,
            role="assistant",
            content="",
            metadata=metadata or {},
            session_id=session_id,
            attachments=[self._register_file(file_path)],
        )
        await self._publish_event(payload)

    async def push_sync_snapshot(self) -> None:
        payload = {
            "type": "history_sync",
            "sessions": sorted(
                self._sessions.values(),
                key=lambda item: item.get("updated_at", ""),
                reverse=True,
            ),
            "events": [
                event
                for session_id in sorted(self._session_events.keys())
                for event in list(self._session_events[session_id])
            ],
            "timestamp": self._now(),
        }
        await self._broadcast(payload)

    async def _handle_ws(self, request: web.Request) -> web.WebSocketResponse:
        ws = web.WebSocketResponse(heartbeat=30)
        await ws.prepare(request)
        authed = False

        try:
            async for msg in ws:
                if msg.type != WSMsgType.TEXT:
                    continue
                payload = self._decode_json(msg.data)
                if payload is None:
                    await ws.send_json({"type": "error", "message": "invalid json"})
                    continue

                if not authed:
                    if payload.get("type") != "auth":
                        await ws.send_json({"type": "error", "message": "auth required"})
                        continue
                    state = self._authenticate_ws(payload)
                    if state is None:
                        await ws.send_json({"type": "error", "message": "auth failed"})
                        continue
                    self._clients[ws] = state
                    authed = True
                    await ws.send_json(
                        {
                            "type": "auth_ok",
                            "client_id": state.client_id,
                            "device_name": state.device_name,
                            "timestamp": self._now(),
                        }
                    )
                    await ws.send_json(self._build_history_sync_payload())
                    continue

                msg_type = payload.get("type")
                if msg_type == "ping":
                    await ws.send_json({"type": "pong", "timestamp": self._now()})
                elif msg_type == "send_message":
                    await self._handle_send_message(ws, payload)
                elif msg_type == "sync_request":
                    await ws.send_json(self._build_history_sync_payload())
                else:
                    await ws.send_json({"type": "error", "message": "unknown message type"})
        finally:
            self._clients.pop(ws, None)

        return ws

    async def _handle_discover(self, request: web.Request) -> web.StreamResponse:
        base_url = self.config.public_base_url.strip().rstrip("/")
        if not base_url:
            base_url = f"{request.scheme}://{request.host}"
        return web.json_response(
            {
                "service": "rxsci-mobile",
                "name": "RxSci Mobile Channel",
                "version": "1",
                "base_url": base_url,
                "host": self.config.host,
                "port": self.config.port,
                "requires_token": True,
                "ws_path": "/mobile/ws",
            }
        )

    async def _handle_upload(self, request: web.Request) -> web.StreamResponse:
        if not self._is_request_authorized(request):
            return web.json_response({"error": "unauthorized"}, status=401)

        reader = await request.multipart()
        client_id = request.headers.get("X-Mobile-Client", "").strip()
        file_field = None
        while True:
            part = await reader.next()
            if part is None:
                break
            if part.name == "file":
                file_field = part
                break

        if file_field is None or not file_field.filename:
            return web.json_response({"error": "file is required"}, status=400)

        upload_id = uuid.uuid4().hex
        safe_name = Path(file_field.filename).name
        target_dir = MEDIA_DIR / "mobile_uploads"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{upload_id}_{safe_name}"

        size = 0
        with target_path.open("wb") as fh:
            while True:
                chunk = await file_field.read_chunk()
                if not chunk:
                    break
                size += len(chunk)
                fh.write(chunk)

        kind = self._guess_file_kind(safe_name)
        self._uploads[upload_id] = {
            "path": str(target_path),
            "name": safe_name,
            "size": size,
            "kind": kind,
            "client_id": client_id,
            "uploaded_at": self._now(),
        }
        return web.json_response(
            {
                "upload_id": upload_id,
                "name": safe_name,
                "size": size,
                "kind": kind,
            }
        )

    async def _handle_file_download(self, request: web.Request) -> web.StreamResponse:
        if not self._is_request_authorized(request):
            return web.json_response({"error": "unauthorized"}, status=401)

        file_id = request.match_info["file_id"]
        record = self._files.get(file_id)
        if not record:
            return web.json_response({"error": "not found"}, status=404)

        file_path = Path(record["path"]).resolve()
        if not file_path.is_file():
            return web.json_response({"error": "not found"}, status=404)
        return web.FileResponse(file_path)

    async def _handle_send_message(
        self,
        ws: web.WebSocketResponse,
        payload: dict[str, Any],
    ) -> None:
        client = self._clients.get(ws)
        if client is None:
            await ws.send_json({"type": "error", "message": "auth required"})
            return

        raw_session = str(payload.get("session_id", "")).strip()
        chat_id = self._chat_id_from_session(raw_session) or uuid.uuid4().hex[:8]
        text = str(payload.get("content", "") or "").strip()
        attachment_refs = payload.get("attachments", []) or []
        media_files: list[str] = []
        upload_meta: list[dict[str, Any]] = []

        for item in attachment_refs:
            upload_id = str((item or {}).get("upload_id", "")).strip()
            record = self._uploads.get(upload_id)
            if not record:
                continue
            media_files.append(record["path"])
            upload_meta.append(
                {
                    "upload_id": upload_id,
                    "name": record["name"],
                    "size": record["size"],
                    "kind": record["kind"],
                }
            )

        if not text and not media_files:
            await ws.send_json({"type": "error", "message": "empty message"})
            return

        metadata = {
            "client_id": client.client_id,
            "device_name": client.device_name,
            "client_message_id": str(payload.get("client_message_id", "")).strip(),
            "uploads": upload_meta,
            "chat_id": chat_id,
        }
        raw = RawIncoming(
            sender_id=client.client_id,
            chat_id=chat_id,
            text=text,
            media_files=media_files,
            message_id=str(payload.get("client_message_id", "")).strip() or uuid.uuid4().hex,
            metadata=metadata,
        )
        await self._enqueue_raw(raw)
        await ws.send_json(
            {
                "type": "accepted",
                "session_id": self._session_id(self.name, chat_id),
                "client_message_id": metadata["client_message_id"],
                "timestamp": self._now(),
            }
        )

    def _authenticate_ws(self, payload: dict[str, Any]) -> _ClientState | None:
        token = str(payload.get("token", "")).strip()
        if token != self.config.token:
            return None

        client_id = str(payload.get("client_id", "")).strip() or uuid.uuid4().hex[:12]
        if self.config.allowed_senders and client_id not in self.config.allowed_senders:
            return None

        return _ClientState(
            client_id=client_id,
            device_name=str(payload.get("device_name", "")).strip() or "Android",
            connected_at=self._now(),
            subscribe_all=bool(payload.get("subscribe_all", True)),
        )

    async def _publish_event(self, payload: dict[str, Any]) -> None:
        session = payload.get("session")
        if isinstance(session, dict):
            session_id = str(session.get("session_id", "")).strip()
            if session_id:
                self._remember_event(session_id, payload)
        await self._broadcast(payload)

    async def _broadcast(self, payload: dict[str, Any]) -> None:
        stale: list[web.WebSocketResponse] = []
        for ws in list(self._clients.keys()):
            try:
                await ws.send_json(payload)
            except Exception:
                stale.append(ws)
        for ws in stale:
            self._clients.pop(ws, None)

    def _build_history_sync_payload(self) -> dict[str, Any]:
        sessions = sorted(
            self._sessions.values(),
            key=lambda item: item.get("updated_at", ""),
            reverse=True,
        )
        events: list[dict[str, Any]] = []
        for session in sessions:
            session_id = session["session_id"]
            events.extend(list(self._session_events.get(session_id, ())))
        return {
            "type": "history_sync",
            "sessions": sessions,
            "events": events,
            "timestamp": self._now(),
        }

    def _build_message_event(
        self,
        *,
        source_channel: str,
        chat_id: str,
        role: str,
        content: str,
        metadata: dict[str, Any],
        session_id: str,
        reply_to: str | None = None,
        attachments: list[dict[str, Any]] | None = None,
        server_message_id: str = "",
    ) -> dict[str, Any]:
        session = self._ensure_session(
            session_id=session_id,
            source_channel=source_channel,
            chat_id=chat_id,
            writable=source_channel == self.name,
            title=self._derive_title(session_id, content),
        )
        message = {
            "message_id": server_message_id or uuid.uuid4().hex,
            "role": role,
            "content": content,
            "reply_to": reply_to,
            "timestamp": self._now(),
            "source_channel": source_channel,
            "chat_id": chat_id,
            "client_message_id": str(metadata.get("client_message_id", "")).strip(),
            "attachments": attachments or [],
        }
        session["last_message"] = content or (
            attachments[0]["name"] if attachments else session.get("last_message", "")
        )
        session["updated_at"] = message["timestamp"]
        return {
            "type": "message",
            "session": session,
            "message": message,
        }

    def _ensure_session(
        self,
        *,
        session_id: str,
        source_channel: str,
        chat_id: str,
        writable: bool,
        title: str | None = None,
    ) -> dict[str, Any]:
        existing = self._sessions.get(session_id, {})
        session = {
            "session_id": session_id,
            "source_channel": source_channel,
            "chat_id": chat_id,
            "title": title or existing.get("title") or session_id,
            "updated_at": existing.get("updated_at") or self._now(),
            "last_message": existing.get("last_message", ""),
            "writable": writable,
        }
        self._sessions[session_id] = session
        return session

    def _remember_event(self, session_id: str, payload: dict[str, Any]) -> None:
        self._session_events[session_id].append(payload)

    def _attachments_from_paths(
        self,
        paths: list[str],
        metadata: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        uploads = metadata.get("uploads", []) if isinstance(metadata, dict) else []
        if uploads:
            result = []
            for item, path in zip(uploads, paths, strict=False):
                result.append(self._register_file(path, item))
            if result:
                return result
        return [self._register_file(path) for path in paths]

    def _register_file(
        self,
        file_path: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        path = Path(file_path).resolve()
        file_id = uuid.uuid4().hex
        name = metadata.get("name") if metadata else path.name
        size = metadata.get("size") if metadata else (path.stat().st_size if path.exists() else 0)
        kind = metadata.get("kind") if metadata else self._guess_file_kind(name)
        self._files[file_id] = {
            "path": str(path),
            "name": name,
            "size": size,
            "kind": kind,
        }
        return {
            "file_id": file_id,
            "name": name,
            "size": size,
            "kind": kind,
            "download_path": f"/mobile/files/{file_id}",
        }

    def _is_request_authorized(self, request: web.Request) -> bool:
        header = request.headers.get("Authorization", "")
        token = header.removeprefix("Bearer ").strip() if header else ""
        if not token:
            token = request.headers.get("X-Mobile-Token", "").strip()
        if not token:
            token = request.query.get("token", "").strip()
        return token == self.config.token

    def _session_id(self, source_channel: str, chat_id: str) -> str:
        return f"{source_channel}:{chat_id}"

    def _chat_id_from_session(self, session_id: str) -> str:
        if session_id.startswith(f"{self.name}:"):
            return session_id.split(":", 1)[1]
        return session_id

    def _derive_title(self, session_id: str, content: str) -> str:
        if content.strip():
            return content.strip().splitlines()[0][:48]
        return self._sessions.get(session_id, {}).get("title") or session_id

    def _guess_file_kind(self, name: str) -> str:
        mime, _ = mimetypes.guess_type(name)
        if mime and mime.startswith("image/"):
            return "image"
        return "file"

    def _decode_json(self, raw: str) -> dict[str, Any] | None:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return None
        return data if isinstance(data, dict) else None

    def _now(self) -> str:
        return datetime.now().isoformat(timespec="seconds")
