from django.db import models
from food.models import Product
from my_auth.models import CustomUser
from food.models import Product

class DeliveryLayers(models.Model):
    points = models.JSONField()
    cost = models.IntegerField()

class CompanySpots(models.Model):
    manager = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='managed_companies',unique=True)
    name = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    open_time = models.TimeField()
    close_time = models.TimeField()
    address = models.JSONField()
    address_link = models.CharField(max_length=255)
    delivery_layers = models.ManyToManyField(DeliveryLayers,blank=True)
    products_on_stop = models.ManyToManyField(Product,blank=True)
    is_delivery = models.BooleanField(default=False)
    from food.models import Addition
    additions_on_stop = models.ManyToManyField(Addition,blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Reminder(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    scheduled_time = models.DateTimeField()
    is_sent = models.BooleanField(default=False)