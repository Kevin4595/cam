import json


def page_for(role):
    return f"""<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://www.gstatic.com; style-src 'self' 'unsafe-inline'; connect-src 'self' https://identitytoolkit.googleapis.com https://securetoken.googleapis.com https://www.googleapis.com https://firebaseinstallations.googleapis.com https://*.firebaseio.com wss://*.firebaseio.com https://*.firebasedatabase.app wss://*.firebasedatabase.app; media-src 'self' blob:">
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
  <script src="./firebase-config.js"></script>
  <script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js"></script>
  <script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-auth-compat.js"></script>
  <script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-database-compat.js"></script>
  <script>
    const role = {json.dumps(role)};
    const status = document.querySelector("#status");
    const stopButton = document.querySelector("#stop-session");
    const viewerPanel = document.querySelector("#viewer-panel");
    const cameraPanel = document.querySelector("#camera-panel");
    const remoteVideo = document.querySelector("#remote-video");
    const localVideo = document.querySelector("#local-video");
    let room = null;
    let roomRef = null;
    let signalsRef = null;
    let peer = null;
    let localStream = null;
    let signalListener = null;
    let removedListener = null;
    let auth = null;
    let database = null;

    function setStatus(message) {{
      status.textContent = message;
    }}

    function firebaseConfigured() {{
      const config = window.FIREBASE_CONFIG;
      return config && config.apiKey && config.authDomain &&
        config.databaseURL && config.projectId && config.appId;
    }}

    async function ensureSignedIn() {{
      if (!firebaseConfigured() || !auth || !database) {{
        throw new Error("Firebase belum dikonfigurasi. Ikuti README untuk membuat proyek Firebase gratis.");
      }}
      if (!auth.currentUser) {{
        await auth.signInAnonymously();
      }}
      return auth.currentUser;
    }}

    async function sendSignal(type, data = null) {{
      if (!signalsRef) {{
        throw new Error("Sesi belum siap.");
      }}
      const value = data && typeof data.toJSON === "function" ? data.toJSON() : data;
      await signalsRef.push({{ from: role, type, data: value || {{ notice: "session-ended" }} }});
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

    function watchSignals() {{
      signalsRef = roomRef.child("signals");
      signalListener = (snapshot) => {{
        const signal = snapshot.val();
        if (signal && signal.from !== role) {{
          handleSignal(signal).catch((error) => setStatus(`Sinyal gagal diproses: ${{error.message}}`));
        }}
      }};
      removedListener = () => {{
        if (role === "camera") {{
          stopSession(false);
          setStatus("Sesi telah berakhir.");
        }}
      }};
      signalsRef.on("child_added", signalListener, (error) => {{
        setStatus(`Koneksi signaling gagal: ${{error.message}}`);
      }});
      roomRef.on("value", (snapshot) => {{
        if (!snapshot.exists()) {{
          removedListener();
        }}
      }}, (error) => setStatus(`Akses sesi ditolak: ${{error.message}}`));
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
      const user = await ensureSignedIn();
      room = Array.from(
        crypto.getRandomValues(new Uint8Array(16)),
        (byte) => byte.toString(16).padStart(2, "0")
      ).join("");
      roomRef = database.ref(`rooms/${{room}}`);
      await roomRef.set({{
        owner: user.uid,
        expiresAt: Date.now() + 60 * 60 * 1000,
        signals: {{}}
      }});
      await roomRef.onDisconnect().remove();
      const inviteUrl = new URL("./camera.html", location.href);
      inviteUrl.hash = room;
      const invitation = inviteUrl.href;
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
      watchSignals();
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
      setStatus("Menunggu izin kamera dari browser...");
      try {{
        localStream = await navigator.mediaDevices.getUserMedia({{
          audio: false,
          video: true
        }});
        localVideo.srcObject = localStream;
        await ensureSignedIn();
        room = inviteRoom;
        roomRef = database.ref(`rooms/${{room}}`);
        const session = await roomRef.once("value");
        if (!session.exists() || session.child("expiresAt").val() <= Date.now()) {{
          throw new Error("Undangan sudah kedaluwarsa atau sesi tidak tersedia.");
        }}
        watchSignals();
        makePeer();
        stopButton.hidden = false;
        setStatus("Kamera aktif. Menghubungkan live ke desktop pengundang...");
      }} catch (error) {{
        if (localStream) {{
          localStream.getTracks().forEach((track) => track.stop());
          localStream = null;
          localVideo.srcObject = null;
        }}
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
      const endedRoomRef = roomRef;
      if (notifyPeer && room) {{
        sendSignal("bye").catch((error) => setStatus(`Gagal memberi tahu sesi lain: ${{error.message}}`));
      }}
      if (signalsRef && signalListener) {{
        signalsRef.off("child_added", signalListener);
      }}
      if (roomRef && removedListener) {{
        roomRef.off("value");
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
      signalsRef = null;
      signalListener = null;
      removedListener = null;
      if (role === "camera") {{
        document.querySelector("#start-camera").disabled = false;
      }} else {{
        document.querySelector("#create-session").disabled = false;
        document.querySelector("#invite").replaceChildren();
        if (endedRoomRef) {{
          if (notifyPeer) {{
            setTimeout(() => {{
              endedRoomRef.remove().catch((error) => setStatus(`Sesi gagal dibersihkan: ${{error.message}}`));
            }}, 1000);
          }} else {{
            endedRoomRef.remove().catch((error) => setStatus(`Sesi gagal dibersihkan: ${{error.message}}`));
          }}
        }}
      }}
      room = null;
      roomRef = null;
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
      if (localStream) localStream.getTracks().forEach((track) => track.stop());
      if (peer) peer.close();
    }});
    if (firebaseConfigured()) {{
      try {{
        firebase.initializeApp(window.FIREBASE_CONFIG);
        auth = firebase.auth();
        database = firebase.database();
      }} catch (error) {{
        setStatus(`Inisialisasi Firebase gagal: ${{error.message}}`);
      }}
    }} else {{
      setStatus("Firebase belum dikonfigurasi. Lihat README untuk menyiapkan website gratis.");
    }}
  </script>
</body>
</html>
"""
