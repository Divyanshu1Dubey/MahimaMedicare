#!/bin/bash
# Vultr Server Invoice Download Configuration Script
# Run this on your Vultr server to fix invoice download issues

echo "🚀 Configuring Vultr Server for Invoice Downloads"
echo "=================================================="

# 1. Install required Python packages
echo "📦 Installing required Python packages..."
pip install reportlab pillow --upgrade

# Alternative if pip doesn't work
pip3 install reportlab pillow --upgrade

# 2. Check Python packages
echo "✅ Checking installed packages..."
python -c "import reportlab; print('ReportLab version:', reportlab.VERSION)" || echo "❌ ReportLab not installed"
python -c "import PIL; print('Pillow version:', PIL.__version__)" || echo "❌ Pillow not installed"

# 3. Create media directory and set permissions
echo "📁 Setting up media directory permissions..."
mkdir -p /home/ubuntu/MahimaMedicare/media/invoices/
mkdir -p /home/ubuntu/MahimaMedicare/media/pharmacy_invoices/
chmod -R 755 /home/ubuntu/MahimaMedicare/media/
chown -R ubuntu:ubuntu /home/ubuntu/MahimaMedicare/media/

# 4. Set up logging directory
echo "📋 Setting up logging..."
mkdir -p /home/ubuntu/MahimaMedicare/logs/
chmod -R 755 /home/ubuntu/MahimaMedicare/logs/
chown -R ubuntu:ubuntu /home/ubuntu/MahimaMedicare/logs/

# 5. Check Django settings for media configuration
echo "⚙️ Checking Django media settings..."
cd /home/ubuntu/MahimaMedicare/

# Create a simple test script
cat > test_pdf_generation.py << 'EOL'
#!/usr/bin/env python
import os
import sys
import django

# Add the project root to Python path
sys.path.append('/home/ubuntu/MahimaMedicare/')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthstack.settings')
django.setup()

def test_pdf_generation():
    """Test PDF generation on server"""
    print("🧪 Testing PDF generation...")
    
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from io import BytesIO
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 50, "Test PDF Generation - Mahima Medicare")
        p.drawString(50, height - 80, "This is a test PDF created on the server")
        
        p.save()
        buffer.seek(0)
        pdf_content = buffer.getvalue()
        
        # Save test PDF
        with open('/tmp/test_invoice.pdf', 'wb') as f:
            f.write(pdf_content)
        
        print("✅ PDF generation test successful!")
        print(f"📄 Test PDF saved: /tmp/test_invoice.pdf ({len(pdf_content)} bytes)")
        return True
        
    except Exception as e:
        print(f"❌ PDF generation test failed: {str(e)}")
        return False

def test_file_permissions():
    """Test file write permissions"""
    print("🔐 Testing file permissions...")
    
    try:
        # Test writing to media directory
        test_file = '/home/ubuntu/MahimaMedicare/media/test_file.txt'
        with open(test_file, 'w') as f:
            f.write("Test file for permissions")
        
        # Clean up
        os.remove(test_file)
        
        print("✅ File permissions test successful!")
        return True
        
    except Exception as e:
        print(f"❌ File permissions test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Running server tests...")
    pdf_ok = test_pdf_generation()
    perm_ok = test_file_permissions()
    
    if pdf_ok and perm_ok:
        print("🎉 All tests passed! Server is ready for invoice downloads.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
EOL

# Make the test script executable
chmod +x test_pdf_generation.py

# 6. Run the test
echo "🔍 Running PDF generation test..."
python test_pdf_generation.py

# 7. Restart services (adjust service names as needed)
echo "🔄 Restarting services..."
sudo systemctl restart gunicorn || echo "Gunicorn not found, skipping..."
sudo systemctl restart nginx || echo "Nginx not found, skipping..."
sudo systemctl restart apache2 || echo "Apache not found, skipping..."

# 8. Create environment check script
cat > check_server_environment.py << 'EOL'
#!/usr/bin/env python
"""Check server environment for invoice downloads"""

import os
import sys
import platform

def check_environment():
    print("🌐 Server Environment Check")
    print("=" * 40)
    
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Check packages
    packages = ['reportlab', 'PIL', 'django']
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package}: Installed")
        except ImportError:
            print(f"❌ {package}: NOT INSTALLED")
    
    # Check directories
    directories = [
        '/home/ubuntu/MahimaMedicare/media/',
        '/home/ubuntu/MahimaMedicare/logs/',
        '/tmp/'
    ]
    
    for directory in directories:
        if os.path.exists(directory) and os.access(directory, os.W_OK):
            print(f"✅ {directory}: Exists and writable")
        else:
            print(f"❌ {directory}: Missing or not writable")
    
    # Check memory
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if line.startswith('MemTotal'):
                    memory = line.split()[1]
                    memory_gb = int(memory) / 1024 / 1024
                    print(f"💾 Total Memory: {memory_gb:.1f} GB")
                    if memory_gb < 1:
                        print("⚠️ Warning: Low memory might affect PDF generation")
                    break
    except:
        print("❓ Could not check memory")

if __name__ == "__main__":
    check_environment()
EOL

chmod +x check_server_environment.py

echo ""
echo "🎯 VULTR SERVER CONFIGURATION COMPLETE!"
echo "======================================="
echo ""
echo "📋 What was done:"
echo "   ✅ Installed ReportLab and Pillow packages"
echo "   ✅ Created and configured media directories"
echo "   ✅ Set proper file permissions"
echo "   ✅ Created logging directories"
echo "   ✅ Generated test scripts"
echo "   ✅ Restarted services"
echo ""
echo "🔧 Next steps:"
echo "   1. Run: python check_server_environment.py"
echo "   2. Test invoice downloads from your web application"
echo "   3. Check logs if issues persist: tail -f logs/django.log"
echo ""
echo "💡 Troubleshooting:"
echo "   - If PDFs still don't work, check Django settings.py MEDIA_ROOT"
echo "   - Ensure your web server (nginx/apache) can serve media files"
echo "   - Check disk space: df -h"
echo "   - Monitor memory usage: free -h"
echo ""
echo "📞 Support: Check the production_invoice_views.py for enhanced error handling"