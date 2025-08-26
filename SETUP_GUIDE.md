# Quick Setup Guide for Django Backend Hosting

## 1. Install Dependencies
```cmd
cd D:\backend
venv\Scripts\activate.bat
pip install -r requirements.txt
```

## 2. Update Domain Settings
- Edit `backend/settings_production.py` - replace `yourdomain.com` with your actual domain
- Edit `nginx.conf` - replace `yourdomain.com` with your actual domain

## 3. Get SSL Certificate
- Use Let's Encrypt (free) or Cloudflare (free)
- Or buy from your domain provider

## 4. Configure DNS
- Point your domain to your PC's public IP address
- Set up port forwarding (80, 443) in your router

## 5. Deploy
```cmd
deploy.bat
start_backend.bat
```

## 6. Install Nginx
- Download Nginx for Windows
- Copy `nginx.conf` to Nginx config directory
- Start Nginx

## 7. Test
- Visit https://yourdomain.com
- Check logs in `logs/` folder

## Auto-start Setup
- Use Windows Task Scheduler to run `start_backend.bat` at startup
- Or create a Windows service using NSSM

## Important Notes
- Keep PC running 24/7
- Ensure stable internet connection
- Regular backups of database
- Monitor logs for issues
