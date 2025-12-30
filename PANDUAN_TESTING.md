# Panduan Testing untuk STN-diklat-panel

## Pendahuluan
Panduan ini menjelaskan cara melakukan testing pada aplikasi STN-diklat-panel, yang merupakan sistem panel diklat (pelatihan) dengan fitur admin dan user.

## Persiapan Testing

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Database
```bash
# Hapus database lama jika ada
rm -f database/users.db

# Jalankan aplikasi untuk membuat database baru
python run.py
# Tekan Ctrl+C setelah database dibuat
```

### 3. Buat Akun Admin
```bash
python add_admin.py
```

## Jenis Testing

### 1. Unit Testing
- Test fungsi-fungsi individual
- Contoh: validasi password, hashing password

### 2. Integration Testing
- Test interaksi antara komponen
- Contoh: login admin, upload file

### 3. End-to-End Testing
- Test alur lengkap dari user
- Contoh: registrasi user sampai pembayaran

## Menjalankan Test

### Test Rate Limiting
```bash
# Jalankan server di background
python run.py &

# Jalankan test rate limiting
python test_rate_limit.py

# Atau test lengkap dengan auto-start server
python test_rate_limit_full.py
```

### Test Manual di Browser
1. Buka `http://localhost:5000`
2. Test login admin dengan username: `admin`, password: `admin123`
3. Test registrasi user
4. Test upload pembayaran
5. Test fitur admin (kelola peserta, dll.)

### Test Import Data
```bash
# Test import CSV untuk kontak
# Buat file CSV dengan kolom: phone, name, email, group
# Upload via admin panel
```

## Test Cases Utama

### Login dan Autentikasi
- [ ] Login admin berhasil
- [ ] Login admin gagal dengan password salah
- [ ] Rate limiting aktif setelah 5 kali gagal
- [ ] CSRF protection aktif

### Registrasi User
- [ ] Registrasi berhasil dengan data valid
- [ ] Validasi password (minimal 8 karakter, angka, huruf besar)
- [ ] Validasi WhatsApp unik

### Upload dan Pembayaran
- [ ] Upload file PDF/JPG berhasil
- [ ] Upload file exe ditolak
- [ ] File terlalu besar ditolak
- [ ] Verifikasi pembayaran oleh admin

### Fitur Admin
- [ ] Lihat daftar peserta dengan pagination
- [ ] Search peserta
- [ ] Edit data peserta
- [ ] Import batch dari CSV
- [ ] Buat grup batch

### Performance
- [ ] Load time halaman < 2 detik
- [ ] Query database dengan index cepat
- [ ] Caching Google Drive aktif

## Tools Testing

### Automated Testing
- `test_rate_limit.py` - Test rate limiting
- `test_rate_limit_full.py` - Test lengkap dengan server auto-start

### Manual Testing
- Browser untuk UI testing
- Postman untuk API testing
- Database viewer untuk cek data

## Troubleshooting

### Server tidak start
- Cek port 5000 tidak digunakan
- Cek dependencies terinstall
- Cek database file ada

### Test gagal
- Pastikan server running
- Cek URL dan port benar
- Cek data test valid

### Database error
- Hapus database dan buat ulang
- Jalankan migration jika ada

## Checklist Testing

- [ ] Semua dependencies terinstall
- [ ] Database fresh dibuat
- [ ] Admin account dibuat
- [ ] Server bisa start
- [ ] Login admin berhasil
- [ ] Registrasi user berhasil
- [ ] Upload file berhasil
- [ ] Fitur admin berfungsi
- [ ] Rate limiting aktif
- [ ] CSRF protection aktif
- [ ] Pagination berfungsi
- [ ] Search berfungsi
- [ ] Import CSV berhasil
- [ ] Performance baik

## Catatan
- Gunakan data test yang konsisten
- Backup database sebelum testing destruktif
- Dokumentasikan bug yang ditemukan
- Test di berbagai browser jika memungkinkan</content>
<parameter name="filePath">/workspaces/STN-diklat-panel/PANDUAN_TESTING.md