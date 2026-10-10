# Website kamera dengan persetujuan

Website statis ini di-host oleh GitHub Pages. Firebase Realtime Database dipakai
hanya untuk pertukaran sinyal WebRTC; video dikirim langsung antar-browser dan
tidak direkam atau disimpan oleh aplikasi.

Orang yang membuka undangan harus menekan tombol berbagi dan menyetujui prompt
kamera browser. Bagikan tautan undangan hanya kepada orang yang setuju.

## Publikasi gratis

Deployment ini menggunakan GitHub Pages dan Firebase Spark. Paket Spark
Realtime Database memiliki kuota gratis **1 GB penyimpanan** dan **10 GB
unduhan per bulan**. Menurut Firebase, Spark tidak meminta informasi pembayaran
untuk produk gratis. Jangan meng-upgrade proyek ke Blaze atau menambahkan
informasi tagihan jika ingin menjaga penggunaan tanpa pembayaran.

### 1. Buat proyek Firebase tanpa menambahkan billing

1. Buka [Firebase Console](https://console.firebase.google.com/) dengan akun
   Google Anda, lalu buat project baru. Lewati pengaturan Google Analytics jika
   tidak diperlukan. Jangan pilih paket Blaze.
2. Di project, pilih **Add app → Web** dan daftarkan aplikasi web. Salin objek
   `firebaseConfig` yang ditampilkan. Ini konfigurasi aplikasi web publik,
   bukan kata sandi atau private key.
3. Buka **Authentication → Sign-in method** dan aktifkan provider **Anonymous**.
   Setelah GitHub Pages aktif, tambahkan `kevin4595.github.io` tanpa skema
   maupun path ke **Authentication → Settings → Authorized domains**.
4. Buka **Realtime Database → Create database** dan buat database pada mode
   locked/secure.
5. Pada tab **Rules**, tempel seluruh isi [`database.rules.json`](./database.rules.json)
   lalu klik **Publish**. Jangan menggantinya dengan aturan yang mengizinkan
   pembacaan atau penulisan publik tanpa autentikasi.

### 2. Tambahkan konfigurasi Firebase ke GitHub

1. Buka repository proyek
   [`Kevin4595/cam`](https://github.com/Kevin4595/cam), lalu pilih
   **Settings → Secrets and variables → Actions → Variables**.
2. Tambahkan repository variable bernama `FIREBASE_CONFIG`.
3. Isikan objek JSON `firebaseConfig` yang disalin dari Firebase console, contoh
   formatnya:

   ```json
   {
     "apiKey": "API_KEY_DARI_FIREBASE",
     "authDomain": "PROJECT_ID.firebaseapp.com",
     "databaseURL": "https://PROJECT_ID-default-rtdb.REGION.firebasedatabase.app",
     "projectId": "PROJECT_ID",
     "appId": "APP_ID"
   }
   ```

   Pakai nilai asli dari console, termasuk `databaseURL` yang tepat untuk region
   database Anda. Jangan masukkan service-account JSON, private key, atau
   kredensial administrator ke variable ini.

### 3. Aktifkan GitHub Pages

1. Di repository, buka **Settings → Pages**.
2. Pada **Build and deployment → Source**, pilih **GitHub Actions**.
3. Buka tab **Actions**, pilih workflow **Publish website**, lalu tekan
   **Run workflow**. Workflow juga berjalan otomatis setiap kali ada perubahan
   di branch `main`.
4. Tunggu sampai workflow selesai dengan status sukses. URL situs akan berbentuk
   `https://kevin4595.github.io/cam/`.

Jika variable Firebase belum ada saat workflow berjalan, build menampilkan
halaman tanpa fungsi sesi. Tambahkan variable terlebih dahulu, lalu jalankan
workflow kembali.

### 4. Gunakan undangan kamera

1. Buka URL GitHub Pages di desktop dan klik **Buat sesi dan tautan undangan**.
2. Bagikan tautan privat yang dibuat hanya kepada orang yang akan berbagi kamera.
3. Penerima membuka tautan, membaca pemberitahuan, menekan tombol persetujuan,
   lalu menyetujui izin kamera yang ditampilkan browser.
4. Live tampil pada halaman pengundang. Tekan **Hentikan sesi** untuk mengakhiri
   sesi.

## Batasan dan keamanan

- Tidak ada backend Render atau layanan berbayar yang digunakan. Video WebRTC
  tidak melewati GitHub Pages atau Firebase.
- Database Rules hanya memberi akses kepada pengguna Firebase yang sudah masuk
  secara anonim, dengan ID sesi acak 128-bit. Setiap sesi kedaluwarsa setelah
  satu jam dan dihapus saat pengundang menutup koneksi atau menekan tombol
  berhenti.
- Bila halaman desktop ditutup paksa atau koneksi terputus, Firebase menghapus
  sesi melalui `onDisconnect`. Data yang dibuat di Firebase dapat diperiksa dan
  dihapus dari console.
- Firebase Spark memberi kuota gratis yang terbatas. Jika kuota terlampaui,
  layanan gratis dapat berhenti sampai kuota pulih; jangan aktifkan billing bila
  Anda tidak ingin biaya.
- STUN digunakan untuk koneksi peer-to-peer. Sebagian jaringan ketat mungkin
  tidak tersambung tanpa server TURN; TURN pihak ketiga bisa berbayar.
- Halaman tersedia publik, tetapi kamera tidak menyala otomatis: penerima harus
  menyetujui pemberitahuan situs dan izin kamera dari browser.

## Mencoba build secara lokal

```powershell
$env:FIREBASE_CONFIG = '{"apiKey":"...","authDomain":"...","databaseURL":"...","projectId":"...","appId":"..."}'
& "C:\path\to\python.exe" build_site.py
```

Lalu sajikan folder `site` menggunakan server HTTP lokal. Untuk mencoba kamera
dari internet, gunakan situs GitHub Pages HTTPS.
