# Generated by Django 5.0.1 on 2024-03-13 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0003_alter_order_client_id_alter_order_delivery_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='lat',
        ),
        migrations.RemoveField(
            model_name='order',
            name='long',
        ),
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.JSONField(default=0),
            preserve_default=False,
        ),
    ]
