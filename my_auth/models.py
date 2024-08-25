from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from rest_framework import permissions
from loyalty.models import Action, Promos
from django.db import models
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, chat_id, full_name, promo, **extra_fields):
        if not chat_id:
            raise ValueError('The Chat ID must be set')
        user = self.model(
            chat_id=chat_id,
            full_name=full_name,
            promo=promo,
            **extra_fields
        )
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, chat_id, full_name, promo, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(chat_id, full_name, promo, **extra_fields)


class CustomUser(AbstractBaseUser):
    telegram_id = models.CharField(primary_key=True,unique=True)
    telegram_fullname = models.CharField(max_length=255,blank=True)
    phone = models.CharField(max_length=20, blank=True)
    kaspi_phone = models.CharField(max_length=20, blank=True)
    address = models.JSONField(blank=True,null=True)
    exact_address = models.CharField(max_length=255, null=True,blank=True)
    bonus = models.IntegerField(default=0)
    role = models.CharField(max_length=10, choices=[('manager', 'Manager'), ('client', 'Client'), ('admin', 'Admin'),
                                                    ('delivery', 'Delivery'),('cook', 'Cook'),('runner', 'Runner')], default='Client')
    promo = models.OneToOneField(Promos, on_delete=models.SET_NULL, null=True, blank=True)
    blocked = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    companies = models.ManyToManyField('service.CompanySpots', related_name='managers', blank=True,null=True)

    USERNAME_FIELD = 'telegram_id'
    REQUIRED_FIELDS = ['telegram_fullname']

    objects = CustomUserManager()

    def __str__(self):
        return self.telegram_fullname


class CustomUserAction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    amount = models.IntegerField()
    date_start = models.DateTimeField(null=True,blank=True)
    date_end = models.DateTimeField(null=True,blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'action')  # Для уникальности сочетания user-action

class UserToken(models.Model):
    telegram_id = models.IntegerField()
    access_token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.telegram_id} - {self.created_at} - {self.access_token}"
