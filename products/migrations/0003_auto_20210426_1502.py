# Generated by Django 2.1.5 on 2021-04-26 09:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_product_categorie'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='categorie',
            new_name='category',
        ),
    ]