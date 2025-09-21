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


class InvoicePDFGenerator:
    def __init__(self, invoice):
        self.invoice = invoice
        self.buffer = BytesIO()
        self.pagesize = A4
        self.width, self.height = self.pagesize
        
    def generate_pdf(self):
        """Generate PDF invoice and return the buffer"""
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
        
        # Add company header
        story.extend(self._create_header())
        story.append(Spacer(1, 20))
        
        # Add invoice details
        story.extend(self._create_invoice_details())
        story.append(Spacer(1, 10))
        
        # Add invoice items table
        story.extend(self._create_items_table())
        story.append(Spacer(1, 20))
        
        # Add totals
        story.extend(self._create_totals())
        story.append(Spacer(1, 20))
        
        # Add footer
        story.extend(self._create_footer())
        
        # Build PDF
        doc.build(story)
        
        # Get PDF content
        pdf_content = self.buffer.getvalue()
        self.buffer.close()
        
        return pdf_content
    
    def _create_header(self):
        """Create GST tax invoice header section"""
        styles = getSampleStyleSheet()
        
        # Create header table with company info and GST tax invoice title
        header_data = [
            # Row 1: Subject to jurisdiction and GST TAX INVOICE
            [
                Paragraph('<font size="8">Subject to Vadodara Jurisdiction</font>', styles['Normal']),
                Paragraph('<font size="16"><b>GST TAX INVOICE</b></font>', 
                         ParagraphStyle('Title', parent=styles['Normal'], alignment=TA_CENTER, fontSize=16))
            ],
            # Row 2: Company name and Original for Buyer
            [
                Paragraph(f'<font size="14"><b>{self.invoice.company_name}</b></font>', styles['Normal']),
                Paragraph('<font size="8">Original for Buyer</font>', 
                         ParagraphStyle('OriginalBuyer', parent=styles['Normal'], alignment=TA_RIGHT, fontSize=8))
            ],
            # Row 3: Company details
            [
                Paragraph(f'''<font size="9">
                Sale of - I, Near Mani Residency Complex,<br/>
                {self.invoice.company_address}<br/>
                Ph.: {self.invoice.company_phone} | Email: info@mahimamedicare.com
                </font>''', styles['Normal']),
                ''
            ]
        ]
        
        header_table = Table(header_data, colWidths=[4*inch, 2.5*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        return [header_table, Spacer(1, 10)]
    
    def _create_invoice_details(self):
        """Create GST invoice details section"""
        styles = getSampleStyleSheet()
        
        # Create invoice details table matching GST format
        details_data = [
            # Row 1: D.L. No, State & Code, Invoice details
            [
                Paragraph('<font size="8"><b>D.L. No.</b><br/>20C VAD 94560, 20D VAD 93441<br/><b>Dated:</b> 20 May 2000<br/><b>Food Reg. No.</b><br/><b>GSTIN:</b> 24AAKPP1343N1ZK</font>', styles['Normal']),
                Paragraph('<font size="8"><b>State & Code</b><br/>Invoice No. : 12<br/>Date : 18-04-2024<br/>Due Date : 28-05-2024<br/>Invoice Type : C</font>', styles['Normal']),
            ],
            # Row 2: To section and GSTIN details
            [
                Paragraph(f'''<font size="9"><b>To</b><br/>
                <b>{self.invoice.customer_name}</b><br/>
                {self.invoice.customer_address or "Address not provided"}<br/>
                Ph No.: {self.invoice.customer_phone}
                </font>''', styles['Normal']),
                Paragraph(f'''<font size="8"><b>GSTIN No.</b><br/>
                <b>D.L. No.</b><br/>
                <b>PAN No.</b><br/>
                <b>State & Code:</b> Gujarat-24
                </font>''', styles['Normal'])
            ]
        ]
        
        details_table = Table(details_data, colWidths=[3.5*inch, 3*inch])
        details_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        return [details_table]
    
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
        """Create GST invoice items table"""
        # Table headers matching GST format
        headers = [
            'Sr.', 'HSN', 'Mfg.', 'Product Name', 'Pack', 'MRP', 'Batch No.', 'Exp Dt', 'Qty', 'Free', 'Rate', 'Dis %', 'GST%', 'Amount'
        ]
        
        # Table data
        data = [headers]
        
        sr_no = 1
        for item in self.invoice.items.all():
            # Calculate GST (assuming 12% for medical services)
            gst_rate = 12 if item.item_type in ['appointment', 'test'] else 5  # 5% for medicines
            base_amount = float(item.unit_price)
            gst_amount = (base_amount * gst_rate) / (100 + gst_rate)
            net_amount = base_amount - gst_amount
            
            row = [
                str(sr_no),
                '1234',  # HSN code - you can make this dynamic
                'Cipla',  # Manufacturer - you can make this dynamic
                item.description,
                '1 X 10' if item.item_type == 'medicine' else '1',  # Pack
                f"₹{item.unit_price:.2f}",  # MRP
                'ABC345' if item.item_type == 'medicine' else '-',  # Batch No
                '03-2026' if item.item_type == 'medicine' else '-',  # Exp Date
                str(item.quantity),
                '0',  # Free
                f"₹{net_amount:.2f}",  # Rate (without GST)
                '0',  # Discount %
                f"{gst_rate}%",  # GST %
                f"₹{item.total_price:.2f}"  # Amount
            ]
            data.append(row)
            sr_no += 1
        
        # Create table with appropriate column widths
        col_widths = [0.3*inch, 0.4*inch, 0.4*inch, 2*inch, 0.5*inch, 0.6*inch, 0.6*inch, 0.5*inch, 0.3*inch, 0.3*inch, 0.6*inch, 0.4*inch, 0.4*inch, 0.7*inch]
        table = Table(data, colWidths=col_widths)
        
        # Table style matching GST format
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Sr. No center
            ('ALIGN', (3, 1), (3, -1), 'LEFT'),    # Product name left
            ('ALIGN', (4, 1), (-1, -1), 'CENTER'), # Rest center aligned
            
            # Grid and borders
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return [table]
    
    def _create_totals(self):
        """Create GST totals section"""
        styles = getSampleStyleSheet()
        
        # Calculate GST breakdown
        total_amount = float(self.invoice.total_amount)
        
        # Create totals table matching GST format
        totals_data = [
            # Row 1: Remarks and GST breakdown
            [
                Paragraph('<font size="8"><b>Remarks:</b></font>', styles['Normal']),
                Paragraph('<font size="8"><b>GST %</b></font>', styles['Normal']),
                Paragraph('<font size="8"><b>Taxable Amt</b></font>', styles['Normal']),
                Paragraph('<font size="8"><b>SGST Amt</b></font>', styles['Normal']),
                Paragraph('<font size="8"><b>CGST Amt</b></font>', styles['Normal']),
                Paragraph('<font size="8"><b>Tax Amt</b></font>', styles['Normal'])
            ],
            # Row 2: Values
            [
                '',
                Paragraph('<font size="8">12 %</font>', styles['Normal']),
                Paragraph(f'<font size="8">₹{total_amount * 0.89:.2f}</font>', styles['Normal']),
                Paragraph(f'<font size="8">₹{total_amount * 0.055:.2f}</font>', styles['Normal']),
                Paragraph(f'<font size="8">₹{total_amount * 0.055:.2f}</font>', styles['Normal']),
                Paragraph(f'<font size="8">₹{total_amount * 0.11:.2f}</font>', styles['Normal'])
            ]
        ]
        
        totals_table = Table(totals_data, colWidths=[2*inch, 0.8*inch, 1*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        totals_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        # Bank details and final total
        bank_details = Paragraph(f'''<font size="8">
        <b>Bank Details:</b><br/>
        State Bank of India<br/>
        Ac No.: 30880782555 IFSC Code: SBIN223ED1<br/>
        <b>Terms & Conditions:</b><br/>
        Subject to Vadodara Jurisdiction<br/>
        Advance Payment before Delivery.<br/>
        E-Invoice data
        </font>''', styles['Normal'])
        
        final_total = Paragraph(f'''<font size="10">
        <b>Sub Total:</b> ₹{total_amount * 0.89:.2f}<br/>
        <b>Discount:</b> ₹0.00<br/>
        <b>CGST/SGST:</b> ₹{total_amount * 0.11:.2f}<br/>
        <b>SGST:</b> ₹{total_amount * 0.055:.2f}<br/>
        <br/>
        <b>Net Amount:</b> ₹{total_amount:.2f}
        </font>''', styles['Normal'])
        
        # Bottom section
        bottom_data = [
            [bank_details, final_total]
        ]
        
        bottom_table = Table(bottom_data, colWidths=[4*inch, 2.5*inch])
        bottom_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        return [totals_table, Spacer(1, 10), bottom_table]
    
    def _create_footer(self):
        """Create GST invoice footer"""
        styles = getSampleStyleSheet()
        
        footer = []
        
        # Company signature line
        footer.append(Spacer(1, 20))
        
        signature_data = [
            ['', f'for {self.invoice.company_name}', 'Page 1 of 1']
        ]
        
        signature_table = Table(signature_data, colWidths=[2*inch, 3*inch, 1.5*inch])
        signature_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ]))
        
        footer.append(signature_table)
        
        # Computer generated message
        footer.append(Spacer(1, 10))
        footer.append(Paragraph(
            '<font size="7">This is computer generated invoice hence doesn\'t require signature</font>',
            ParagraphStyle('ComputerGenerated', parent=styles['Normal'], alignment=TA_CENTER, fontSize=7)
        ))
        
        return footer


def generate_invoice_for_payment(payment):
    """
    Generate invoice for a successful payment
    """
    try:
        from .models import Invoice, InvoiceItem
        
        # Check if invoice already exists
        if hasattr(payment, 'invoice'):
            return payment.invoice
        
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
            f"invoice_{invoice_number}.pdf",
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
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        # Title
        title = Paragraph("MAHIMA MEDICARE", title_style)
        elements.append(title)
        
        subtitle = Paragraph("Medicine Purchase Invoice", styles['Heading2'])
        elements.append(subtitle)
        elements.append(Spacer(1, 20))
        
        # Invoice details
        invoice_data = [
            ['Invoice Number:', f'INV-{order.id:06d}'],
            ['Order Date:', order.created.strftime('%B %d, %Y')],
            ['Payment Status:', 'Paid'],
            ['Order Status:', order.get_order_status_display()],
        ]
        
        invoice_table = Table(invoice_data, colWidths=[2*inch, 3*inch])
        invoice_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(invoice_table)
        elements.append(Spacer(1, 20))
        
        # Patient details
        patient_header = Paragraph("Patient Information", header_style)
        elements.append(patient_header)
        
        patient_data = [
            ['Name:', order.user.patient.name if hasattr(order.user, 'patient') else order.user.username],
            ['Phone:', order.delivery_phone or 'N/A'],
            ['Delivery Method:', order.get_delivery_method_display()],
        ]
        
        if order.delivery_method == 'delivery' and order.delivery_address:
            patient_data.append(['Address:', order.delivery_address])
        
        patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(patient_table)
        elements.append(Spacer(1, 20))
        
        # Medicine details
        medicine_header = Paragraph("Medicine Details", header_style)
        elements.append(medicine_header)
        
        # Table headers
        medicine_data = [['Medicine Name', 'Quantity', 'Unit Price', 'Total Price']]
        
        # Add medicine items
        for item in order.orderitems.all():
            medicine_data.append([
                item.item.name,
                str(item.quantity),
                f'₹{item.item.price:.2f}',
                f'₹{item.get_total():.2f}'
            ])
        
        medicine_table = Table(medicine_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
        medicine_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(medicine_table)
        elements.append(Spacer(1, 20))
        
        # Billing summary
        billing_header = Paragraph("Billing Summary", header_style)
        elements.append(billing_header)
        
        subtotal = order.get_totals()
        gst_amount = order.get_gst_amount()
        delivery_fee = 40 if order.delivery_method == 'delivery' else 0
        total_amount = order.final_bill()
        
        billing_data = [
            ['Subtotal:', f'₹{subtotal:.2f}'],
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
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        ]))
        elements.append(billing_table)
        elements.append(Spacer(1, 30))
        
        # Footer
        footer_text = "Thank you for choosing Mahima Medicare for your healthcare needs!"
        footer = Paragraph(footer_text, styles['Normal'])
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
        # Get the value of the BytesIO buffer and return it
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
        
    except Exception as e:
        print(f"Error generating pharmacy invoice PDF: {str(e)}")
        return None
