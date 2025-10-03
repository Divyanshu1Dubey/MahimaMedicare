from django.core.management.base import BaseCommand
from razorpay_payment.models import RazorpayPayment, Invoice
from django.db.models import Count

class Command(BaseCommand):
    help = 'Clean up duplicate payments and invoices'

    def handle(self, *args, **options):
        self.stdout.write("Starting duplicate payment cleanup...")
        
        # Find duplicate pharmacy payments for same order
        pharmacy_duplicates = (
            RazorpayPayment.objects
            .filter(payment_type='pharmacy', order__isnull=False)
            .values('order_id')
            .annotate(count=Count('payment_id'))
            .filter(count__gt=1)
        )
        
        cleaned_pharmacy = 0
        for duplicate in pharmacy_duplicates:
            order_id = duplicate['order_id']
            payments = RazorpayPayment.objects.filter(
                payment_type='pharmacy', 
                order_id=order_id
            ).order_by('created_at')
            
            # Keep the first payment, delete others
            payments_to_delete = payments[1:]
            for payment in payments_to_delete:
                # Delete associated invoices first
                if hasattr(payment, 'invoice'):
                    payment.invoice.delete()
                payment.delete()
                cleaned_pharmacy += 1
                
        # Find duplicate test payments for same test_order
        test_duplicates = (
            RazorpayPayment.objects
            .filter(payment_type='test', test_order__isnull=False)
            .values('test_order_id')
            .annotate(count=Count('payment_id'))
            .filter(count__gt=1)
        )
        
        cleaned_test = 0
        for duplicate in test_duplicates:
            test_order_id = duplicate['test_order_id']
            payments = RazorpayPayment.objects.filter(
                payment_type='test', 
                test_order_id=test_order_id
            ).order_by('created_at')
            
            # Keep the first payment, delete others
            payments_to_delete = payments[1:]
            for payment in payments_to_delete:
                # Delete associated invoices first
                if hasattr(payment, 'invoice'):
                    payment.invoice.delete()
                payment.delete()
                cleaned_test += 1
                
        # Find duplicate appointment payments
        appointment_duplicates = (
            RazorpayPayment.objects
            .filter(payment_type='appointment', appointment__isnull=False)
            .values('appointment_id')
            .annotate(count=Count('payment_id'))
            .filter(count__gt=1)
        )
        
        cleaned_appointment = 0
        for duplicate in appointment_duplicates:
            appointment_id = duplicate['appointment_id']
            payments = RazorpayPayment.objects.filter(
                payment_type='appointment', 
                appointment_id=appointment_id
            ).order_by('created_at')
            
            # Keep the first payment, delete others
            payments_to_delete = payments[1:]
            for payment in payments_to_delete:
                # Delete associated invoices first  
                if hasattr(payment, 'invoice'):
                    payment.invoice.delete()
                payment.delete()
                cleaned_appointment += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Cleanup completed!\n'
                f'Removed {cleaned_pharmacy} duplicate pharmacy payments\n'
                f'Removed {cleaned_test} duplicate test payments\n'
                f'Removed {cleaned_appointment} duplicate appointment payments\n'
                f'Total cleaned: {cleaned_pharmacy + cleaned_test + cleaned_appointment}'
            )
        )