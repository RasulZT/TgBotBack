from rest_framework import serializers
from .models import Category, Modifier, Addition, Tag, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class ModifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modifier
        fields = ['id', 'price', 'currency', 'name', 'on_stop']


class AdditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Addition
        fields = ['id', 'price', 'currency', 'name', 'on_stop']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name', 'tag_color']


class ProductSerializer(serializers.ModelSerializer):
    modifiers = ModifierSerializer(many=True)
    additions = AdditionSerializer(many=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'category_id', 'image_url', 'name', 'description', 'price', 'currency', 'modifiers',
                  'additions', 'tags', 'on_stop']


from .models import Order, OrderProduct


class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
