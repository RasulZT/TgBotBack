from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import DeliveryLayers, CompanySpots, Reminder, Integration, Payment


@admin.register(DeliveryLayers)
class DeliveryLayersAdmin(admin.ModelAdmin):
    list_display = ('id', 'cost')


@admin.register(CompanySpots)
class CompanySpotsAdmin(admin.ModelAdmin):
    list_display = ('id', 'address', 'address_link', 'updated_at', 'created_at')


admin.site.register(Reminder)


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'companySpot', 'login', 'token', 'created_at', 'updated_at')
    search_fields = ('user__telegram_fullname', 'companySpot__name', 'login', 'token')
    list_filter = ('created_at', 'updated_at')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'payment_data')
    search_fields = ('order_id',)
