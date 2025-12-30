# STN Diklat Panel 🚗⚡

Sistem Panel Diklat Smart Tuning Nusantara - Platform pembelajaran otomotif untuk teknisi EFI dan sensor.

## ✨ Fitur

- ✅ Registrasi dan Login User/Admin
- ✅ Dashboard interaktif dengan jadwal
- ✅ Upload bukti pembayaran
- ✅ Verifikasi pembayaran oleh admin
- ✅ Manajemen peserta diklat
- ✅ Integrasi Google Drive untuk materi
- ✅ Rate limiting dan CSRF protection
- ✅ Responsive design

## 🚀 Quick Start

### Persiapan Environment

1. **Clone repository:**
   ```bash
   git clone https://github.com/smarttuning24-prog/STN-diklat-panel.git
   cd STN-diklat-panel
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env dengan SECRET_KEY yang aman
   ```

4. **Initialize database:**
   ```bash
   python run.py  # Database akan dibuat otomatis
   ```

5. **Create admin account:**
   ```bash
   python add_admin.py
   ```

## 🌍 Deployment Options

### 1. GitHub Codespaces (Development)

Aplikasi otomatis terdeteksi sebagai Codespaces dan mengkonfigurasi CSP yang sesuai.

```bash
python run.py
# Akan running di port yang disediakan Codespaces
```

### 2. Local Development

```bash
# Development mode
FLASK_ENV=development python run.py
# Access: http://localhost:5000

# Dengan debug
DEBUG=True FLASK_ENV=development python run.py
```

### 3. Production Server

```bash
# Production mode
FLASK_ENV=production SECRET_KEY=your-secret-key python run.py
# Access: http://your-server:8000
```

### 4. Docker Deployment

```bash
# Build and run
docker-compose up -d

# Atau manual
docker build -t stn-diklat-panel .
docker run -p 8000:8000 -e SECRET_KEY=your-secret-key stn-diklat-panel
```

### 5. Gunicorn (Production WSGI)

```bash
# Install gunicorn
pip install gunicorn

# Run dengan gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 4 wsgi:application
```

## ⚙️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | ❌ Required | Flask secret key untuk security |
| `FLASK_ENV` | `production` | Environment: development/production |
| `HOST` | `127.0.0.1` (dev) / `0.0.0.0` (prod) | Server host |
| `PORT` | `5000` (dev) / `8000` (prod) | Server port |
| `DEBUG` | `False` | Enable Flask debug mode |

## 🗄️ Database

### SQLite (Default - Simple)
- File: `database/users.db`
- Otomatis dibuat saat pertama run
- Cocok untuk development dan small production

### PostgreSQL (Production Recommended)
```bash
# Set environment variable
export SQLALCHEMY_DATABASE_URI=postgresql://user:password@localhost/dbname
```

## 🔒 Security Features

- **CSRF Protection**: Enabled dengan konfigurasi adaptif
- **Rate Limiting**: Mencegah brute force attacks
- **Content Security Policy**: Konfigurasi berdasarkan environment
- **Secure Headers**: X-Frame-Options, X-Content-Type-Options, dll
- **Password Hashing**: bcrypt untuk password security

## 📁 Project Structure

```
STN-diklat-panel/
├── app/
│   ├── __init__.py      # App factory & configuration
│   ├── models.py        # Database models
│   ├── routes.py        # Route handlers
│   ├── security.py      # Security utilities
│   └── templates/       # Jinja2 templates
│       ├── admin/       # Admin pages
│       └── user/        # User pages
├── database/            # SQLite database files
├── instance/            # Instance-specific files
│   ├── uploads/         # File uploads
│   └── cache/           # Cache files
├── static/              # Static assets (CSS, JS, images)
├── .env.example         # Environment template
├── requirements.txt     # Python dependencies
├── run.py              # Development server
├── wsgi.py             # Production WSGI entry
├── Dockerfile          # Docker configuration
└── docker-compose.yml  # Docker Compose
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest

# Test specific functionality
python test_rate_limit.py
python test_rate_limit_full.py
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/
# Should return 200 OK
```

### Logs
- Flask logs otomatis ditampilkan di console
- Untuk production, gunakan log aggregation service

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
lsof -i :8080
# Kill process or change port
PORT=8081 python run.py
```

#### 2. SECRET_KEY Missing
```bash
# Generate secure key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set environment variable
export SECRET_KEY=generated-key-here
```

#### 3. Database Permission Error
```bash
# Fix permissions
chmod 755 database/
chmod 644 database/users.db
```

#### 4. Upload Folder Missing
```bash
# Create manually
mkdir -p instance/uploads
chmod 755 instance/uploads
```

### Environment-Specific Issues

#### GitHub Codespaces
- CSP otomatis dikonfigurasi untuk compatibility
- Port otomatis dideteksi dari environment

#### Production Server
- Pastikan SECRET_KEY kuat dan unik
- Gunakan reverse proxy (nginx) untuk SSL
- Monitor resource usage

## 🤝 Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/smarttuning24-prog/STN-diklat-panel/issues)
- **Discussions**: [GitHub Discussions](https://github.com/smarttuning24-prog/STN-diklat-panel/discussions)

---

**Dibuat dengan ❤️ untuk komunitas otomotif Indonesia**