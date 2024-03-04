from rest_framework import serializers
from .models import Action, Trigger, Payload, Promos


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ['id', 'name', 'can_be_triggered', 'date_start', 'date_end', 'triggers', 'payloads']

class TriggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trigger
        fields = ['id', 'name', 'short_name', 'payload']

class PayloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payload
        fields = ['id', 'name', 'short_name', 'payload']


class PromosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promos
        fields = ['token', 'name', 'link_to_source']
