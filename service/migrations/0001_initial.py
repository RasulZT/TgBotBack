# Generated by Django 5.0.1 on 2024-03-11 17:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('food', '0001_initial'),
        ('my_auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryLayers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.JSONField()),
                ('cost', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='CompanySpots',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('link', models.CharField(max_length=255)),
                ('open_time', models.TimeField()),
                ('close_time', models.TimeField()),
                ('address', models.JSONField()),
                ('address_link', models.CharField(max_length=255)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('additions_on_stop', models.ManyToManyField(blank=True, to='food.addition')),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='managed_companies', to='my_auth.customuser')),
                ('products_on_stop', models.ManyToManyField(blank=True, to='food.product')),
                ('delivery_layers', models.ManyToManyField(blank=True, to='service.deliverylayers')),
            ],
        ),
    ]
