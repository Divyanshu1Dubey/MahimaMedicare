#!/bin/bash

echo "🚀 Starting Mahima Medicare Docker Container..."

# Start supervisor (which starts both gunicorn and nginx)
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf