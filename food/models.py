from django.db import models

from django.db import models

from django.contrib.postgres.fields import ArrayField

from loyalty.models import Action
from my_auth.models import CustomUser


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
    name = models.CharField(max_length=255)
    tag_color = models.CharField(max_length=7)  # Assuming hex color code, e.g., '#RRGGBB'

class Company(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    link = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    spots = models.ManyToManyField('service.CompanySpots', related_name='companies')


class Product(models.Model):
    image_url = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.IntegerField(blank=True, null=True)
    currency = models.CharField(max_length=3)  # 'KZT'
    modifiers = models.ManyToManyField(Modifier, null=True, blank=True)
    additions = models.ManyToManyField(Addition, null=True, blank=True)
    tags = models.ManyToManyField(Tag, null=True, blank=True)
    on_stop = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products')
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
    REJECTED='rejected'

    ORDER_STATUSES = [
        (PAYMENT_AWAIT, 'Payment Await'),
        (MANAGER_AWAIT, 'Manager Await'),
        (ACTIVE, 'Active'),
        (DONE, 'Done'),
        (ON_DELIVERY, 'On Delivery'),
        (INACTIVE, 'Inactive'),
        (REJECTED,'Rejected')
    ]
    RATING_CHOICES = [(i, str(i)) for i in range(5)]  # Выбор оценки от 0 до 4
    id = models.AutoField(primary_key=True)
    client_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='client_orders')
    delivery_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='delivery_orders',blank=True,null=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUSES, default=MANAGER_AWAIT)
    bonus_used = models.BooleanField(default=False)
    user_name = models.CharField(max_length=255)
    address=models.JSONField( blank=True)
    exact_address = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20)
    kaspi_phone = models.CharField(max_length=20, blank=True)
    actions = models.ManyToManyField(Action, blank=True,null=True)
    products = models.ManyToManyField(OrderProduct,blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    rejected_text=models.TextField(null=True, blank=True)
    client_comment = models.TextField(null=True, blank=True)
    from service.models import CompanySpots
    company_id = models.ForeignKey(CompanySpots, on_delete=models.SET_NULL, null=True, blank=True)
    done_time = models.TimeField(null=True, blank=True)
    bonus_amount = models.IntegerField(default=0,blank=True,null=True)  # Количество бонусов
    delivery_price = models.DecimalField(max_digits=10, decimal_places=2, default=0,blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.status}"

