# Setup GitHub Repository

## Langkah-langkah Upload ke GitHub

### 1. Buat Repository di GitHub
- Buka https://github.com/new
- Nama repository: `Django-dbt-Self-Service-Analytics-Platform` (atau sesuai yang Anda inginkan)
- Pilih Public atau Private
- **JANGAN** centang "Initialize with README" (karena kita sudah punya)
- Klik "Create repository"

### 2. Tambahkan Remote dan Push

Jalankan command berikut (ganti `YOUR_USERNAME` dengan username GitHub Anda):

```bash
cd C:\Users\aryag\Documents\Latihan_DBT\django_dbt_platform

# Tambahkan remote (ganti YOUR_USERNAME dengan username GitHub Anda)
git remote add origin https://github.com/YOUR_USERNAME/Django-dbt-Self-Service-Analytics-Platform.git

# Atau jika menggunakan SSH:
# git remote add origin git@github.com:YOUR_USERNAME/Django-dbt-Self-Service-Analytics-Platform.git

# Push ke GitHub
git push -u origin main
```

### 3. Jika Branch Masih "master"

Jika branch Anda masih bernama "master", jalankan:

```bash
git branch -M main
git push -u origin main
```

### 4. Verifikasi

Setelah push berhasil, buka repository di GitHub dan pastikan semua file sudah ter-upload.

## Catatan Penting

⚠️ **Sebelum Push, Pastikan:**
- File `.env` TIDAK ter-commit (sudah ada di .gitignore)
- Password di `docker-compose.yml` dan `settings.py` sudah di-review
- File `logs/` dan `target/` tidak ter-commit (sudah ada di .gitignore)

## Troubleshooting

### Jika ada error "remote origin already exists":
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/Django-dbt-Self-Service-Analytics-Platform.git
```

### Jika perlu update .gitignore:
```bash
# Edit .gitignore, lalu:
git add .gitignore
git commit -m "Update .gitignore"
git push
```
