from django.db import models

class Client(models.Model):
    telegram_id = models.IntegerField()
    telegram_fullname = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.JSONField(blank=True, null=True)
    bonus = models.FloatField(default=0, blank=True, null=True)
    history = models.JSONField(blank=True, null=True)
    role = models.CharField(max_length=255, default='user', blank=True, null=True)
    blocked = models.JSONField(default=dict, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Client {self.id}"
