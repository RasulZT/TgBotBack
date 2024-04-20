# Generated by Django 5.0.1 on 2024-03-19 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0008_order_kaspi_phone'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='image',
        ),
        migrations.AddField(
            model_name='product',
            name='image_url',
            field=models.CharField(default=0, max_length=255),
            preserve_default=False,
        ),
    ]