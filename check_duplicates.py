#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthstack.settings')
django.setup()

from razorpay_payment.models import RazorpayPayment, Invoice
from pharmacy.models import Order

print("=== CHECKING FOR DUPLICATE PAYMENTS ===")
print(f"Total Orders: {Order.objects.count()}")
print(f"Total Payments: {RazorpayPayment.objects.count()}")
print(f"Total Invoices: {Invoice.objects.count()}")

print("\n=== ORDER-PAYMENT ANALYSIS ===")
duplicates_found = False

for order in Order.objects.all():
    payments = RazorpayPayment.objects.filter(order=order)
    if payments.count() > 1:
        print(f"🚨 DUPLICATE: Order {order.id} has {payments.count()} payments!")
        for p in payments:
            print(f"   - Payment {p.id}: {p.status} - ₹{p.amount} - {p.created}")
        duplicates_found = True
    elif payments.count() == 1:
        print(f"✅ Order {order.id}: 1 payment (normal)")
    else:
        print(f"⚠️  Order {order.id}: 0 payments")

print("\n=== PAYMENT-INVOICE ANALYSIS ===")
for payment in RazorpayPayment.objects.filter(payment_type='pharmacy'):
    invoices = Invoice.objects.filter(payment=payment)
    if invoices.count() > 1:
        print(f"🚨 INVOICE DUPLICATE: Payment {payment.pk} has {invoices.count()} invoices!")
        duplicates_found = True
    elif invoices.count() == 1:
        print(f"✅ Payment {payment.pk}: 1 invoice (normal)")
    else:
        print(f"⚠️  Payment {payment.pk}: 0 invoices")

if not duplicates_found:
    print("\n✅ No duplicates found in database!")
else:
    print("\n🚨 Duplicates detected! Need to investigate further.")