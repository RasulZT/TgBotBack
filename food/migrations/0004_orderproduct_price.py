# Generated by Django 5.0.1 on 2024-01-26 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0003_rename_product_orderproduct_product_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderproduct',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]