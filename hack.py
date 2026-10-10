import json


def page_for(role):
    return f"""<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com; style-src 'self' 'unsafe-inline'; connect-src 'self' https://0.peerjs.com wss://0.peerjs.com https://*.peerjs.com wss://*.peerjs.com; media-src 'self' blob:">
  <title>Kuis Basic Matematika</title>
  <style>
    :root {{
      color-scheme: dark;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 16px;
      -webkit-text-size-adjust: 100%;
      --page: #080d18;
      --panel: rgba(17, 26, 43, .9);
      --panel-soft: #121d30;
      --text: #f1f5fb;
      --muted: #aab7ca;
      --accent: #72f0ce;
      --accent-strong: #37cda7;
      --line: rgba(180, 202, 225, .16);
      --danger: #ff7185;
    }}
    * {{ box-sizing: border-box; }}
    [hidden] {{ display: none !important; }}
    body {{
      display: grid;
      place-items: center;
      min-height: 100vh;
      margin: 0;
      padding: max(2rem, env(safe-area-inset-top)) max(1rem, env(safe-area-inset-right))
        max(2rem, env(safe-area-inset-bottom)) max(1rem, env(safe-area-inset-left));
      overflow-x: hidden;
      color: var(--text);
      background:
        radial-gradient(ellipse at 12% 12%, rgba(35, 151, 133, .2), transparent 36rem),
        radial-gradient(ellipse at 90% 85%, rgba(73, 96, 190, .2), transparent 34rem),
        var(--page);
    }}
    body::before {{
      position: fixed;
      z-index: -1;
      inset: 0;
      background-image: radial-gradient(rgba(203, 220, 242, .13) .7px, transparent .7px);
      background-size: 24px 24px;
      content: "";
      mask-image: linear-gradient(to bottom, black, transparent 90%);
    }}
    main {{
      display: grid;
      align-content: start;
      gap: 1.25rem;
      width: min(100%, 760px);
      padding: clamp(1.25rem, 5vw, 2.5rem);
      border: 1px solid var(--line);
      border-radius: 28px;
      background: linear-gradient(145deg, rgba(20, 31, 50, .96), rgba(11, 18, 32, .94));
      box-shadow: 0 32px 90px rgba(0, 0, 0, .42), inset 0 1px rgba(255, 255, 255, .045);
      animation: card-enter .65s cubic-bezier(.2, .75, .25, 1) both;
    }}
    .eyebrow {{
      margin: 0 0 -.85rem;
      color: var(--accent);
      font-size: .75rem;
      font-weight: 800;
      letter-spacing: .18em;
    }}
    h1 {{
      margin: 0;
      font-size: clamp(1.9rem, 7vw, 3rem);
      letter-spacing: -.045em;
      line-height: 1.08;
    }}
    p {{ margin: 0; color: var(--muted); line-height: 1.65; }}
    section {{ display: grid; gap: 1rem; }}
    video {{
      display: block;
      width: 100%;
      max-height: min(65vh, 720px);
      aspect-ratio: 4 / 3;
      object-fit: contain;
      border: 1px solid var(--line);
      border-radius: 20px;
      background: #05080e;
      box-shadow: 0 18px 45px rgba(0, 0, 0, .28);
    }}
    button {{
      width: 100%;
      min-height: 54px;
      padding: .9rem 1.2rem;
      border: 0;
      border-radius: 15px;
      color: #06231d;
      background: linear-gradient(115deg, #87f5d6, #48d8b4);
      font: inherit;
      font-weight: 750;
      cursor: pointer;
      touch-action: manipulation;
      box-shadow: 0 8px 24px rgba(55, 205, 167, .16);
      transition: transform .2s ease, box-shadow .2s ease, filter .2s ease;
      animation: button-enter .45s ease both;
    }}
    button:hover:not(:disabled) {{
      transform: translateY(-2px);
      filter: brightness(1.06);
      box-shadow: 0 13px 30px rgba(55, 205, 167, .27);
    }}
    button:active:not(:disabled) {{ transform: translateY(1px) scale(.99); }}
    button:focus-visible, a:focus-visible, input:focus-visible {{
      outline: 3px solid #fff;
      outline-offset: 3px;
    }}
    button:disabled {{
      color: #758298;
      background: #273247;
      cursor: not-allowed;
      box-shadow: none;
      animation: none;
    }}
    #invite {{
      overflow-wrap: anywhere;
      padding: 1rem 1.1rem;
      border: 1px solid var(--line);
      border-radius: 16px;
      background: rgba(5, 10, 19, .45);
    }}
    #invite:empty {{ display: none; }}
    #invite a {{ display: inline-block; padding: .35rem 0; color: var(--accent); }}
    #invite button {{ margin-top: .7rem; }}
    #status {{
      min-height: 3.25rem;
      margin: 0;
      padding: .9rem 1.1rem;
      border: 1px solid var(--line);
      border-radius: 15px;
      background: rgba(5, 10, 19, .52);
      color: #d1dbea;
      line-height: 1.5;
    }}
    .notice {{
      margin: 0;
      padding: 1rem 1.1rem;
      border: 1px solid rgba(248, 196, 94, .24);
      border-inline-start: 4px solid #f3bd59;
      border-radius: 14px;
      background: rgba(243, 189, 89, .09);
      color: #f3dfb9;
    }}
    #camera-active-indicator {{ border-color: rgba(76, 224, 176, .28); border-inline-start-color: var(--accent-strong); background: rgba(76, 224, 176, .09); color: #c6f6e8; }}
    #quiz-panel {{
      gap: 1rem;
      padding: clamp(1rem, 4vw, 1.5rem);
      border: 1px solid rgba(114, 240, 206, .22);
      border-radius: 20px;
      background: linear-gradient(145deg, rgba(23, 44, 58, .92), rgba(17, 28, 46, .96));
      animation: card-enter .35s ease both;
    }}
    #quiz-panel h2 {{ margin: 0; color: var(--text); font-size: 1.4rem; }}
    #quiz-panel label {{ display: grid; gap: .5rem; color: #dce6f3; font-weight: 650; }}
    #quiz-answer {{
      width: 100%;
      min-height: 52px;
      padding: .8rem 1rem;
      border: 1px solid var(--line);
      border-radius: 13px;
      color: var(--text);
      background: rgba(5, 10, 19, .65);
      font: inherit;
    }}
    #quiz-feedback {{ min-height: 1.65rem; color: var(--accent); }}
    #stop-session {{ color: #fff; background: linear-gradient(115deg, #f46f83, #d94966); box-shadow: 0 8px 24px rgba(217, 73, 102, .17); }}
    #stop-session:hover:not(:disabled) {{ box-shadow: 0 13px 30px rgba(217, 73, 102, .3); }}
    @keyframes card-enter {{
      from {{ opacity: 0; transform: translateY(12px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes button-enter {{
      from {{ opacity: .7; transform: translateY(5px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      *, *::before, *::after {{
        scroll-behavior: auto !important;
        animation-duration: .01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: .01ms !important;
      }}
    }}
    @media (max-width: 600px) {{
      body {{ min-height: 100dvh; padding-inline: .8rem; }}
      main {{ gap: 1rem; border-radius: 22px; }}
      video {{ aspect-ratio: 3 / 4; max-height: 52dvh; border-radius: 16px; }}
      #viewer-panel video {{ aspect-ratio: 4 / 3; max-height: 38dvh; }}
    }}
  </style>
</head>
<body>
  <main>
    <p class="eyebrow">KUIS BASIC MATEMATIKA · LIVE DENGAN IZIN</p>
    <h1>Kuis Basic Matematika</h1>
    <section id="viewer-panel" hidden>
      <p>Buat tautan undangan pribadi, lalu kirim hanya kepada orang yang akan berbagi kamera.</p>
      <button id="create-session" type="button">Buat sesi dan tautan undangan</button>
      <p id="invite"></p>
      <video id="remote-video" autoplay playsinline hidden></video>
    </section>
    <section id="camera-panel" hidden>
      <p class="notice">
        Jika Anda melanjutkan, kamera akan dinyalakan setelah izin browser diberikan
        dan video live akan terlihat oleh orang yang mengirim tautan undangan ini.
        Video dikirim langsung ke browser orang tersebut dan tidak direkam atau
        disimpan oleh aplikasi ini.
      </p>
      <button id="start-camera" type="button">Mulai kuis &amp; bagikan kamera</button>
      <video id="local-video" autoplay playsinline muted hidden></video>
      <p id="camera-active-indicator" class="notice" role="status" aria-live="polite" hidden>
        Kamera aktif. Pratinjau disembunyikan selama kuis; live dibagikan ke pengundang.
        Tekan <strong>Hentikan sesi</strong> untuk menghentikan kamera dan berbagi.
      </p>
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
    const cameraActiveIndicator = document.querySelector("#camera-active-indicator");
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
      localVideo.hidden = true;
      cameraActiveIndicator.hidden = true;
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
          remoteVideo.hidden = false;
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
        localVideo.hidden = true;
        cameraActiveIndicator.hidden = false;
        stopButton.hidden = false;
        quizIndex = 0;
        quizPanel.hidden = false;
        document.querySelector("#open-quiz").hidden = true;
        showQuizQuestion();
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
        stopButton.hidden = true;
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
      if (localVideo) localVideo.hidden = true;
      cameraActiveIndicator.hidden = true;
      if (remoteVideo) {{
        remoteVideo.srcObject = null;
        remoteVideo.hidden = true;
      }}
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
        localVideo.hidden = false;
        setStatus("Kuis selesai. Semua 10 jawaban benar.");
        return;
      }}
      feedback.textContent = "Benar!";
      showQuizQuestion();
    }});
    document.querySelector("#close-quiz").addEventListener("click", () => {{
      quizPanel.hidden = true;
      document.querySelector("#open-quiz").hidden = false;
      localVideo.hidden = false;
    }});
    document.querySelector("#open-quiz").addEventListener("click", () => {{
      quizPanel.hidden = false;
      document.querySelector("#open-quiz").hidden = true;
      localVideo.hidden = true;
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
