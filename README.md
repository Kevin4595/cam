# Website kamera dengan persetujuan

Website statis ini diterbitkan gratis oleh GitHub Pages. PeerJS Cloud dipakai
untuk menemukan browser dan menukar informasi awal WebRTC. Setelah tersambung,
video dikirim langsung antar-browser dan tidak direkam atau disimpan website.

Orang yang membuka undangan perlu menekan tombol berbagi dan menyetujui prompt
kamera browser. Bagikan undangan hanya kepada orang yang memang setuju.

## Terbitkan ke GitHub Pages

1. Pastikan repository menggunakan branch `main` dan workflow
   `.github/workflows/pages.yml` ada di branch tersebut.
2. Buka **Settings → Pages** dan pilih **GitHub Actions** pada bagian
   **Build and deployment → Source**.
3. Buka tab **Actions**, pilih workflow **Publish website**, lalu jalankan
   **Run workflow**. Workflow juga berjalan otomatis setiap ada push ke `main`.
4. Tunggu workflow selesai dengan status sukses. Untuk repository ini, URL situs
   adalah `https://kevin4595.github.io/cam/`.

## Gunakan tautan undangan

1. Buka website pada desktop dan klik **Buat sesi dan tautan undangan**.
2. Bagikan tautan pribadi yang muncul hanya kepada orang yang akan berbagi
   kameranya.
3. Penerima membuka undangan, membaca pemberitahuan, menekan tombol persetujuan,
   dan menyetujui izin kamera dari browser.
4. Live tampil pada halaman desktop. Tekan **Hentikan sesi** untuk mengakhiri
   berbagi kamera.
5. Setelah kamera penerima menyala, kuis 10 soal matematika dasar akan muncul.
   Jawaban yang salah dapat dicoba lagi; kuis dapat ditutup atau dibuka kembali
   sebelum selesai, lalu otomatis tertutup setelah jawaban benar untuk soal
   terakhir dikirim. Tombol **Hentikan sesi** tetap tersedia.

## Biaya dan batasan

- GitHub Pages dan PeerJS Cloud yang digunakan sebagai broker default tidak
  memerlukan konfigurasi Render, Firebase, kartu, atau private key pada proyek.
- PeerJS Cloud adalah layanan publik pihak ketiga; ketersediaan dan batas
  pemakaian tidak dijamin oleh proyek ini. Peer ID publik akan terlihat di
  undangan selama sesi aktif. Gunakan tautan hanya untuk sesi yang memang Anda
  harapkan, lalu hentikan sesi setelah selesai.
- Video WebRTC tidak melewati GitHub Pages atau PeerJS Cloud. Sebagian jaringan
  ketat mungkin memerlukan server TURN; TURN pihak ketiga mungkin berbayar.
- Akses kamera hanya berjalan setelah penerima menyetujui prompt situs dan izin
  kamera browser.
