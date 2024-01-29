from django.db import models

from django.db import models

from users.models import Client
from django.contrib.postgres.fields import ArrayField


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Modifier(models.Model):
    price = models.IntegerField()
    currency = models.CharField(max_length=3)  # 'KZT'
    name = models.CharField(max_length=255)
    on_stop = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Addition(models.Model):
    price = models.IntegerField()
    currency = models.CharField(max_length=3)  # 'KZT'
    name = models.CharField(max_length=255)
    on_stop = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    tag_color = models.CharField(max_length=7, unique=True)  # Assuming hex color code, e.g., '#RRGGBB'


class Product(models.Model):
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    image_url = models.URLField()
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.IntegerField(blank=True, null=True)
    currency = models.CharField(max_length=3)  # 'KZT'
    modifiers = models.ManyToManyField(Modifier, null=True, blank=True)
    additions = models.ManyToManyField(Addition, null=True, blank=True)
    tags = models.ManyToManyField(Tag, null=True, blank=True)
    on_stop = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderProduct(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    active_modifier = models.ForeignKey(Modifier, on_delete=models.SET_NULL, null=True, blank=True)
    additions = models.ManyToManyField(Addition, blank=True)
    amount = models.PositiveIntegerField()
    client_comment = models.TextField(blank=True)
    price = models.IntegerField(blank=True)

    def __str__(self):
        return f"{self.product_id} - {self.amount}"


class Order(models.Model):
    PAYMENT_AWAIT = 'payment_await'
    MANAGER_AWAIT = 'manager_await'
    ACTIVE = 'active'
    DONE = 'done'
    ON_DELIVERY = 'on_delivery'
    INACTIVE = 'inactive'

    ORDER_STATUSES = [
        (PAYMENT_AWAIT, 'Payment Await'),
        (MANAGER_AWAIT, 'Manager Await'),
        (ACTIVE, 'Active'),
        (DONE, 'Done'),
        (ON_DELIVERY, 'On Delivery'),
        (INACTIVE, 'Inactive'),
    ]

    id = models.AutoField(primary_key=True)
    client_id = models.IntegerField()  # Assuming telegram_id is an integer
    status = models.CharField(max_length=20, choices=ORDER_STATUSES, default=PAYMENT_AWAIT)
    bonus_used = models.BooleanField(default=False)
    user_name = models.CharField(max_length=255)
    loc = models.FloatField()
    lat = models.FloatField()
    exact_address = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20)
    # actions = models.ManyToManyField(OrderAction, blank=True)
    products = models.ManyToManyField(OrderProduct)
    client_comment = models.TextField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.status}"
