from rest_framework import serializers

from .models import CustomUser, UserToken, CustomUserAction


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['telegram_id', 'telegram_fullname', 'phone', 'kaspi_phone', 'promo', 'address', 'exact_address',
                  'bonus', 'role','companies', 'blocked', 'updated_at', 'created_at']

    def create(self, validated_data):
        validated_data['role'] = 'client'  # устанавливаем роль по умолчанию
        return super().create(validated_data)


class UserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserToken
        fields = ['telegram_id', 'access_token', 'refresh_token', 'created_at']
class CustomUserActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserAction
        fields = '__all__'