from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.conf import settings
from django.core.files.base import ContentFile
from io import BytesIO
import os
from datetime import datetime
from decimal import Decimal
from .models import Invoice, InvoiceItem


class InvoicePDFGenerator:
    def __init__(self, invoice):
        self.invoice = invoice
        self.buffer = BytesIO()
        self.pagesize = A4
        self.width, self.height = self.pagesize
        
    def generate_pdf(self):
        """Generate PDF invoice and return the buffer (production-safe)"""
        try:
            doc = SimpleDocTemplate(
                self.buffer,
                pagesize=self.pagesize,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build the PDF content
            story = []
            
            # Add company header (with error handling)
            try:
                story.extend(self._create_header())
                story.append(Spacer(1, 20))
            except Exception as e:
                print(f"Header creation error: {e}")
                # Add fallback header
                story.append(Paragraph("<b>MAHIMA MEDICARE</b>", getSampleStyleSheet()['Title']))
                story.append(Spacer(1, 20))
            
            # Add invoice details
            try:
                story.extend(self._create_invoice_details())
                story.append(Spacer(1, 10))
            except Exception as e:
                print(f"Invoice details error: {e}")
                story.append(Paragraph(f"Invoice #{self.invoice.invoice_number}", getSampleStyleSheet()['Heading2']))
            
            # Add invoice items table
            try:
                story.extend(self._create_items_table())
                story.append(Spacer(1, 20))
            except Exception as e:
                print(f"Items table error: {e}")
                story.append(Paragraph(f"Total: ₹{self.invoice.total_amount}", getSampleStyleSheet()['Normal']))
            
            # Add totals
            try:
                story.extend(self._create_totals())
                story.append(Spacer(1, 20))
            except Exception as e:
                print(f"Totals section error: {e}")
            
            # Add footer
            try:
                story.extend(self._create_footer())
            except Exception as e:
                print(f"Footer error: {e}")
            
            # Build PDF
            doc.build(story)
            
            # Get PDF content
            pdf_content = self.buffer.getvalue()
            self.buffer.close()
            
            return pdf_content
            
        except Exception as e:
            print(f"PDF generation error: {e}")
            # Clean up buffer
            try:
                self.buffer.close()
            except:
                pass
            raise Exception(f"Invoice PDF generation failed: {str(e)}")
    
    def _create_header(self):
        """Create professional header with Mahima Medicare branding"""
        styles = getSampleStyleSheet()
        elements = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.Color(0.2, 0.4, 0.8)  # Professional blue
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            spaceAfter=15,
            alignment=TA_CENTER,
            textColor=colors.Color(0.3, 0.3, 0.3)
        )
        
        # Try to add Mahima Medicare logo (safe for production)
        logo = None
        try:
            # Try multiple logo paths (production-safe)
            logo_paths = []
            
            # Add STATIC_ROOT path if available
            if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
                logo_paths.append(os.path.join(settings.STATIC_ROOT, 'HealthStack-System', 'images', 'Normal', 'logo.png'))
            
            # Add STATICFILES_DIRS paths if available
            if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
                for static_dir in settings.STATICFILES_DIRS:
                    logo_paths.append(os.path.join(static_dir, 'HealthStack-System', 'images', 'Normal', 'logo.png'))
            
            # Add BASE_DIR fallback
            logo_paths.extend([
                os.path.join(settings.BASE_DIR, 'static', 'HealthStack-System', 'images', 'Normal', 'logo.png'),
                os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png'),
            ])
            
            for logo_path in logo_paths:
                try:
                    if os.path.exists(logo_path) and os.path.isfile(logo_path):
                        logo = Image(logo_path, width=2*inch, height=1.4*inch)
                        break
                except (IOError, OSError) as img_error:
                    print(f"Could not load logo from {logo_path}: {img_error}")
                    continue
                    
        except Exception as e:
            print(f"Logo loading error (continuing without logo): {e}")
            logo = None
        
        # Header with logo and company info
        if logo:
            # Create header table with logo and company details
            header_data = [
                [
                    logo,
                    Paragraph('''
                    <font size="18" color="#2E5CBA"><b>MAHIMA MEDICARE</b></font><br/>
                    <font size="10" color="#666666">ଆପଣଙ୍କ ସ୍ବାସ୍ଥ୍ୟ ର ସାଥୀ (Your Health Partner)</font><br/>
                    <font size="9" color="#333333">
                    Barkoliya Bajar, Orti, Cuttack, 754209<br/>
                    Mobile: +91 8763814619 | Email: mahimamedicare01@gmail.com<br/>
                    Web: mahimamedicare.co.in<br/>
                    <b>GSTIN: 21AXRPN9340C1ZH</b>
                    </font>
                    ''', ParagraphStyle('CompanyInfo', parent=styles['Normal'], alignment=TA_LEFT))
                ]
            ]
            
            header_table = Table(header_data, colWidths=[2.5*inch, 4.5*inch])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            elements.append(header_table)
        else:
            # Fallback header without logo
            elements.append(Paragraph("MAHIMA MEDICARE", title_style))
            elements.append(Paragraph("Healthcare Services & Medical Solutions", subtitle_style))
            elements.append(Paragraph('''
            Address: Near Mani Residency Complex, Indore, MP<br/>
            Phone: +91-98765-43210 | Email: info@mahimamedicare.co.in<br/>
            <b>GSTIN: 23AAAAA0000A1Z5 | PAN: AAAAA0000A</b>
            ''', ParagraphStyle('CompanyAddress', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9)))
        
        elements.append(Spacer(1, 10))
        
        # Invoice title with border
        invoice_title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading2'],
            fontSize=16,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            borderWidth=1,
            borderColor=colors.darkblue,
            borderPadding=10,
            spaceAfter=15
        )
        
        payment_type = self.invoice.payment.payment_type if self.invoice.payment else 'service'
        if payment_type == 'pharmacy':
            title_text = "MEDICINE PURCHASE INVOICE"
        elif payment_type == 'appointment':
            title_text = "DOCTOR CONSULTATION INVOICE" 
        elif payment_type == 'test':
            title_text = "LABORATORY TEST INVOICE"
        else:
            title_text = "SERVICE INVOICE"
            
        elements.append(Paragraph(f"<b>{title_text}</b>", invoice_title_style))
        
        return elements

    
    def _create_invoice_details(self):
        """Create professional invoice details section"""
        styles = getSampleStyleSheet()
        elements = []
        
        # Custom header style
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.Color(0.2, 0.4, 0.8)
        )
        
        # Invoice details section
        elements.append(Paragraph("Invoice Details", header_style))
        
        invoice_details_data = [
            ['Invoice Number:', f'INV-{self.invoice.invoice_number}'],
            ['Invoice Date:', self.invoice.created_at.strftime('%B %d, %Y')],
            ['Payment ID:', self.invoice.payment.razorpay_payment_id if self.invoice.payment and self.invoice.payment.razorpay_payment_id else 'N/A'],
            ['Payment Status:', 'Paid'],
        ]
        
        # Add service-specific details
        if self.invoice.payment:
            if self.invoice.payment.payment_type == 'appointment' and self.invoice.payment.appointment:
                invoice_details_data.append(['Doctor:', self.invoice.payment.appointment.doctor.name])
                invoice_details_data.append(['Appointment Date:', self.invoice.payment.appointment.date.strftime('%B %d, %Y')])
            elif self.invoice.payment.payment_type == 'pharmacy' and self.invoice.payment.order:
                invoice_details_data.append(['Order Status:', self.invoice.payment.order.get_order_status_display()])
                invoice_details_data.append(['Total Items:', str(self.invoice.payment.order.orderitems.count())])
        
        invoice_details_table = Table(invoice_details_data, colWidths=[2.5*inch, 3.5*inch])
        invoice_details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))
        elements.append(invoice_details_table)
        elements.append(Spacer(1, 15))
        
        # Customer details section
        elements.append(Paragraph("Customer Information", header_style))
        
        customer_data = [
            ['Name:', self.invoice.customer_name],
            ['Phone:', self.invoice.customer_phone or 'N/A'],
            ['Email:', self.invoice.customer_email or 'N/A'],
        ]
        
        if self.invoice.customer_address:
            customer_data.append(['Address:', self.invoice.customer_address])
        
        customer_table = Table(customer_data, colWidths=[2.5*inch, 3.5*inch])
        customer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))
        elements.append(customer_table)
        
        return elements
    
    def _create_customer_details(self):
        """Create customer details section"""
        styles = getSampleStyleSheet()
        
        # Bill to section
        bill_to_style = ParagraphStyle(
            'BillTo',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#2E8B57'),
            spaceAfter=10
        )
        
        customer_style = ParagraphStyle(
            'Customer',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=5
        )
        
        details = []
        details.append(Paragraph("BILL TO:", bill_to_style))
        
        customer_info = f"""
        <b>{self.invoice.customer_name}</b><br/>
        Email: {self.invoice.customer_email}<br/>
        Phone: {self.invoice.customer_phone}
        """
        
        if self.invoice.customer_address:
            customer_info += f"<br/>Address: {self.invoice.customer_address}"
        
        details.append(Paragraph(customer_info, customer_style))
        
        return details
    
    def _create_items_table(self):
        """Create professional service items table"""
        styles = getSampleStyleSheet()
        elements = []
        
        # Items header
        header_style = ParagraphStyle(
            'ItemsHeader',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.Color(0.2, 0.4, 0.8)
        )
        
        payment_type = self.invoice.payment.payment_type if self.invoice.payment else 'service'
        
        if payment_type == 'pharmacy':
            elements.append(Paragraph("Medicine Details", header_style))
        elif payment_type == 'appointment':
            elements.append(Paragraph("Consultation Details", header_style))
        elif payment_type == 'test':
            elements.append(Paragraph("Laboratory Test Details", header_style))
        else:
            elements.append(Paragraph("Service Details", header_style))
        
        # Table headers - simpler format
        headers = ['Description', 'Quantity', 'Unit Price', 'Total Price']
        data = [headers]
        
        # Add items
        for item in self.invoice.items.all():
            row = [
                item.description,
                str(item.quantity),
                f'₹{item.unit_price:.2f}',
                f'₹{item.total_price:.2f}'
            ]
            data.append(row)
        
        # Create table
        items_table = Table(data, colWidths=[3.5*inch, 1*inch, 1.5*inch, 1.5*inch])
        items_table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.4, 0.8)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Description left-aligned
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)])
        ]))
        
        elements.append(items_table)
        return elements
    
    def _create_totals(self):
        """Create professional billing summary section"""
        styles = getSampleStyleSheet()
        elements = []
        
        # Billing summary header
        header_style = ParagraphStyle(
            'BillingHeader',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.Color(0.2, 0.4, 0.8)
        )
        
        elements.append(Paragraph("Billing Summary", header_style))
        
        # Calculate totals
        total_amount = float(self.invoice.total_amount)
        
        # Determine GST rate based on payment type
        payment_type = self.invoice.payment.payment_type if self.invoice.payment else 'service'
        if payment_type == 'pharmacy':
            gst_rate = 5  # 5% GST for medicines
        else:
            gst_rate = 18  # 18% GST for services
        
        # Calculate amounts
        base_amount = total_amount / (1 + gst_rate/100)
        gst_amount = total_amount - base_amount
        
        # Create billing summary table
        billing_data = [
            ['Subtotal (Before GST):', f'₹{base_amount:.2f}'],
            [f'GST ({gst_rate}%):', f'₹{gst_amount:.2f}'],
        ]
        
        # Add delivery charges for pharmacy orders
        if payment_type == 'pharmacy' and self.invoice.payment and self.invoice.payment.order:
            delivery_fee = 40 if hasattr(self.invoice.payment.order, 'delivery_method') and self.invoice.payment.order.delivery_method == 'delivery' else 0
            if delivery_fee > 0:
                billing_data.insert(-1, ['Delivery Charges:', f'₹{delivery_fee:.2f}'])
        
        billing_data.append(['Total Amount:', f'₹{total_amount:.2f}'])
        
        billing_table = Table(billing_data, colWidths=[4*inch, 2*inch])
        billing_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.Color(0.2, 0.4, 0.8)),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.Color(0.2, 0.4, 0.8)),
        ]))
        
        elements.append(billing_table)
        return elements
    
    def _create_footer(self):
        """Create professional invoice footer"""
        styles = getSampleStyleSheet()
        elements = []
        
        # Terms and conditions
        elements.append(Spacer(1, 15))
        
        terms_style = ParagraphStyle(
            'Terms',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_LEFT,
            textColor=colors.Color(0.3, 0.3, 0.3)
        )
        
        terms_text = """
        <b>Terms & Conditions:</b><br/>
        • Payment is subject to realization of cheque/DD.<br/>
        • All disputes are subject to Indore jurisdiction.<br/>
        • Goods once sold will not be taken back.<br/>
        • E&OE (Errors and Omissions Excepted)
        """
        
        elements.append(Paragraph(terms_text, terms_style))
        elements.append(Spacer(1, 20))
        
        # Thank you message
        thank_you_style = ParagraphStyle(
            'ThankYou',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            textColor=colors.Color(0.2, 0.4, 0.8),
            spaceAfter=10
        )
        
        elements.append(Paragraph("Thank you for choosing Mahima Medicare for your healthcare needs!", thank_you_style))
        
        # Company signature section
        signature_data = [
            ['Customer Signature', '', 'Authorized Signatory\nMAHIMA MEDICARE']
        ]
        
        signature_table = Table(signature_data, colWidths=[2.5*inch, 1*inch, 2.5*inch])
        signature_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
        ]))
        
        elements.append(signature_table)
        elements.append(Spacer(1, 10))
        
        # Computer generated message
        computer_msg_style = ParagraphStyle(
            'ComputerMsg',
            parent=styles['Normal'],
            fontSize=7,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
        
        elements.append(Paragraph(
            "This is a computer generated invoice and does not require physical signature.",
            computer_msg_style
        ))
        
        return elements


def generate_invoice_for_payment(payment):
    """
    Generate invoice for a successful payment
    """
    try:
        # Check if invoice already exists - prevent duplicates (multiple checks)
        try:
            if hasattr(payment, 'invoice') and payment.invoice:
                print(f"Found existing invoice via hasattr: {payment.invoice.invoice_number}")
                return payment.invoice
        except Invoice.DoesNotExist:
            # Invoice relation exists but invoice was deleted, continue to create new one
            pass
        
        # Double check: Look for any existing invoice for this payment
        existing_invoice = Invoice.objects.filter(payment=payment).first()
        if existing_invoice:
            print(f"Found existing invoice via filter: {existing_invoice.invoice_number}")
            return existing_invoice
            
        # Triple check: Check by payment ID directly to be extra sure
        existing_by_id = Invoice.objects.filter(payment_id=payment.payment_id).first()
        if existing_by_id:
            print(f"Found existing invoice via payment_id: {existing_by_id.invoice_number}")
            return existing_by_id
            
        print(f"Creating new invoice for payment {payment.payment_id}")
        
        # Calculate amounts
        subtotal = payment.amount
        tax_amount = Decimal('0.00')  # You can calculate tax based on your business rules
        discount_amount = Decimal('0.00')
        total_amount = subtotal + tax_amount - discount_amount
        
        # Create invoice
        invoice = Invoice.objects.create(
            payment=payment,
            customer_name=payment.name or 'Customer',
            customer_email=payment.email or '',
            customer_phone=payment.phone or '',
            customer_address=payment.address or '',
            subtotal=subtotal,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            total_amount=total_amount,
            status='paid'
        )
        
        # Create invoice items based on payment type
        if payment.payment_type == 'appointment' and payment.appointment:
            # Determine if it's consultation or report based on appointment type
            if payment.appointment.appointment_type == 'checkup':
                description = f"Medical Consultation - Dr. {payment.appointment.doctor.name}"
                service_type = "Medical Consultation"
            else:  # report type
                description = f"Medical Report Review - Dr. {payment.appointment.doctor.name}"
                service_type = "Medical Report"
            
            InvoiceItem.objects.create(
                invoice=invoice,
                description=description,
                quantity=1,
                unit_price=payment.amount,
                item_type='appointment',
                item_id=payment.appointment.id
            )
        
        elif payment.payment_type == 'pharmacy' and payment.order:
            # For pharmacy orders, create items for each medicine
            for order_item in payment.order.orderitems.all():
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=f"{order_item.item.name} - {order_item.item.description}",
                    quantity=order_item.quantity,
                    unit_price=order_item.item.price,
                    item_type='medicine',
                    item_id=order_item.item.serial_number
                )
        
        elif payment.payment_type == 'test' and payment.test_order:
            # Create description for test order
            description = f"Laboratory Test Order #{payment.test_order.id}"
            
            # Check if prescription exists (safely)
            if hasattr(payment.test_order, 'prescription') and payment.test_order.prescription:
                description += f" (Prescription #{payment.test_order.prescription.prescription_id})"
            elif payment.prescription:
                description += f" (Prescription #{payment.prescription.prescription_id})"
            
            # Get test details from order items if available
            if hasattr(payment.test_order, 'orderitems'):
                test_items = payment.test_order.orderitems.all()
                if test_items.exists():
                    # Create separate items for each test
                    for test_item in test_items:
                        # Get test name from the testCart item
                        test_name = test_item.name or f'Test Item #{test_item.id}'
                        if hasattr(test_item, 'item') and test_item.item:
                            # Get test name from Prescription_test
                            test_name = getattr(test_item.item, 'test_name', test_name)
                        
                        # Get test price from testCart total property
                        test_price = getattr(test_item, 'total', payment.amount / len(test_items))
                        
                        InvoiceItem.objects.create(
                            invoice=invoice,
                            description=f"Lab Test: {test_name}",
                            quantity=1,
                            unit_price=test_price,
                            item_type='test',
                            item_id=test_item.id
                        )
                else:
                    # Fallback: single test item
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        description="Lab Test",
                        quantity=1,
                        unit_price=payment.amount,
                        item_type='test'
                    )
        
        # Generate PDF (outside all conditional blocks)
        pdf_generator = InvoicePDFGenerator(invoice)
        pdf_content = pdf_generator.generate_pdf()
        
        # Save PDF to invoice
        from django.core.files.base import ContentFile
        pdf_file = ContentFile(pdf_content)
        invoice.pdf_file.save(
            f"invoice_{invoice.invoice_number}.pdf",
            pdf_file,
            save=True
        )
        
        return invoice
        
    except Exception as e:
        print(f"Error generating invoice: {str(e)}")
        return None


def generate_pharmacy_invoice_pdf(order):
    """
    Generate PDF invoice for pharmacy order
    """
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
        from io import BytesIO
        from datetime import datetime
        
        # Create a BytesIO buffer to receive PDF data
        buffer = BytesIO()
        
        # Create the PDF object, using the buffer as its "file"
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles - Professional Design
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.Color(0.2, 0.4, 0.8)  # Professional blue
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            spaceAfter=15,
            alignment=TA_CENTER,
            textColor=colors.Color(0.3, 0.3, 0.3)
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.Color(0.2, 0.4, 0.8)
        )
        
        # Try to add Mahima Medicare logo (production-safe)
        logo = None
        try:
            logo_paths = []
            
            if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
                logo_paths.append(os.path.join(settings.STATIC_ROOT, 'HealthStack-System', 'images', 'Normal', 'logo.png'))
            
            if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
                for static_dir in settings.STATICFILES_DIRS:
                    logo_paths.append(os.path.join(static_dir, 'HealthStack-System', 'images', 'Normal', 'logo.png'))
            
            logo_paths.extend([
                os.path.join(settings.BASE_DIR, 'static', 'HealthStack-System', 'images', 'Normal', 'logo.png'),
                os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png'),
            ])
            
            for logo_path in logo_paths:
                try:
                    if os.path.exists(logo_path) and os.path.isfile(logo_path):
                        logo = Image(logo_path, width=2*inch, height=1.4*inch)
                        break
                except (IOError, OSError):
                    continue
        except Exception as e:
            print(f"Logo loading error (continuing without logo): {e}")
            logo = None
        
        # Header with logo and company info
        if logo:
            header_data = [
                [
                    logo,
                    Paragraph('''
                    <font size="18" color="#2E5CBA"><b>MAHIMA MEDICARE</b></font><br/>
                    <font size="10" color="#666666">ଆପଣଙ୍କ ସ୍ବାସ୍ଥ୍ୟ ର ସାଥୀ (Your Health Partner)</font><br/>
                    <font size="9" color="#333333">
                    Barkoliya Bajar, Orti, Cuttack, 754209<br/>
                    Mobile: +91 8763814619 | Email: mahimamedicare01@gmail.com<br/>
                    Web: mahimamedicare.co.in<br/>
                    <b>GSTIN: 21AXRPN9340C1ZH</b>
                    </font>
                    ''', ParagraphStyle('CompanyInfo', parent=styles['Normal'], alignment=TA_LEFT))
                ]
            ]
            
            header_table = Table(header_data, colWidths=[2.5*inch, 4.5*inch])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            elements.append(header_table)
        else:
            # Fallback header without logo
            elements.append(Paragraph("MAHIMA MEDICARE", title_style))
            elements.append(Paragraph("ଆପଣଙ୍କ ସ୍ବାସ୍ଥ୍ୟ ର ସାଥୀ (Your Health Partner)", subtitle_style))
            elements.append(Paragraph('''
            Barkoliya Bajar, Orti, Cuttack, 754209<br/>
            Mobile: +91 8763814619 | Email: mahimamedicare01@gmail.com<br/>
            Web: mahimamedicare.co.in<br/>
            <b>GSTIN: 21AXRPN9340C1ZH</b>
            ''', ParagraphStyle('CompanyAddress', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9)))
        
        elements.append(Spacer(1, 10))
        
        # Invoice title with professional styling
        invoice_title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading2'],
            fontSize=16,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            spaceAfter=15
        )
        
        elements.append(Paragraph("<b>MEDICINE PURCHASE INVOICE</b>", invoice_title_style))
        elements.append(Spacer(1, 15))
        
        # Invoice details section
        elements.append(Paragraph("Invoice Details", header_style))
        
        # Get payment information for transaction details
        payment_info = order.razorpaypayment_set.first() if hasattr(order, 'razorpaypayment_set') else None
        
        invoice_details_data = [
            ['Invoice Number:', f'INV-{order.id:06d}'],
            ['Order Date:', order.created.strftime('%B %d, %Y')],
            ['Payment ID:', payment_info.razorpay_payment_id if payment_info and payment_info.razorpay_payment_id else 'N/A'],
            ['Payment Status:', 'Paid'],
            ['Order Status:', order.get_order_status_display()],
            ['Total Items:', str(order.orderitems.count())],
        ]
        
        invoice_details_table = Table(invoice_details_data, colWidths=[2.5*inch, 3.5*inch])
        invoice_details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))
        elements.append(invoice_details_table)
        elements.append(Spacer(1, 15))
        
        # Customer details section
        elements.append(Paragraph("Customer Information", header_style))
        
        customer_data = [
            ['Name:', order.user.patient.name if hasattr(order.user, 'patient') else order.user.username],
            ['Phone:', order.delivery_phone or 'N/A'],
            ['Email:', order.user.email or 'N/A'],
            ['Delivery Method:', order.get_delivery_method_display()],
        ]
        
        if order.delivery_method == 'delivery' and order.delivery_address:
            customer_data.append(['Delivery Address:', order.delivery_address])
        
        customer_table = Table(customer_data, colWidths=[2.5*inch, 3.5*inch])
        customer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))
        elements.append(customer_table)
        elements.append(Spacer(1, 15))
        
        # Medicine details section
        elements.append(Paragraph("Medicine Details", header_style))
        
        # Table headers with professional styling
        medicine_data = [['Medicine Name', 'Quantity', 'Unit Price', 'Total Price']]
        
        # Add medicine items
        for item in order.orderitems.all():
            medicine_data.append([
                item.item.name,
                str(item.quantity),
                f'₹{item.item.price:.2f}',
                f'₹{item.get_total():.2f}'
            ])
        
        medicine_table = Table(medicine_data, colWidths=[3.5*inch, 1*inch, 1.5*inch, 1.5*inch])
        medicine_table.setStyle(TableStyle([
            # Header styling - professional blue
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.4, 0.8)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Medicine name left-aligned
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)])
        ]))
        elements.append(medicine_table)
        elements.append(Spacer(1, 15))
        
        # Billing summary section
        elements.append(Paragraph("Billing Summary", header_style))
        
        subtotal = order.get_totals()
        gst_amount = order.get_gst_amount()
        delivery_fee = 40 if order.delivery_method == 'delivery' else 0
        total_amount = order.final_bill()
        
        billing_data = [
            ['Subtotal (Before GST):', f'₹{subtotal:.2f}'],
            ['GST (5%):', f'₹{gst_amount:.2f}'],
            ['Delivery Charges:', f'₹{delivery_fee:.2f}' if delivery_fee > 0 else 'FREE'],
            ['Total Amount:', f'₹{total_amount:.2f}']
        ]
        
        billing_table = Table(billing_data, colWidths=[4*inch, 2*inch])
        billing_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.Color(0.2, 0.4, 0.8)),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.Color(0.2, 0.4, 0.8)),
        ]))
        elements.append(billing_table)
        elements.append(Spacer(1, 20))
        
        # Professional footer
        terms_style = ParagraphStyle(
            'Terms',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_LEFT,
            textColor=colors.Color(0.3, 0.3, 0.3)
        )
        
        terms_text = """
        <b>Terms & Conditions:</b><br/>
        • Payment is subject to realization of cheque/DD.<br/>
        • All disputes are subject to Indore jurisdiction.<br/>
        • Medicines once sold will not be taken back unless defective.<br/>
        • E&OE (Errors and Omissions Excepted)
        """
        
        elements.append(Paragraph(terms_text, terms_style))
        elements.append(Spacer(1, 15))
        
        # Thank you message
        thank_you_style = ParagraphStyle(
            'ThankYou',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            textColor=colors.Color(0.2, 0.4, 0.8),
        )
        
        elements.append(Paragraph("Thank you for choosing Mahima Medicare for your healthcare needs!", thank_you_style))
        elements.append(Spacer(1, 15))
        
        # Signature section
        signature_data = [
            ['Customer Signature', '', 'Authorized Signatory\nMAHIMA MEDICARE']
        ]
        
        signature_table = Table(signature_data, colWidths=[2.5*inch, 1*inch, 2.5*inch])
        signature_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
        ]))
        
        elements.append(signature_table)
        elements.append(Spacer(1, 10))
        
        # Computer generated message
        elements.append(Paragraph(
            "This is a computer generated invoice and does not require physical signature.",
            ParagraphStyle('ComputerMsg', parent=styles['Normal'], fontSize=7, alignment=TA_CENTER, textColor=colors.grey)
        ))
        
        # Build PDF
        doc.build(elements)
        
        # Get the value of the BytesIO buffer and return it
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
        
    except Exception as e:
        print(f"Error generating pharmacy invoice PDF: {str(e)}")
        return None
