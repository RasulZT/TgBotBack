from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from rest_framework import permissions



from django.db import models
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class CustomToken(models.Model):
    key = models.CharField(max_length=40, unique=True,primary_key=True)
    name = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.key}"

class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = 'Client'
        DELIVERY = 'Delivery'
        MANAGER = 'Manager'
        COMPANY_ADMIN = 'CompanyAdmin'
        ADMIN = 'Admin'

    username = models.EmailField(unique=True, null=True)
    password = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200, choices=Role.choices, default=Role.CLIENT)
    is_client = models.BooleanField(default=False)  # Флаг для обозначения клиентов
    is_company_admin = models.BooleanField(default=False)  # Флаг для обозначения админов компании
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        # Проверяем, что пользователь авторизован и имеет роль "менеджер"
        return request.user.is_authenticated and request.user.role == User.Role.MANAGER
