from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import RazorpayPayment, Invoice, InvoiceItem
from .invoice_utils import generate_invoice_for_payment
from pharmacy.models import Medicine, Cart, Order
from hospital.models import Patient

User = get_user_model()

class InvoiceGenerationTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create a patient
        self.patient = Patient.objects.create(
            user=self.user,
            name='Test Patient',
            email='patient@example.com',
            phone_number=1234567890,
            address='Test Address'
        )
        
        # Create a medicine
        self.medicine = Medicine.objects.create(
            name='Test Medicine',
            description='Test Description',
            price=100,
            quantity=10,
            stock_quantity=50
        )
        
        # Create a cart item
        self.cart_item = Cart.objects.create(
            user=self.user,
            item=self.medicine,
            quantity=2
        )
        
        # Create an order
        self.order = Order.objects.create(
            user=self.user,
            ordered=True
        )
        self.order.orderitems.add(self.cart_item)
        
        # Create a payment
        self.payment = RazorpayPayment.objects.create(
            razorpay_order_id='order_test123',
            patient=self.patient,
            order=self.order,
            payment_type='pharmacy',
            amount=Decimal('240.00'),  # 2 * 100 + 40 delivery
            name='Test Patient',
            email='patient@example.com',
            phone='1234567890',
            status='captured'
        )
    
    def test_pharmacy_invoice_generation(self):
        """Test that pharmacy invoice generation works with correct field names"""
        # Generate invoice
        invoice = generate_invoice_for_payment(self.payment)
        
        # Check that invoice was created
        self.assertIsNotNone(invoice)
        self.assertEqual(invoice.payment, self.payment)
        self.assertEqual(invoice.customer_name, 'Test Patient')
        self.assertEqual(invoice.total_amount, Decimal('240.00'))
        
        # Check that invoice items were created correctly
        invoice_items = invoice.items.all()
        self.assertEqual(invoice_items.count(), 1)
        
        item = invoice_items.first()
        self.assertEqual(item.description, 'Test Medicine - Test Description')
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.unit_price, Decimal('100.00'))
        self.assertEqual(item.item_type, 'medicine')
        self.assertEqual(item.item_id, self.medicine.id)
    
    def test_invoice_pdf_generation(self):
        """Test that PDF generation works"""
        # Generate invoice
        invoice = generate_invoice_for_payment(self.payment)
        
        # Check that PDF was generated
        self.assertTrue(invoice.pdf_file)
        self.assertTrue(invoice.pdf_file.name.endswith('.pdf'))
    
    def test_cart_item_field_access(self):
        """Test that we can access cart item fields correctly"""
        # This test ensures our fix for 'Cart' object has no attribute 'medicine' works
        cart_item = self.cart_item
        
        # Should work - accessing item field
        self.assertEqual(cart_item.item.name, 'Test Medicine')
        self.assertEqual(cart_item.item.description, 'Test Description')
        self.assertEqual(cart_item.item.price, 100)
        
        # Should fail if we try to access 'medicine' field (the old bug)
        with self.assertRaises(AttributeError):
            _ = cart_item.medicine
