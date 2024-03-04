from django.db import models
from food.models import Product

class DeliveryLayers(models.Model):
    points = models.JSONField()
    cost = models.IntegerField()

class CompanySpots(models.Model):
    manager_id = models.IntegerField()
    name = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    open_time = models.TimeField()
    close_time = models.TimeField()
    address = models.JSONField()
    address_link = models.CharField(max_length=255)
    delivery_layers = models.ManyToManyField(DeliveryLayers)
    products_on_stop = models.ManyToManyField(Product)
    from food.models import Addition
    additions_on_stop = models.ManyToManyField(Addition)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
