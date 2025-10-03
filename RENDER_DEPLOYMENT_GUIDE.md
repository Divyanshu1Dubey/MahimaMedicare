# 🚀 Render.com Deployment Guide for Mahima Medicare

## Quick Fix for Current Issue

The `DisallowedHost` error occurs because `mahimamedicare.onrender.com` is not in ALLOWED_HOSTS.

### Immediate Fix:
1. Go to your Render.com dashboard
2. Navigate to your web service
3. Go to "Environment" tab
4. Add/Update these environment variables:

```
ALLOWED_HOSTS=mahimamedicare.onrender.com,.onrender.com,127.0.0.1,localhost
DEBUG=False
SECRET_KEY=your-super-secret-50-character-production-key-here
```

### Step-by-Step Deployment Process:

## 1. Environment Variables Setup

In your Render.com service, set these environment variables:

```bash
# Critical Security Settings
DEBUG=False
SECRET_KEY=mahima-medicare-render-prod-2025-CHANGE-THIS-TO-50-CHARS
ALLOWED_HOSTS=mahimamedicare.onrender.com,.onrender.com,127.0.0.1,localhost

# Database (Render provides this automatically if you add PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/dbname

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Payment Gateway (Production Keys)
RAZORPAY_KEY_ID=rzp_live_your_production_key
RAZORPAY_KEY_SECRET=your_production_secret
```

## 2. Build Settings

In your Render.com service:

- **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- **Start Command**: `gunicorn healthstack.wsgi:application --bind 0.0.0.0:$PORT`

## 3. Important Files to Check

Make sure these files exist in your repository:

### `requirements.txt` should include:
```
gunicorn>=21.0.0
whitenoise>=6.5.0
dj-database-url>=2.1.0
psycopg2-binary>=2.9.7
```

### `healthstack/wsgi.py` should include:
```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthstack.settings')
application = get_wsgi_application()
```

## 4. Database Setup

1. Add a PostgreSQL database in Render.com
2. It will automatically provide `DATABASE_URL`
3. Your settings.py already handles this with `dj_database_url`

## 5. Static Files

Your `settings.py` already includes WhiteNoise configuration for static files.

## 6. Security Notes

1. **NEVER** commit your production `.env` file to Git
2. Always use environment variables in Render.com
3. Generate a secure SECRET_KEY (50+ characters, random)
4. Use production payment gateway keys
5. Set `DEBUG=False` in production

## 7. Monitoring

After deployment, monitor:
- Application logs in Render.com dashboard
- Error tracking
- Performance metrics

## 8. Common Issues & Solutions

### DisallowedHost Error:
- Add your domain to ALLOWED_HOSTS environment variable

### Static Files Not Loading:
- Ensure `python manage.py collectstatic --noinput` runs in build command
- Check WhiteNoise configuration in settings.py

### Database Connection Error:
- Verify PostgreSQL service is linked
- Check DATABASE_URL is properly set

## 9. Testing Deployment

After setting environment variables:
1. Trigger a new deployment
2. Check logs for any errors
3. Test key functionality:
   - Homepage loading
   - User registration
   - Admin panel access
   - Payment processing

## Support

If you encounter issues:
1. Check Render.com logs
2. Verify all environment variables are set
3. Ensure build and start commands are correct
4. Test locally with production-like settings