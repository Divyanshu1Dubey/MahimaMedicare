# Generated manually for delivery and order status fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0008_medicine_expiry_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_method',
            field=models.CharField(choices=[('pickup', 'Pickup at Pharmacy'), ('delivery', 'Home Delivery')], default='pickup', max_length=20),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_phone',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('preparing', 'Preparing'), ('ready', 'Ready for Pickup'), ('out_for_delivery', 'Out for Delivery'), ('delivered', 'Delivered'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='order',
            name='pharmacist_notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='estimated_ready_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
