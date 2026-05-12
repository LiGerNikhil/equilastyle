# EQUILA STYLE - Production Deployment Guide

## 🚀 Overview
This guide covers deploying EQUILA STYLE to production VPS server with domain `equilastyle.com` and IP `187.127.147.152`.

## 📋 Prerequisites
- Ubuntu/Debian server with SSH access
- Python 3.8+ installed
- Git installed
- Domain pointed to VPS IP
- SSL certificate configured (optional but recommended)

## 🔧 Environment Setup

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd equila-demo
```

### 2. Set Up Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual production values:
nano .env
```

**Required Environment Variables:**
- `SECRET_KEY`: Generate new Django secret key
- `DEBUG`: Set to `False`
- `ALLOWED_HOSTS`: Your domain and IP
- `DATABASE_URL`: SQLite database path
- `RAZORPAY_KEY_ID`: Production Razorpay key ID
- `RAZORPAY_KEY_SECRET`: Production Razorpay secret
- `RAZORPAY_CURRENCY`: Set to `INR`

### 3. Generate Django Secret Key
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 📦 Install Dependencies
```bash
# Install production requirements
pip install -r requirements.txt

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🗄️ Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## 📁 Collect Static Files
```bash
# Collect all static files for production
python manage.py collectstatic --noinput --clear
```

## 🚀 Deployment Options

### Option 1: Gunicorn (Recommended)
```bash
# Start with Gunicorn
gunicorn --bind 187.127.147.152:8000 equila_fashion.wsgi:application

# Run in background
nohup gunicorn --bind 187.127.147.152:8000 equila_fashion.wsgi:application > gunicorn.log &
```

### Option 2: Systemd Service (Production)
Create `/etc/systemd/equila-style.service`:
```ini
[Unit]
Description=EQUILA STYLE Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/equila-demo
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/gunicorn --workers 3 --bind 187.127.147.152:8000 equila_fashion.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID

[Install]
WantedBy=multi-user.target

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable equila-style.service
sudo systemctl start equila-style.service
```

## 🌐 Nginx Configuration (Optional)
Create `/etc/nginx/sites-available/equila-style`:
```nginx
server {
    listen 80;
    server_name equilastyle.com www.equilastyle.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name equilastyle.com www.equilastyle.com;
    
    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;
    
    # Django static files
    location /static/ {
        alias /path/to/equila-demo/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Django media files
    location /media/ {
        alias /path/to/equila-demo/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Django application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔒 Security Settings
The application is configured with:
- ✅ DEBUG mode disabled
- ✅ Secure SSL redirect
- ✅ HSTS security headers
- ✅ Secure cookies
- ✅ CSRF protection
- ✅ XSS protection
- ✅ Clickjacking protection

## 📊 Monitoring & Logs

### Check Application Status
```bash
# Check if Django is running
ps aux | grep gunicorn

# View logs
tail -f gunicorn.log

# Check systemd service
sudo systemctl status equila-style.service
```

## 🔄 Deployment Automation

### Using Deploy Script
```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

## 🌍 Domain Configuration
- **Primary Domain**: equilastyle.com
- **VPS IP**: 187.127.147.152
- **Port**: 8000 (application), 80/443 (web server)
- **Database**: SQLite (production-ready)
- **Static Files**: Collected to `/staticfiles/`

## 📱 Production Checklist
- [ ] Update SECRET_KEY with secure value
- [ ] Configure SSL certificates
- [ ] Set up domain DNS records
- [ ] Configure firewall rules
- [ ] Set up backup strategy
- [ ] Test payment gateway in production
- [ ] Monitor application performance

## 🚨 Troubleshooting

### Common Issues:
1. **Static files not loading**: Run `collectstatic` again
2. **Database errors**: Check file permissions
3. **Permission denied**: Check user/group permissions
4. **502 Bad Gateway**: Check if Gunicorn is running

### Log Locations:
- Django logs: Check Django logging configuration
- Gunicorn logs: `gunicorn.log` or journalctl
- Nginx logs: `/var/log/nginx/error.log`

## 📞 Support
For deployment issues, check:
1. Django error logs
2. Gunicorn process status
3. Nginx configuration and logs
4. VPS resource usage

---

**Deployment completed! 🎉 Your EQUILA STYLE application is now production-ready.**
