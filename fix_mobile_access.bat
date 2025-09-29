@echo off
echo Fixing mobile access and preparing for SSL...

ssh root@139.84.155.25 "
# Update Django settings for better mobile compatibility
cd /var/www/mahima-medicare

# Update ALLOWED_HOSTS to include all possible variations
sed -i 's/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=mahimamedicare.co.in,www.mahimamedicare.co.in,139.84.155.25,127.0.0.1,localhost,*/' .env

# Verify the change
echo 'Current ALLOWED_HOSTS:'
cat .env | grep ALLOWED_HOSTS

# Restart Gunicorn to apply changes
killall gunicorn 2>/dev/null || true
pkill -f gunicorn 2>/dev/null || true
sleep 3

# Start Gunicorn fresh
source venv/bin/activate
gunicorn --config gunicorn.conf.py healthstack.wsgi:application &

echo 'Services restarted. Testing connectivity...'
sleep 5

# Test local connectivity
curl -I http://127.0.0.1:8000/

echo 'Update complete. Website should now work on mobile devices.'
echo 'SSL will be ready when Namecheap status changes to ACTIVE.'
"

pause