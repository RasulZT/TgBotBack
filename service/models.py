from django.db import models
from food.models import Product
from my_auth.models import CustomUser
from food.models import Product, Action, OrderProduct
from django.utils import timezone
from django.core.validators import MinLengthValidator
from django.contrib.auth.hashers import make_password
class DeliveryLayers(models.Model):
    points = models.JSONField()
    cost = models.IntegerField()


class CompanySpots(models.Model):
    name = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    open_time = models.TimeField()
    close_time = models.TimeField()
    address = models.JSONField()
    address_link = models.CharField(max_length=255)
    delivery_layers = models.ManyToManyField(DeliveryLayers, blank=True)
    products_on_stop = models.ManyToManyField(Product, blank=True)
    is_delivery = models.BooleanField(default=False)
    from food.models import Addition
    additions_on_stop = models.ManyToManyField(Addition, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Reminder(models.Model):
    user_id = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    scheduled_time = models.DateTimeField()
    is_sent = models.BooleanField(default=False)


# models.py
class ArchivedOrder(models.Model):
    PAYMENT_AWAIT = 'payment_await'
    MANAGER_AWAIT = 'manager_await'
    ACTIVE = 'active'
    DONE = 'done'
    ON_DELIVERY = 'on_delivery'
    INACTIVE = 'inactive'
    REJECTED = 'rejected'

    ORDER_STATUSES = [
        (PAYMENT_AWAIT, 'Payment Await'),
        (MANAGER_AWAIT, 'Manager Await'),
        (ACTIVE, 'Active'),
        (DONE, 'Done'),
        (ON_DELIVERY, 'On Delivery'),
        (INACTIVE, 'Inactive'),
        (REJECTED, 'Rejected')
    ]

    original_order_id = models.IntegerField()
    client_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='archived_client_orders')
    delivery_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='archived_delivery_orders',
                                    blank=True, null=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUSES, default=MANAGER_AWAIT)
    bonus_used = models.BooleanField(default=False)
    is_delivery = models.BooleanField(default=False)
    user_name = models.CharField(max_length=255)
    address = models.JSONField(blank=True)
    exact_address = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20)
    kaspi_phone = models.CharField(max_length=20, blank=True)
    actions = models.ManyToManyField(Action, blank=True)
    products = models.ManyToManyField(OrderProduct, blank=True)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(5)], null=True, blank=True)
    rejected_text = models.TextField(null=True, blank=True)
    client_comment = models.TextField(null=True, blank=True)
    company_id = models.ForeignKey('service.CompanySpots', on_delete=models.SET_NULL, null=True, blank=True)
    done_time = models.TimeField(null=True, blank=True)
    bonus_amount = models.IntegerField(default=0, blank=True, null=True)
    delivery_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Archived Order {self.original_order_id} - {self.status}"


class Integration(models.Model):
    companySpot = models.ForeignKey('service.CompanySpots', on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    login = models.CharField(max_length=25,unique=True)
    password = models.CharField(max_length=128)  # Пароль лучше хранить в зашифрованном виде
    token = models.CharField(max_length=40, unique=True, validators=[MinLengthValidator(10)])  # Уникальный токен для нас (не каспи)
    api=models.CharField(max_length=128)
    created_at = models.DateTimeField(default=timezone.now)  # Время создания
    updated_at = models.DateTimeField(auto_now=True)  # Время последнего обновления

    class Meta:
        unique_together = ('companySpot', 'user')  # Уникальная комбинация companySpot и user

    def __str__(self):
        return f"Integration for {self.user} with {self.companySpot}"

    # Пример метода для шифрования пароля перед сохранением
    def save(self, *args, **kwargs):
        if self.password:
            self.password = self.encrypt_password(self.password)  # Метод для шифрования
        super().save(*args, **kwargs)

    def encrypt_password(self, raw_password):
        return make_password(raw_password)

class Payment(models.Model):
    order_id = models.CharField(max_length=100, unique=True)  # Уникальный идентификатор заказа
    payment_data = models.JSONField()