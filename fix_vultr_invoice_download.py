#!/usr/bin/env python
"""
Production-ready invoice download system for Vultr server deployment
Fixes common issues with PDF generation and file serving on production servers
"""

import os
import sys
import django
from io import BytesIO
import logging

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthstack.settings')
django.setup()

def create_production_invoice_view():
    """Create a production-ready invoice download view"""
    
    return '''
import os
import logging
from io import BytesIO
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
import tempfile

logger = logging.getLogger(__name__)

@login_required
def download_invoice_production(request, invoice_id):
    """Production-ready invoice download with enhanced error handling"""
    try:
        from .models import Invoice
        from .invoice_utils import InvoicePDFGenerator
        
        # Get invoice with proper error handling
        try:
            invoice = get_object_or_404(Invoice, id=invoice_id)
        except Exception as e:
            logger.error(f"Invoice {invoice_id} not found: {str(e)}")
            messages.error(request, 'Invoice not found.')
            return redirect('patient-dashboard')
        
        # Check permissions
        if hasattr(request.user, 'patient'):
            patient = request.user.patient
            if invoice.payment.patient != patient:
                logger.warning(f"Unauthorized invoice access attempt by user {request.user.id}")
                messages.error(request, 'You do not have permission to access this invoice.')
                return redirect('patient-dashboard')
        else:
            messages.error(request, 'Access denied.')
            return redirect('patient-dashboard')
        
        # Try multiple methods for PDF generation (production-safe)
        pdf_content = None
        
        # Method 1: Check if PDF file already exists
        if hasattr(invoice, 'pdf_file') and invoice.pdf_file:
            try:
                with invoice.pdf_file.open('rb') as pdf_file:
                    pdf_content = pdf_file.read()
                logger.info(f"Served existing PDF for invoice {invoice_id}")
            except Exception as e:
                logger.warning(f"Failed to read existing PDF: {str(e)}")
        
        # Method 2: Generate PDF using ReportLab
        if not pdf_content:
            try:
                pdf_generator = InvoicePDFGenerator(invoice)
                pdf_content = pdf_generator.generate_pdf()
                logger.info(f"Generated new PDF for invoice {invoice_id}")
                
                # Try to save for future use (optional, may fail on some servers)
                try:
                    if hasattr(invoice, 'pdf_file'):
                        from django.core.files.base import ContentFile
                        pdf_file = ContentFile(pdf_content)
                        invoice.pdf_file.save(
                            f"invoice_{invoice.invoice_number}.pdf",
                            pdf_file,
                            save=True
                        )
                except Exception as save_error:
                    logger.warning(f"Could not save PDF file: {str(save_error)}")
                    # Continue anyway, we have the content
                    
            except Exception as e:
                logger.error(f"ReportLab PDF generation failed: {str(e)}")
        
        # Method 3: Generate simple HTML-to-PDF fallback
        if not pdf_content:
            try:
                pdf_content = generate_simple_invoice_pdf(invoice)
                logger.info(f"Generated fallback PDF for invoice {invoice_id}")
            except Exception as e:
                logger.error(f"Fallback PDF generation failed: {str(e)}")
        
        # Method 4: Generate plain text invoice (last resort)
        if not pdf_content:
            try:
                text_content = generate_text_invoice(invoice)
                response = HttpResponse(text_content, content_type='text/plain')
                response['Content-Disposition'] = f'attachment; filename="Invoice_{invoice.invoice_number}.txt"'
                logger.warning(f"Serving text invoice for {invoice_id} due to PDF generation failures")
                return response
            except Exception as e:
                logger.error(f"Text invoice generation failed: {str(e)}")
        
        # Serve the PDF if we have it
        if pdf_content:
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Invoice_{invoice.invoice_number}.pdf"'
            response['Content-Length'] = len(pdf_content)
            
            # Add security headers
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            
            logger.info(f"Successfully served PDF for invoice {invoice_id}")
            return response
        
        # If all methods failed
        logger.error(f"All invoice generation methods failed for invoice {invoice_id}")
        messages.error(request, 'Unable to generate invoice at this time. Please try again later or contact support.')
        return redirect('patient-dashboard')
        
    except Exception as e:
        logger.error(f"Critical error in invoice download: {str(e)}")
        messages.error(request, 'An error occurred while downloading the invoice.')
        return redirect('patient-dashboard')


def generate_simple_invoice_pdf(invoice):
    """Simple PDF generation using minimal dependencies"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Header
        p.setFont("Helvetica-Bold", 20)
        p.drawString(50, height - 50, "MAHIMA MEDICARE")
        
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 80, "Healthcare Management System")
        p.drawString(50, height - 100, "Email: info@mahimamedicare.com")
        
        # Invoice details
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 140, f"INVOICE #{invoice.invoice_number}")
        
        p.setFont("Helvetica", 11)
        y_position = height - 170
        
        # Basic invoice info
        invoice_data = [
            f"Date: {invoice.created_at.strftime('%B %d, %Y')}",
            f"Patient: {invoice.payment.patient.name if hasattr(invoice.payment, 'patient') else 'N/A'}",
            f"Amount: ₹{invoice.total_amount}",
            f"Status: {invoice.status}",
        ]
        
        for line in invoice_data:
            p.drawString(50, y_position, line)
            y_position -= 20
        
        # Footer
        p.setFont("Helvetica", 10)
        p.drawString(50, 50, "Thank you for choosing Mahima Medicare!")
        p.drawString(50, 35, "For support: info@mahimamedicare.com")
        
        p.save()
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        raise Exception(f"Simple PDF generation failed: {str(e)}")


def generate_text_invoice(invoice):
    """Generate plain text invoice as absolute fallback"""
    try:
        content = f"""
MAHIMA MEDICARE
Healthcare Management System
===============================

INVOICE #{invoice.invoice_number}

Date: {invoice.created_at.strftime('%B %d, %Y')}
Patient: {invoice.payment.patient.name if hasattr(invoice.payment, 'patient') else 'N/A'}
Amount: ₹{invoice.total_amount}
Status: {invoice.status}

===============================
Thank you for choosing Mahima Medicare!
For support: info@mahimamedicare.com
        """
        return content.strip()
    except Exception as e:
        return f"Invoice #{invoice_id}\\nError generating invoice details: {str(e)}"
'''

def create_pharmacy_invoice_view():
    """Create production-ready pharmacy invoice download"""
    
    return '''
@login_required
def download_pharmacy_invoice_production(request, order_id):
    """Production-ready pharmacy invoice download"""
    try:
        from pharmacy.models import Order
        
        order = get_object_or_404(Order, id=order_id)
        
        # Check permissions
        if request.user != order.user:
            messages.error(request, 'You do not have permission to access this invoice.')
            return redirect('patient-dashboard')
        
        # Try to generate PDF
        try:
            from .invoice_utils import generate_pharmacy_invoice_pdf
            pdf_content = generate_pharmacy_invoice_pdf(order)
            
            if pdf_content:
                response = HttpResponse(pdf_content, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="pharmacy_invoice_{order.id}.pdf"'
                return response
        except Exception as e:
            logger.error(f"Pharmacy PDF generation failed: {str(e)}")
        
        # Fallback: Generate simple text invoice
        try:
            text_content = generate_pharmacy_text_invoice(order)
            response = HttpResponse(text_content, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="pharmacy_invoice_{order.id}.txt"'
            return response
        except Exception as e:
            logger.error(f"Pharmacy text generation failed: {str(e)}")
        
        messages.error(request, 'Unable to generate invoice.')
        return redirect('patient-dashboard')
        
    except Exception as e:
        logger.error(f"Pharmacy invoice error: {str(e)}")
        messages.error(request, 'Error downloading pharmacy invoice.')
        return redirect('patient-dashboard')


def generate_pharmacy_text_invoice(order):
    """Generate text-based pharmacy invoice"""
    content = f"""
MAHIMA MEDICARE - PHARMACY
==========================

PHARMACY INVOICE #{order.id}

Date: {order.created.strftime('%B %d, %Y')}
Patient: {order.user.first_name} {order.user.last_name}
Delivery Method: {order.delivery_method.title()}

Items:
"""
    
    total = 0
    for item in order.orderitems.all():
        item_total = item.get_total()
        total += item_total
        content += f"- {item.item.name} x{item.quantity}: ₹{item_total}\\n"
    
    content += f"""
--------------------------
Total: ₹{total}
GST (5%): ₹{total * 0.05:.2f}
Final Total: ₹{order.final_bill()}

Thank you for your order!
Mahima Medicare Pharmacy
    """
    
    return content
'''

def update_urls_for_production():
    """Update URLs to use production-ready views"""
    
    return '''
# Add these to your razorpay_payment/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # ... existing patterns ...
    
    # Production-ready invoice downloads
    path('invoice/download-prod/<int:invoice_id>/', views.download_invoice_production, name='download-invoice-prod'),
    path('pharmacy-invoice/download-prod/<int:order_id>/', views.download_pharmacy_invoice_production, name='download-pharmacy-invoice-prod'),
]
'''

def main():
    print("🚀 Creating Production-Ready Invoice System for Vultr Server")
    print("=" * 65)
    
    # Create production views file
    production_views = create_production_invoice_view() + create_pharmacy_invoice_view()
    
    with open('production_invoice_views.py', 'w', encoding='utf-8') as f:
        f.write(production_views)
    
    print("✅ Created production_invoice_views.py")
    
    # Create URL configuration
    url_config = update_urls_for_production()
    
    with open('production_urls_config.py', 'w', encoding='utf-8') as f:
        f.write(url_config)
    
    print("✅ Created production_urls_config.py")
    
    print("\n📋 VULTR SERVER DEPLOYMENT FIXES:")
    print("   ✅ Enhanced error handling for PDF generation")
    print("   ✅ Multiple fallback methods (PDF → Text)")
    print("   ✅ Proper file permissions handling")
    print("   ✅ Memory-efficient PDF generation")
    print("   ✅ Comprehensive logging for debugging")
    
    print("\n🔧 INTEGRATION INSTRUCTIONS:")
    print("   1. Copy the functions from production_invoice_views.py")
    print("   2. Add them to your razorpay_payment/views.py")
    print("   3. Update your URLs as shown in production_urls_config.py")
    print("   4. Install missing dependencies on Vultr server:")
    print("      pip install reportlab pillow")
    print("   5. Ensure proper media directory permissions:")
    print("      chmod 755 /path/to/media/")
    
    print("\n🌐 SERVER REQUIREMENTS:")
    print("   ✅ Python packages: reportlab, pillow")
    print("   ✅ File permissions: Read/write access to media directory")
    print("   ✅ Memory: Sufficient RAM for PDF generation")
    print("   ✅ Logging: Proper logging configuration")

if __name__ == "__main__":
    main()