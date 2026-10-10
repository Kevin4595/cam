import json
import os
import re
import time
import asyncio
import secrets
from typing import Literal

from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel


ROOM_PATTERN = re.compile(r"^[0-9a-f]{32}$")
SIGNAL_TYPES = {"description", "ice", "bye"}
ROOMS = {}
ROOMS_LOCK = asyncio.Lock()
ROOM_TTL_SECONDS = 3600
MAX_SIGNAL_BYTES = 65536
MAX_QUEUED_SIGNALS = 200
MAX_ACTIVE_ROOMS = 1000


def page_for(role):
    return f"""<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>Sesi kamera dengan izin</title>
  <style>
    :root {{
      color-scheme: light dark;
      font-family: system-ui, sans-serif;
      font-size: 16px;
      -webkit-text-size-adjust: 100%;
    }}
    * {{ box-sizing: border-box; }}
    [hidden] {{ display: none !important; }}
    body {{
      max-width: 800px;
      min-height: 100vh;
      margin: 0 auto;
      padding: max(1.25rem, env(safe-area-inset-top)) max(1rem, env(safe-area-inset-right))
        max(1.5rem, env(safe-area-inset-bottom)) max(1rem, env(safe-area-inset-left));
    }}
    main {{ display: grid; align-content: start; gap: 1rem; }}
    h1 {{ margin: .25rem 0; font-size: clamp(1.6rem, 7vw, 2.2rem); line-height: 1.15; }}
    p {{ line-height: 1.55; }}
    section {{ display: grid; gap: 1rem; }}
    video {{
      display: block;
      width: 100%;
      max-height: min(65vh, 720px);
      aspect-ratio: 4 / 3;
      object-fit: contain;
      background: #181818;
      border-radius: 16px;
    }}
    button {{
      width: 100%;
      min-height: 48px;
      padding: .8rem 1rem;
      border: 0;
      border-radius: 12px;
      font: inherit;
      font-weight: 650;
      cursor: pointer;
      touch-action: manipulation;
    }}
    button:disabled {{ cursor: not-allowed; opacity: .65; }}
    #invite {{ overflow-wrap: anywhere; }}
    #invite a {{ display: inline-block; padding: .4rem 0; }}
    #invite button {{ margin-top: .6rem; }}
    #status {{
      min-height: 3rem;
      margin: 0;
      padding: .8rem 1rem;
      border-radius: 12px;
      background: color-mix(in srgb, CanvasText 8%, Canvas);
      line-height: 1.45;
    }}
    .notice {{
      margin: 0;
      padding: .9rem 1rem;
      border-inline-start: 4px solid #d99b00;
      border-radius: 8px;
      background: color-mix(in srgb, #d99b00 10%, Canvas);
    }}
    @media (max-width: 600px) {{
      body {{ min-height: 100dvh; }}
      main {{ gap: .9rem; }}
      video {{ aspect-ratio: 3 / 4; max-height: 58dvh; }}
      #viewer-panel video {{ aspect-ratio: 4 / 3; max-height: 42dvh; }}
    }}
    @media (min-width: 601px) {{
      body {{ padding-top: 3rem; }}
    }}
  </style>
</head>
<body>
  <main>
    <h1>Sesi kamera dengan izin</h1>
    <section id="viewer-panel" hidden>
      <p>Buat tautan undangan pribadi, lalu kirim hanya kepada orang yang akan berbagi kamera.</p>
      <button id="create-session" type="button">Buat sesi dan tautan undangan</button>
      <p id="invite"></p>
      <video id="remote-video" autoplay playsinline></video>
    </section>
    <section id="camera-panel" hidden>
      <p class="notice">
        Jika Anda melanjutkan, kamera akan dinyalakan setelah izin browser diberikan
        dan video live akan terlihat oleh orang yang mengirim tautan undangan ini.
        Video dikirim langsung ke browser orang tersebut dan tidak direkam atau
        disimpan oleh aplikasi ini.
      </p>
      <button id="start-camera" type="button">Setujui, nyalakan kamera, dan bagikan live</button>
      <video id="local-video" autoplay playsinline muted></video>
    </section>
    <button id="stop-session" type="button" hidden>Hentikan sesi</button>
    <p id="status" role="status" aria-live="polite">Memuat...</p>
  </main>
  <script>
    const role = {json.dumps(role)};
    const status = document.querySelector("#status");
    const stopButton = document.querySelector("#stop-session");
    const viewerPanel = document.querySelector("#viewer-panel");
    const cameraPanel = document.querySelector("#camera-panel");
    const remoteVideo = document.querySelector("#remote-video");
    const localVideo = document.querySelector("#local-video");
    let room = null;
    let peer = null;
    let localStream = null;
    let cursor = 0;
    let polling = false;

    function setStatus(message) {{
      status.textContent = message;
    }}

    async function sendSignal(type, data = null) {{
      const response = await fetch("/api/signal", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{ room, role, type, data }})
      }});
      if (!response.ok) {{
        throw new Error(`Gagal mengirim sinyal (${{response.status}}).`);
      }}
    }}

    async function handleSignal(signal) {{
      if (signal.type === "bye") {{
        stopSession(false);
        setStatus("Orang di sisi lain telah mengakhiri sesi.");
        return;
      }}
      if (signal.type === "ice") {{
        if (peer && signal.data) {{
          await peer.addIceCandidate(signal.data);
        }}
        return;
      }}
      if (signal.type !== "description" || !peer || !signal.data) {{
        return;
      }}

      await peer.setRemoteDescription(signal.data);
      if (role === "camera" && signal.data.type === "offer") {{
        const answer = await peer.createAnswer();
        await peer.setLocalDescription(answer);
        await sendSignal("description", peer.localDescription);
        setStatus("Menghubungkan video live ke desktop...");
      }}
    }}

    async function pollSignals() {{
      while (polling) {{
        const query = new URLSearchParams({{ role, cursor: String(cursor) }});
        const response = await fetch(`/api/poll?${{query}}`, {{
          headers: {{ "Authorization": `Bearer ${{room}}` }}
        }});
        if (!response.ok) {{
          throw new Error(`Koneksi sinyal terputus (${{response.status}}).`);
        }}
        const result = await response.json();
        cursor = result.cursor;
        for (const signal of result.signals) {{
          await handleSignal(signal);
        }}
      }}
    }}

    function makePeer() {{
      peer = new RTCPeerConnection({{
        iceServers: [{{ urls: "stun:stun.l.google.com:19302" }}]
      }});
      peer.onicecandidate = (event) => {{
        if (event.candidate) {{
          sendSignal("ice", event.candidate).catch((error) => setStatus(error.message));
        }}
      }};
      peer.onconnectionstatechange = () => {{
        if (!peer) return;
        if (peer.connectionState === "connected") {{
          setStatus("Live tersambung ke desktop.");
        }} else if (peer.connectionState === "failed") {{
          setStatus("Koneksi gagal. Jaringan ini mungkin memerlukan konfigurasi TURN.");
        }} else if (peer.connectionState === "disconnected") {{
          setStatus("Koneksi terputus.");
        }}
      }};
      if (role === "camera") {{
        for (const track of localStream.getTracks()) {{
          peer.addTrack(track, localStream);
        }}
      }} else {{
        peer.ontrack = (event) => {{
          remoteVideo.srcObject = event.streams[0];
          remoteVideo.play().catch(() => {{
            setStatus("Klik video untuk mulai memutar live.");
          }});
        }};
      }}
    }}

    async function startViewerSession() {{
      const response = await fetch("/api/session", {{ method: "POST" }});
      if (!response.ok) {{
        throw new Error(`Gagal membuat sesi (${{response.status}}).`);
      }}
      ({{ room }} = await response.json());
      const invitation = `${{location.origin}}/camera#${{room}}`;
      document.querySelector("#invite").replaceChildren(
        document.createTextNode("Tautan pribadi: "),
        Object.assign(document.createElement("a"), {{
          href: invitation,
          textContent: invitation
        }})
      );
      const copyButton = document.createElement("button");
      copyButton.type = "button";
      copyButton.textContent = "Salin tautan";
      copyButton.addEventListener("click", async () => {{
        try {{
          await navigator.clipboard.writeText(invitation);
          setStatus("Tautan undangan disalin. Bagikan hanya kepada orang yang dimaksud.");
        }} catch (error) {{
          setStatus(`Tidak dapat menyalin tautan: ${{error.message}}`);
        }}
      }});
      document.querySelector("#invite").append(" ", copyButton);

      makePeer();
      polling = true;
      pollSignals().catch((error) => setStatus(error.message));
      stopButton.hidden = false;
      document.querySelector("#create-session").disabled = true;
      setStatus("Menunggu orang yang diundang menyetujui dan menyalakan kameranya...");

      const offer = await peer.createOffer();
      await peer.setLocalDescription(offer);
      await sendSignal("description", peer.localDescription);
    }}

    async function startCamera() {{
      const inviteRoom = location.hash.slice(1);
      if (!/^[0-9a-f]{{32}}$/.test(inviteRoom)) {{
        setStatus("Tautan undangan tidak valid. Minta tautan baru dari pengundang.");
        return;
      }}
      if (!navigator.mediaDevices?.getUserMedia) {{
        setStatus("Akses kamera memerlukan browser modern dan koneksi HTTPS.");
        return;
      }}
      room = inviteRoom;
      const startButton = document.querySelector("#start-camera");
      startButton.disabled = true;
      setStatus("Menunggu persetujuan kamera dari browser...");
      try {{
        localStream = await navigator.mediaDevices.getUserMedia({{
          audio: false,
          video: true
        }});
        localVideo.srcObject = localStream;
        makePeer();
        polling = true;
        pollSignals().catch((error) => setStatus(error.message));
        stopButton.hidden = false;
        setStatus("Kamera aktif. Menghubungkan live ke desktop pengundang...");
      }} catch (error) {{
        startButton.disabled = false;
        if (error.name === "NotAllowedError" || error.name === "PermissionDeniedError") {{
          setStatus("Izin kamera ditolak. Tidak ada video yang dibagikan.");
        }} else if (error.name === "NotFoundError" || error.name === "DevicesNotFoundError") {{
          setStatus("Kamera tidak ditemukan pada perangkat ini.");
        }} else {{
          setStatus(`Kamera tidak dapat dinyalakan: ${{error.message || error.name}}`);
        }}
      }}
    }}

    function stopSession(notifyPeer = true) {{
      polling = false;
      if (notifyPeer && room) {{
        sendSignal("bye").catch((error) => setStatus(error.message));
      }}
      if (peer) {{
        peer.close();
        peer = null;
      }}
      if (localStream) {{
        localStream.getTracks().forEach((track) => track.stop());
        localStream = null;
      }}
      if (localVideo) localVideo.srcObject = null;
      if (remoteVideo) remoteVideo.srcObject = null;
      stopButton.hidden = true;
      if (role === "camera") {{
        document.querySelector("#start-camera").disabled = false;
      }} else {{
        document.querySelector("#create-session").disabled = false;
        document.querySelector("#invite").replaceChildren();
        room = null;
      }}
      setStatus("Sesi dihentikan.");
    }}

    if (role === "viewer") {{
      viewerPanel.hidden = false;
      setStatus("Buat sesi untuk mendapatkan tautan undangan pribadi.");
      document.querySelector("#create-session").addEventListener("click", () => {{
        startViewerSession().catch((error) => setStatus(error.message));
      }});
    }} else {{
      cameraPanel.hidden = false;
      setStatus("Periksa pemberitahuan sebelum menyetujui berbagi kamera.");
      document.querySelector("#start-camera").addEventListener("click", () => {{
        startCamera();
      }});
    }}
    stopButton.addEventListener("click", () => stopSession());
    window.addEventListener("pagehide", () => {{
      polling = false;
      if (localStream) localStream.getTracks().forEach((track) => track.stop());
      if (peer) peer.close();
    }});
  </script>
</body>
</html>
"""


def clean_expired_rooms():
    cutoff = time.monotonic() - ROOM_TTL_SECONDS
    expired = [
        room_id
        for room_id, room_data in ROOMS.items()
        if room_data["last_seen"] < cutoff
    ]
    for room_id in expired:
        del ROOMS[room_id]


class SignalRequest(BaseModel):
    room: str
    role: Literal["viewer", "camera"]
    type: Literal["description", "ice", "bye"]
    data: dict | None = None


app = FastAPI(docs_url=None, redoc_url=None)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
        "connect-src 'self'; media-src 'self' blob:"
    )
    return response


@app.get("/", response_class=HTMLResponse)
async def viewer_page():
    return page_for("viewer")


@app.get("/camera", response_class=HTMLResponse)
async def camera_page():
    return page_for("camera")


@app.get("/healthz")
async def health_check():
    return {"status": "ok"}


@app.post("/api/session")
async def create_session():
    async with ROOMS_LOCK:
        clean_expired_rooms()
        if len(ROOMS) >= MAX_ACTIVE_ROOMS:
            raise HTTPException(status_code=503, detail="Server is at session capacity")
        room_id = secrets.token_hex(16)
        ROOMS[room_id] = {
            "signals": [],
            "event": asyncio.Event(),
            "last_seen": time.monotonic(),
        }
    return {"room": room_id}


@app.get("/api/poll")
async def poll_signals(
    role: Literal["viewer", "camera"],
    cursor: int = Query(default=0, ge=0),
    authorization: str | None = Header(default=None),
):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing session token")
    room = authorization.removeprefix("Bearer ").strip()
    if not ROOM_PATTERN.fullmatch(room):
        raise HTTPException(status_code=400, detail="Invalid session")

    deadline = time.monotonic() + 20
    while True:
        async with ROOMS_LOCK:
            clean_expired_rooms()
            room_data = ROOMS.get(room)
            if room_data is None:
                raise HTTPException(status_code=404, detail="Session not found or expired")
            room_data["last_seen"] = time.monotonic()
            available = [
                signal for signal in room_data["signals"] if signal["cursor"] > cursor
            ]
            if available:
                next_cursor = available[-1]["cursor"]
                signals = [
                    {"cursor": signal["cursor"], "type": signal["type"], "data": signal["data"]}
                    for signal in available
                    if signal["to"] == role
                ]
                return {"cursor": next_cursor, "signals": signals}
            room_data["event"].clear()
            event = room_data["event"]

        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return {"cursor": cursor, "signals": []}
        try:
            await asyncio.wait_for(event.wait(), timeout=remaining)
        except TimeoutError:
            return {"cursor": cursor, "signals": []}


@app.post("/api/signal")
async def post_signal(payload: SignalRequest, request: Request):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > MAX_SIGNAL_BYTES:
                raise HTTPException(status_code=413, detail="Signal is too large")
        except ValueError as error:
            raise HTTPException(status_code=400, detail="Invalid content length") from error
    if not ROOM_PATTERN.fullmatch(payload.room):
        raise HTTPException(status_code=400, detail="Invalid session")
    if payload.type == "description" and (
        payload.data is None
        or payload.data.get("type") not in {"offer", "answer"}
        or not isinstance(payload.data.get("sdp"), str)
    ):
        raise HTTPException(status_code=400, detail="Invalid session description")
    if payload.type == "ice" and payload.data is None:
        raise HTTPException(status_code=400, detail="Invalid ICE candidate")

    async with ROOMS_LOCK:
        clean_expired_rooms()
        room_data = ROOMS.get(payload.room)
        if room_data is None:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        signals = room_data["signals"]
        if len(signals) >= MAX_QUEUED_SIGNALS:
            raise HTTPException(status_code=429, detail="Too many queued signals")
        cursor = signals[-1]["cursor"] + 1 if signals else 1
        signals.append(
            {
                "cursor": cursor,
                "to": "camera" if payload.role == "viewer" else "viewer",
                "type": payload.type,
                "data": payload.data,
            }
        )
        room_data["last_seen"] = time.monotonic()
        room_data["event"].set()
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn

    host = os.environ.get("CAMERA_DEMO_HOST", "127.0.0.1")
    port = int(os.environ.get("CAMERA_DEMO_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
