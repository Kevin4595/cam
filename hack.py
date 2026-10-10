import json


def page_for(role):
    return f"""<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com; style-src 'self' 'unsafe-inline'; connect-src 'self' https://0.peerjs.com wss://0.peerjs.com https://*.peerjs.com wss://*.peerjs.com; media-src 'self' blob:">
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
    #quiz-panel {{
      padding: 1rem;
      border: 1px solid color-mix(in srgb, CanvasText 20%, Canvas);
      border-radius: 12px;
    }}
    #quiz-panel h2 {{ margin: 0; }}
    #quiz-panel label {{ display: grid; gap: .4rem; }}
    #quiz-answer {{
      width: 100%;
      min-height: 48px;
      padding: .7rem;
      border: 1px solid currentColor;
      border-radius: 8px;
      font: inherit;
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
      <section id="quiz-panel" aria-labelledby="quiz-title" hidden>
        <h2 id="quiz-title">Tantangan matematika</h2>
        <p id="quiz-progress"></p>
        <p id="quiz-question"></p>
        <form id="quiz-form">
          <label for="quiz-answer">Jawaban
            <input id="quiz-answer" type="number" inputmode="numeric" required>
          </label>
          <button type="submit">Periksa jawaban</button>
        </form>
        <p id="quiz-feedback" role="status" aria-live="polite"></p>
        <button id="close-quiz" type="button">Tutup kuis</button>
      </section>
      <button id="open-quiz" type="button" hidden>Buka kuis matematika</button>
    </section>
    <button id="stop-session" type="button" hidden>Hentikan sesi</button>
    <p id="status" role="status" aria-live="polite">Memuat...</p>
  </main>
  <script src="https://unpkg.com/peerjs@1.5.4/dist/peerjs.min.js"></script>
  <script>
    const role = {json.dumps(role)};
    const status = document.querySelector("#status");
    const stopButton = document.querySelector("#stop-session");
    const viewerPanel = document.querySelector("#viewer-panel");
    const cameraPanel = document.querySelector("#camera-panel");
    const remoteVideo = document.querySelector("#remote-video");
    const localVideo = document.querySelector("#local-video");
    const quizPanel = document.querySelector("#quiz-panel");
    const quizForm = document.querySelector("#quiz-form");
    const quizAnswer = document.querySelector("#quiz-answer");
    const quizQuestions = [
      {{ text: "7 + 5 = ?", answer: 12 }},
      {{ text: "14 - 6 = ?", answer: 8 }},
      {{ text: "3 × 4 = ?", answer: 12 }},
      {{ text: "18 ÷ 3 = ?", answer: 6 }},
      {{ text: "9 + 8 = ?", answer: 17 }},
      {{ text: "20 - 7 = ?", answer: 13 }},
      {{ text: "5 × 6 = ?", answer: 30 }},
      {{ text: "24 ÷ 4 = ?", answer: 6 }},
      {{ text: "16 + 9 = ?", answer: 25 }},
      {{ text: "30 - 12 = ?", answer: 18 }}
    ];
    let quizIndex = 0;
    let room = null;
    let peer = null;
    let call = null;
    let localStream = null;

    function setStatus(message) {{
      status.textContent = message;
    }}

    function showQuizQuestion() {{
      document.querySelector("#quiz-progress").textContent =
        `Soal ${{quizIndex + 1}} dari ${{quizQuestions.length}}`;
      document.querySelector("#quiz-question").textContent =
        quizQuestions[quizIndex].text;
      quizAnswer.value = "";
      quizAnswer.focus();
    }}

    function resetQuiz() {{
      quizIndex = 0;
      quizPanel.hidden = true;
      document.querySelector("#open-quiz").hidden = true;
      quizForm.hidden = false;
      document.querySelector("#quiz-feedback").textContent = "";
    }}

    function makePeer() {{
      if (typeof Peer === "undefined") {{
        throw new Error("Layanan koneksi tidak termuat. Periksa koneksi internet lalu muat ulang halaman.");
      }}
      peer = new Peer(undefined, {{
        debug: 1,
        config: {{
          iceServers: [{{ urls: "stun:stun.l.google.com:19302" }}]
        }}
      }});
      peer.on("error", (error) => {{
        setStatus(`Koneksi gagal: ${{error.message}}`);
      }});
      return peer;
    }}

    function waitForPeerOpen(activePeer) {{
      return new Promise((resolve, reject) => {{
        activePeer.once("open", resolve);
        activePeer.once("error", reject);
      }});
    }}

    async function startViewerSession() {{
      const createButton = document.querySelector("#create-session");
      createButton.disabled = true;
      setStatus("Membuat tautan undangan...");
      const activePeer = makePeer();
      activePeer.on("call", (incomingCall) => {{
        call = incomingCall;
        call.answer();
        call.on("stream", (stream) => {{
          remoteVideo.srcObject = stream;
          remoteVideo.play().catch(() => {{
            setStatus("Klik video untuk mulai memutar live.");
          }});
          setStatus("Live kamera tersambung.");
        }});
        call.on("close", () => {{
          remoteVideo.srcObject = null;
          setStatus("Sesi kamera telah berakhir.");
        }});
        call.on("error", (error) => setStatus(`Panggilan gagal: ${{error.message}}`));
      }});
      activePeer.on("disconnected", () => {{
        setStatus("Koneksi layanan terputus. Mencoba menyambungkan kembali...");
        activePeer.reconnect();
      }});
      let peerId;
      try {{
        peerId = await waitForPeerOpen(activePeer);
      }} catch (error) {{
        activePeer.destroy();
        peer = null;
        createButton.disabled = false;
        throw error;
      }}
      room = peerId;
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
      stopButton.hidden = false;
      setStatus("Menunggu orang yang diundang menyetujui dan menyalakan kameranya...");
    }}

    async function startCamera() {{
      const inviteRoom = location.hash.slice(1);
      if (!/^[A-Za-z0-9_-]{{1,128}}$/.test(inviteRoom)) {{
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
        quizIndex = 0;
        showQuizQuestion();
        quizPanel.hidden = false;
        document.querySelector("#open-quiz").hidden = true;
        room = inviteRoom;
        const activePeer = makePeer();
        await waitForPeerOpen(activePeer);
        call = activePeer.call(room, localStream, {{
          metadata: {{ purpose: "consensual-camera-share" }}
        }});
        if (!call) {{
          throw new Error("Sesi undangan tidak dapat dihubungi. Minta tautan baru.");
        }}
        call.on("close", () => {{
          stopSession(false);
          setStatus("Sesi kamera telah berakhir.");
        }});
        call.on("error", (error) => setStatus(`Panggilan gagal: ${{error.message}}`));
        stopButton.hidden = false;
        setStatus("Kamera aktif. Menghubungkan live ke desktop pengundang...");
      }} catch (error) {{
        if (localStream) {{
          localStream.getTracks().forEach((track) => track.stop());
          localStream = null;
          localVideo.srcObject = null;
        }}
        if (peer) {{
          peer.destroy();
          peer = null;
        }}
        if (call) {{
          call.close();
          call = null;
        }}
        resetQuiz();
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
      if (call) {{
        call.close();
        call = null;
      }}
      if (peer) {{
        peer.destroy();
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
        resetQuiz();
      }} else {{
        document.querySelector("#create-session").disabled = false;
        document.querySelector("#invite").replaceChildren();
      }}
      room = null;
      setStatus("Sesi dihentikan.");
    }}

    if (role === "viewer") {{
      viewerPanel.hidden = false;
      setStatus("Buat sesi untuk mendapatkan tautan undangan pribadi.");
      document.querySelector("#create-session").addEventListener("click", () => {{
        startViewerSession().catch((error) => {{
          setStatus(`Tautan gagal dibuat: ${{error.message}}`);
        }});
      }});
    }} else {{
      cameraPanel.hidden = false;
      setStatus("Periksa pemberitahuan sebelum menyetujui berbagi kamera.");
      document.querySelector("#start-camera").addEventListener("click", () => {{
        startCamera();
      }});
    }}
    stopButton.addEventListener("click", () => stopSession());
    quizForm.addEventListener("submit", (event) => {{
      event.preventDefault();
      if (quizIndex >= quizQuestions.length) return;
      const answer = Number(quizAnswer.value);
      const feedback = document.querySelector("#quiz-feedback");
      if (!Number.isInteger(answer) || quizAnswer.value.trim() === "") {{
        feedback.textContent = "Masukkan jawaban berupa bilangan bulat.";
        return;
      }}
      if (answer !== quizQuestions[quizIndex].answer) {{
        feedback.textContent = "Belum tepat. Coba lagi, atau tutup kuis.";
        quizAnswer.select();
        return;
      }}
      quizIndex += 1;
      if (quizIndex === quizQuestions.length) {{
        quizPanel.hidden = true;
        document.querySelector("#open-quiz").hidden = true;
        setStatus("Kuis selesai. Semua 10 jawaban benar.");
        return;
      }}
      feedback.textContent = "Benar!";
      showQuizQuestion();
    }});
    document.querySelector("#close-quiz").addEventListener("click", () => {{
      quizPanel.hidden = true;
      document.querySelector("#open-quiz").hidden = false;
    }});
    document.querySelector("#open-quiz").addEventListener("click", () => {{
      quizPanel.hidden = false;
      document.querySelector("#open-quiz").hidden = true;
      if (quizIndex < quizQuestions.length) quizAnswer.focus();
    }});
    window.addEventListener("pagehide", () => {{
      if (localStream) localStream.getTracks().forEach((track) => track.stop());
      if (call) call.close();
      if (peer) peer.destroy();
    }});
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

    import os
    from functools import partial

    host = os.environ.get("CAMERA_DEMO_HOST", "127.0.0.1")
    port = int(os.environ.get("CAMERA_DEMO_PORT", "8000"))
    web_root = os.path.join(os.path.dirname(__file__), "site")
    os.makedirs(web_root, exist_ok=True)
    for page_role, filename in (("viewer", "index.html"), ("camera", "camera.html")):
        with open(os.path.join(web_root, filename), "w", encoding="utf-8") as page_file:
            page_file.write(page_for(page_role))
    handler = partial(SimpleHTTPRequestHandler, directory=web_root)
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Camera demo listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()
