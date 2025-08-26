# Django Backend Deployment Guide

This guide will help you deploy your Django backend on your local PC for 24/7 hosting with a domain.

## Prerequisites

- Windows PC that will remain on 24/7
- Domain name (already purchased)
- Python 3.8+ installed
- Git installed

## Step 1: Install Dependencies

1. Open Command Prompt as Administrator
2. Navigate to your project directory:
   ```cmd
   cd D:\backend
   ```

3. Activate your virtual environment:
   ```cmd
   venv\Scripts\activate.bat
   ```

4. Install production dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

## Step 2: Configure Domain Settings

1. **Update `backend/settings_production.py`:**
   - Replace `yourdomain.com` with your actual domain
   - Update `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`

2. **Update `nginx.conf`:**
   - Replace `yourdomain.com` with your actual domain
   - Update SSL certificate paths

3. **Create `.env` file:**
   - Copy `env_example.txt` to `.env`
   - Update with your actual domain and credentials

## Step 3: Get SSL Certificates

You have several options for SSL certificates:

### Option A: Let's Encrypt (Free)
1. Install Certbot: https://certbot.eff.org/
2. Run: `certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com`

### Option B: Cloudflare (Free)
1. Sign up for Cloudflare
2. Add your domain
3. Update your domain's nameservers to Cloudflare's
4. Enable SSL/TLS encryption mode: "Full (strict)"

### Option C: Self-signed (Development only)
```cmd
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout private.key -out certificate.crt
```

## Step 4: Configure DNS

1. **If using Cloudflare:**
   - Add A record: `yourdomain.com` → Your PC's public IP
   - Add A record: `www.yourdomain.com` → Your PC's public IP

2. **If using other DNS provider:**
   - Add A record pointing to your PC's public IP address
   - Find your public IP at: https://whatismyipaddress.com/

## Step 5: Port Forwarding

1. Access your router's admin panel (usually 192.168.1.1)
2. Set up port forwarding:
   - Port 80 → Your PC's local IP
   - Port 443 → Your PC's local IP
   - Port 8000 → Your PC's local IP (optional, for direct access)

## Step 6: Deploy the Backend

1. Run the deployment script:
   ```cmd
   deploy.bat
   ```

2. Start the backend:
   ```cmd
   start_backend.bat
   ```

## Step 7: Install and Configure Nginx

1. Download Nginx for Windows: http://nginx.org/en/download.html
2. Extract to `C:\nginx`
3. Copy `nginx.conf` to `C:\nginx\conf\`
4. Update the paths in `nginx.conf` to match your setup
5. Start Nginx:
   ```cmd
   cd C:\nginx
   start nginx
   ```

## Step 8: Test Your Setup

1. **Test locally:**
   - http://localhost:8000 (Django directly)
   - http://localhost (Nginx proxy)

2. **Test from internet:**
   - https://yourdomain.com
   - https://www.yourdomain.com

## Step 9: Set Up Auto-Start

### Option A: Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: "At startup"
4. Action: Start a program
5. Program: `D:\backend\start_backend.bat`

### Option B: Windows Service (Advanced)
1. Install NSSM: https://nssm.cc/
2. Create service for Django backend
3. Set to auto-start

## Monitoring and Maintenance

### View Logs
- Django logs: `D:\backend\logs\django.log`
- Gunicorn logs: `D:\backend\logs\gunicorn_*.log`
- Nginx logs: `C:\nginx\logs\`

### Restart Services
```cmd
# Restart Django backend
taskkill /f /im gunicorn.exe
start_backend.bat

# Restart Nginx
cd C:\nginx
nginx -s reload
```

### Update Backend
1. Pull latest code: `git pull`
2. Run: `deploy.bat`
3. Restart backend

## Security Considerations

1. **Firewall:** Ensure Windows Firewall allows ports 80, 443, 8000
2. **Updates:** Keep Windows and Python packages updated
3. **Backups:** Regular backups of database and media files
4. **Monitoring:** Set up uptime monitoring (e.g., UptimeRobot)

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```cmd
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

2. **Permission denied:**
   - Run Command Prompt as Administrator

3. **SSL errors:**
   - Check certificate paths in nginx.conf
   - Verify certificate validity

4. **Domain not accessible:**
   - Check DNS settings
   - Verify port forwarding
   - Check firewall settings

### Check Service Status
```cmd
# Check if Django is running
netstat -ano | findstr :8000

# Check if Nginx is running
netstat -ano | findstr :80
netstat -ano | findstr :443
```

## Performance Optimization

1. **Database:** Consider migrating from SQLite to PostgreSQL
2. **Caching:** Add Redis for caching
3. **CDN:** Use Cloudflare for static assets
4. **Monitoring:** Add application performance monitoring

## Support

If you encounter issues:
1. Check the logs in `D:\backend\logs\`
2. Verify all configuration files are updated with your domain
3. Ensure all ports are properly forwarded
4. Test connectivity step by step

---

**Remember:** Keep your PC running 24/7 and ensure stable internet connection for reliable hosting.
