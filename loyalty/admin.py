from django.contrib import admin
from .models import Action, Trigger, Payload
from .models import Promos


@admin.register(Promos)
class PromosAdmin(admin.ModelAdmin):
    list_display = ('token', 'name', 'link_to_source')


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'can_be_triggered', 'date_start', 'date_end')
    list_filter = ('can_be_triggered', 'date_start', 'date_end')
    search_fields = ('name',)


@admin.register(Trigger)
class TriggerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'short_name')
    search_fields = ('name', 'short_name')


@admin.register(Payload)
class PayloadAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'short_name')
    search_fields = ('name', 'short_name')
