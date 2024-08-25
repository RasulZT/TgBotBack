from rest_framework import serializers

from food.models import Product, Addition
from my_auth.models import CustomUser
from my_auth.serializers import CustomUserSerializer
from .models import DeliveryLayers, CompanySpots
from rest_framework import serializers



class DeliveryLayersSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryLayers
        fields = ['points', 'cost']


class CompanySpotsSerializer(serializers.ModelSerializer):
    delivery_layers = DeliveryLayersSerializer(many=True)
    products_on_stop = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), many=True)
    additions_on_stop = serializers.PrimaryKeyRelatedField(queryset=Addition.objects.all(), many=True)

    class Meta:
        model = CompanySpots
        fields = '__all__'

    def create(self, validated_data):
        delivery_layers_data = validated_data.pop('delivery_layers', None)
        products_on_stop_data = validated_data.pop('products_on_stop', [])
        additions_on_stop_data = validated_data.pop('additions_on_stop', [])

        # Проверяем существование пользователя с указанным telegram_id
        telegram_id = validated_data['manager'].telegram_id
        print(telegram_id)
        try:
            manager = CustomUser.objects.get(telegram_id=telegram_id)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("User with the provided telegram_id does not exist.")

        company_spot = CompanySpots.objects.create(**validated_data)

        if delivery_layers_data:
            for layer_data in delivery_layers_data:
                points_data = layer_data.pop('points')  # Получаем данные точек из словаря
                delivery_layer = DeliveryLayers.objects.create(points=points_data, cost=layer_data['cost'])
                company_spot.delivery_layers.add(delivery_layer)

        company_spot.products_on_stop.set(products_on_stop_data)
        company_spot.additions_on_stop.set(additions_on_stop_data)

        return company_spot

    def update(self, instance, validated_data):
        delivery_layers_data = validated_data.pop('delivery_layers', None)
        products_on_stop_data = validated_data.pop('products_on_stop', None)
        additions_on_stop_data = validated_data.pop('additions_on_stop', None)

        if delivery_layers_data:
            instance.delivery_layers.clear()  # Очищаем существующие связи
            for layer_data in delivery_layers_data:
                points_data = layer_data.pop('points')
                delivery_layer = DeliveryLayers.objects.create(points=points_data, cost=layer_data['cost'])
                instance.delivery_layers.add(delivery_layer)

        if products_on_stop_data is not None:
            instance.products_on_stop.set(products_on_stop_data)

        if additions_on_stop_data is not None:
            instance.additions_on_stop.set(additions_on_stop_data)

        # Обновляем остальные поля
        instance.name = validated_data.get('name', instance.name)
        instance.link = validated_data.get('link', instance.link)
        instance.open_time = validated_data.get('open_time', instance.open_time)
        instance.close_time = validated_data.get('close_time', instance.close_time)
        instance.address = validated_data.get('address', instance.address)
        instance.address_link = validated_data.get('address_link', instance.address_link)
        instance.manager = validated_data.get('manager', instance.manager_id)  # Обновляем manager_id
        instance.updated_at = validated_data.get('updated_at', instance.updated_at)
        instance.created_at = validated_data.get('created_at', instance.created_at)
        instance.save()

        return instance


from .models import Reminder


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ['id', 'user_id', 'message', 'scheduled_time', 'is_sent']
