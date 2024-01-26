from rest_framework import serializers
from django.contrib.auth.models import User

from users.models import Client

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'