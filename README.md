# Website kamera dengan persetujuan

Website ini membuat tautan undangan privat untuk sesi kamera WebRTC.
Orang yang membuka undangan perlu menekan tombol berbagi dan menyetujui prompt
kamera browser. Video live dikirim langsung antar-browser; aplikasi tidak
merekam atau menyimpan videonya.

## Publikasikan gratis dengan Netlify + Render

Publikasi ini memerlukan akun Netlify, Render, dan GitHub. Saya tidak bisa masuk
atau membuat layanan di akun Anda. Jangan kirim kata sandi, token, atau private
key lewat chat.

### 1. Unggah proyek ke GitHub

1. Buat repository baru di GitHub.
2. Unggah file proyek berikut ke repository, dengan struktur folder tetap sama:
   `.gitignore`, `README.md`, `hack.py`, `build_site.py`, `netlify.toml`,
   `render.yaml`, `requirements.txt`, `requirements-build.txt`, dan folder
   `deploy/`.
3. Jangan unggah folder `.venv` atau folder hasil build `site/`.

### 2. Deploy backend signaling di Render

1. Masuk ke [Render](https://render.com/) dan pilih **New → Blueprint**.
2. Hubungkan repository GitHub proyek ini.
3. Render akan membaca `render.yaml`; pilih **Apply** untuk membuat web service.
   Blueprint memasang dependensi, menjalankan satu worker, dan memeriksa
   `/healthz`.
4. Tunggu deploy selesai. Di halaman service Render, pastikan statusnya **Live**
   dan buka URL HTTPS yang diberikan, misalnya
   `https://camera-consent-backend.onrender.com/healthz`. Hasil yang benar:
   `{"status":"ok"}`. Salin origin domainnya saja, misalnya
   `https://camera-consent-backend.onrender.com`.

### 3. Deploy halaman di Netlify

1. Masuk ke [Netlify](https://app.netlify.com/) dan pilih **Add new site →
   Import an existing project**.
2. Hubungkan repository GitHub yang sama. `netlify.toml` mengatur perintah
   build dan folder publik secara otomatis.
3. Di **Site configuration → Environment variables**, tambahkan:

   ```text
   SIGNALING_ORIGIN=https://camera-consent-backend.onrender.com
   ```

   Ganti contoh tersebut dengan origin HTTPS Render Anda, tanpa path dan tanpa
   garis miring di bagian akhir.
4. Jalankan **Trigger deploy → Deploy site**. Tunggu hingga status deploy sukses.
5. Buka URL HTTPS Netlify, klik **Buat sesi dan tautan undangan**, lalu bagikan
   tautan privat yang dihasilkan. Tautan kamera bekerja di browser ponsel maupun
   desktop melalui HTTPS.

### 4. Uji alur sesi

1. Buka situs Netlify di desktop dan buat sesi.
2. Kirim undangan yang dihasilkan hanya kepada orang yang memang setuju berbagi
   kameranya.
3. Penerima membuka undangan, membaca pemberitahuan, menekan tombol persetujuan,
   lalu menyetujui izin kamera yang ditampilkan browser.
4. Live akan tampil di halaman desktop. Tekan **Hentikan sesi** untuk mengakhiri
   berbagi.

## Batasan layanan gratis

- Backend Render pada paket gratis dapat tidur saat tidak digunakan, sehingga
  kunjungan pertama bisa lambat. Restart atau tidur dapat menghapus sesi yang
  sedang menunggu karena state signaling sementara disimpan di memori. Jangan
  gunakan untuk sesi yang memerlukan ketersediaan terjamin.
- Jalankan backend dengan satu worker dan satu instance. Beberapa worker tidak
  dapat berbagi state sesi ini.
- Sesi undangan kedaluwarsa setelah satu jam tidak aktif. Siapa pun yang memiliki
  tautan undangan privat dapat mencoba bergabung.
- Video peer-to-peer tidak melewati server Netlify atau server signaling.
  Sebagian jaringan ketat mungkin membutuhkan TURN; STUN saja tidak menjamin
  semua jaringan dapat tersambung.
- Jangan aktifkan pencatatan header `Authorization` pada proxy/backend; header
  tersebut membawa token sesi undangan.
