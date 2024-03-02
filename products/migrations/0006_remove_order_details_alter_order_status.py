# Generated by Django 4.0.6 on 2024-02-07 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_order_details'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='details',
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('shipped', 'Shipped'), ('delivered', 'Delivered')], default='Order Placed', max_length=20),
        ),
    ]
