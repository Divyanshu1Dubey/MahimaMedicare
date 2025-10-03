from django.core.management.base import BaseCommand
from razorpay_payment.models import RazorpayPayment, Invoice
from razorpay_payment.invoice_utils import generate_invoice_for_payment

class Command(BaseCommand):
    help = 'Generate missing Invoice records for appointment and test payments'

    def handle(self, *args, **options):
        # Find payments that don't have Invoice records
        payments_without_invoices = RazorpayPayment.objects.filter(
            status='captured'
        ).exclude(
            payment_type='pharmacy'  # Skip pharmacy payments
        ).filter(
            invoice__isnull=True  # Only payments without invoices
        )

        self.stdout.write(f"Found {payments_without_invoices.count()} payments without invoices")

        created_count = 0
        error_count = 0

        for payment in payments_without_invoices:
            try:
                self.stdout.write(f"Generating invoice for payment {payment.payment_id} ({payment.payment_type})")
                invoice = generate_invoice_for_payment(payment)
                if invoice:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Created invoice {invoice.invoice_number} for payment {payment.payment_id}")
                    )
                else:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f"✗ Failed to create invoice for payment {payment.payment_id}")
                    )
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f"✗ Error creating invoice for payment {payment.payment_id}: {str(e)}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"\nCompleted: {created_count} invoices created, {error_count} errors")
        )