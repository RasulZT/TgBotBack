from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import DeliveryLayers, CompanySpots, Reminder


@admin.register(DeliveryLayers)
class DeliveryLayersAdmin(admin.ModelAdmin):
    list_display = ('id', 'cost')

@admin.register(CompanySpots)
class CompanySpotsAdmin(admin.ModelAdmin):
    list_display = ('id', 'manager_id', 'address', 'address_link', 'updated_at', 'created_at')

admin.site.register(Reminder)