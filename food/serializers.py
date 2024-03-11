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
    tags = TagSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'category_id', 'image_url', 'name', 'description', 'price', 'currency', 'modifiers',
                  'additions', 'tags', 'on_stop']

    def create(self, validated_data):
        modifiers_data = validated_data.pop('modifiers', [])
        additions_data = validated_data.pop('additions', [])
        tags_data = validated_data.pop('tags', [])

        product = Product.objects.create(**validated_data)

        for modifier_data in modifiers_data:
            Modifier.objects.create(product=product, **modifier_data)

        for addition_data in additions_data:
            Addition.objects.create(product=product, **addition_data)

        for tag_data in tags_data:
            # Создаем или получаем объект тега по переданным данным и связываем его с продуктом
            tag, _ = Tag.objects.get_or_create(**tag_data)
            print(tag)
            product.tags.add(tag)

        return product

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        additions_data = validated_data.pop('additions', None)
        modifiers_data = validated_data.pop('modifiers', None)

        # Удаляем существующие связи с тегами
        instance.tags.clear()

        instance = super().update(instance, validated_data)

        # Создаем новые связи с тегами
        if tags_data:
            for tag_data in tags_data:
                tag, _ = Tag.objects.get_or_create(name=tag_data['name'], tag_color=tag_data['tag_color'])
                instance.tags.add(tag)

        # Обновляем вложенные добавки продукта
        if additions_data:
            instance.additions.clear()  # Очищаем существующие добавки
            for addition_data in additions_data:
                addition, _ = Addition.objects.get_or_create(name=addition_data['name'], price=addition_data['price'])
                instance.additions.add(addition)

        # Обновляем вложенные модификаторы продукта
        if modifiers_data:
            instance.modifiers.clear()  # Очищаем существующие модификаторы
            for modifier_data in modifiers_data:
                modifier, _ = Modifier.objects.get_or_create(name=modifier_data['name'], price=modifier_data['price'])
                instance.modifiers.add(modifier)

        return instance



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
