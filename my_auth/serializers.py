from rest_framework import serializers

from .models import CustomUser, UserToken


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['telegram_id', 'telegram_fullname', 'phone', 'promo', 'address', 'exact_address', 'bonus', 'role', 'blocked', 'updated_at', 'created_at']

    def create(self, validated_data):
        validated_data['role'] = 'client'  # устанавливаем роль по умолчанию
        return super().create(validated_data)
class UserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserToken
        fields = ['telegram_id', 'access_token', 'refresh_token', 'created_at']