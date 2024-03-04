from rest_framework import serializers
from .models import DeliveryLayers, CompanySpots
from rest_framework import serializers

class DeliveryLayersSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeliveryLayers
        fields = ['points', 'cost']

class CompanySpotsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanySpots
        fields = ['id', 'manager_id', 'name', 'link', 'open_time', 'close_time', 'address', 'address_link', 'delivery_layers', 'products_on_stop', 'additions_on_stop', 'updated_at', 'created_at']