# Django-dbt Self-Service Analytics Platform

Platform self-service analytics yang menggabungkan Django untuk data ingestion dan dbt untuk data transformation.

## 🚀 Fitur

- **CSV Upload**: Upload file CSV melalui web interface
- **Automatic dbt Processing**: Data otomatis diproses menggunakan dbt setelah upload
- **Async Pipeline**: dbt berjalan di background thread (non-blocking)
- **Pipeline Logging**: Semua dbt run disimpan ke database untuk tracking
- **Re-run Pipeline**: Button untuk menjalankan ulang pipeline
- **Achievement Metrics**: Dashboard metrics untuk monitoring
- **Real-time Status**: Auto-refresh status pipeline

## 📋 Prerequisites

- Docker & Docker Compose
- Git

## 🛠️ Installation

1. Clone repository:
```bash
git clone <your-repo-url>
cd django_dbt_platform
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Edit `.env` file dan isi dengan credentials Anda

4. Build dan jalankan dengan Docker:
```bash
docker-compose up -d
```

5. Buat migration (jika diperlukan):
```bash
docker-compose exec web python django_app/manage.py makemigrations
docker-compose exec web python django_app/manage.py migrate
```

6. Buat superuser (optional):
```bash
docker-compose exec web python django_app/manage.py createsuperuser
```

## 🌐 Access

- **Django App**: http://localhost:8000
- **Upload Page**: http://localhost:8000/upload/
- **Admin Panel**: http://localhost:8000/admin/
- **PgAdmin**: http://localhost:5050

## 📁 Project Structure

```
django_dbt_platform/
├── django_app/              # Django application
│   ├── config/              # Django settings
│   └── uploads/             # Upload app
│       ├── models.py        # Database models
│       ├── views.py         # Views & dbt integration
│       └── templates/       # HTML templates
├── dbt_project/             # dbt project files
│   └── models/              # dbt models
├── dbt_profiles/            # dbt profiles configuration
├── docker-compose.yml       # Docker configuration
├── Dockerfile              # Docker image definition
└── requirements.txt        # Python dependencies
```

## 🔧 Configuration

### Database
Database PostgreSQL dikonfigurasi melalui environment variables di `.env` atau `docker-compose.yml`.

### dbt Configuration
dbt profiles ada di `dbt_profiles/profiles.yml`. Pastikan environment variables sudah di-set dengan benar.

## 📊 Usage

1. **Upload CSV**: 
   - Buka http://localhost:8000/upload/
   - Upload file CSV dengan kolom `order_delivered_carrier_date`
   - Data akan otomatis disimpan dan dbt pipeline akan berjalan

2. **Monitor Pipeline**:
   - Status pipeline ditampilkan di halaman upload
   - Klik "Re-run Pipeline" untuk menjalankan ulang
   - Lihat metrics di Achievement Metrics card

3. **View Data**:
   - Raw data: Tabel `raw_user_targets`
   - Processed data: Tabel `user_targets_clean` (hasil dbt)
   - Pipeline logs: Tabel `dbt_run_logs`

## 🗄️ Database Tables

- `raw_user_targets`: Data mentah dari CSV upload
- `user_targets_clean`: Data hasil transformasi dbt
- `dbt_run_logs`: Log semua dbt run

## 🛡️ Security Notes

⚠️ **PENTING**: Sebelum push ke production:
- Ganti semua password di `.env`
- Set `DEBUG=False` di production
- Gunakan secret key yang aman
- Jangan commit file `.env` ke Git

## 📝 License

MIT License

## 👤 Author

Your Name

## 🙏 Acknowledgments

- Django
- dbt (data build tool)
- PostgreSQL
