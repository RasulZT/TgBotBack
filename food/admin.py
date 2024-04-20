from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Category, Modifier, Addition, Tag, Product, OrderProduct, Order, Company
from .serializers import CategorySerializer, ModifierSerializer, AdditionSerializer, TagSerializer, ProductSerializer


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'updated_at', 'created_at']


admin.site.register(Category, CategoryAdmin)


class ModifierAdmin(admin.ModelAdmin):
    list_display = ['id', 'price', 'currency', 'name', 'on_stop', 'updated_at', 'created_at']


admin.site.register(Modifier, ModifierAdmin)


class AdditionAdmin(admin.ModelAdmin):
    list_display = ['id', 'price', 'currency', 'name', 'on_stop', 'updated_at', 'created_at']


admin.site.register(Addition, AdditionAdmin)


class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


admin.site.register(Tag, TagAdmin)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'link', 'contact_info', 'updated_at', 'created_at']
    search_fields = ['name', 'description', 'contact_info']
    list_filter = ['updated_at', 'created_at']

class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'category_id', 'image_url', 'name', 'description', 'price', 'currency', 'on_stop',
                    'updated_at', 'created_at']


admin.site.register(Product, ProductAdmin)

admin.site.register(OrderProduct)
admin.site.register(Order)