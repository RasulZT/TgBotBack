import pytz
from datetime import datetime, time, timedelta
import json
from django.utils.timezone import make_aware
from rest_framework import generics

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import render

# Create your views here.
from rest_framework.permissions import AllowAny
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from my_auth.models import CustomUser
from .models import Category, Product, OrderProduct, Order, Modifier, Addition, Tag
from .serializers import CategorySerializer, ProductSerializer, OrderProductSerializer, OrderSerializer, \
    ModifierSerializer, AdditionSerializer, TagSerializer

from django.http import Http404


class GetAllCategoriesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, category_id):
        try:
            return Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return None

    def get(self, request, category_id, *args, **kwargs):
        category = self.get_object(category_id)
        if category:
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, category_id, *args, **kwargs):
        category = self.get_object(category_id)
        if category:
            serializer = CategorySerializer(category, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, category_id, *args, **kwargs):
        category = self.get_object(category_id)
        if category:
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)


class GetProductsByCategoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, category_id, *args, **kwargs):
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        products = Product.objects.filter(category_id=category.id)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request, category_id, *args, **kwargs):
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        data["category_id"] = category.id
        serializer = ProductSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, product_id):
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return None

    def get(self, request, product_id, *args, **kwargs):
        product = self.get_object(product_id)
        if product:
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, product_id, *args, **kwargs):
        product = self.get_object(product_id)
        if product:
            serializer = ProductSerializer(product, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, product_id, *args, **kwargs):
        product = self.get_object(product_id)
        if product:
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)


class OrderListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Получаем данные запроса
        request_data = request.data

        # Получаем данные о бонусах и другие данные
        bonus_used = request_data.get('bonus_used', False)
        bonus_amount = request_data.get('bonus_amount', 0)
        client_id = request_data.get('client_id')

        # Получаем или создаем экземпляр CustomUser
        try:
            custom_user = CustomUser.objects.get(pk=client_id)
        except CustomUser.DoesNotExist:
            custom_user = CustomUser.objects.create(pk=client_id)

        # Проверяем, хватает ли у пользователя бонусов для совершения заказа
        if bonus_used and custom_user.bonus < bonus_amount:
            return Response(
                {"error": f"У вас не хватает бонусов. Ваши бонусы: {custom_user.bonus}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Создаем и сохраняем заказ
        order_serializer = OrderSerializer(data=request_data)
        if order_serializer.is_valid():
            order_instance = order_serializer.save()

            # Обновляем поля экземпляра CustomUser
            custom_user.kaspi_phone = request_data.get('kaspi_phone')
            custom_user.telegram_fullname=request.data.get('user_name')
            custom_user.phone = request_data.get('phone')
            custom_user.address = request_data.get('address')
            custom_user.exact_address = request_data.get('exact_address')
            if bonus_used:
                custom_user.bonus -= bonus_amount
            custom_user.save()
            print(json.dumps(request_data.get('address'), ensure_ascii=False))

            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO addresses (user_id, address, creation_date) "
                    "SELECT %s, %s, CURRENT_TIMESTAMP "
                    "WHERE NOT EXISTS (SELECT 1 FROM addresses WHERE user_id = %s AND address = %s)",
                    [client_id, json.dumps(request_data.get('address'), ensure_ascii=False), client_id,
                     json.dumps(request_data.get('address'), ensure_ascii=False)]
                )
            # Создаем и сохраняем OrderProduct для каждого продукта в списке
            products_data = request_data.get('products', [])
            for product_data in products_data:
                product_serializer = OrderProductSerializer(data=product_data)
                if product_serializer.is_valid():
                    product_instance = product_serializer.save()
                    order_instance.products.add(product_instance)

            return Response(order_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailAPIView(APIView):

    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        order = self.get_object(pk)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def put(self, request, pk):
        order = self.get_object(pk)
        bonus_amount = order.bonus_amount
        bonus_used = order.bonus_used
        sum_price = 0
        for i in list(order.products.values()):
            product = Product.objects.get(id=i['product_id_id'])
            sum_price += product.price
        serializer = OrderSerializer(order, data=request.data)
        if serializer.is_valid():
            status_value = request.data.get('status', None)
            if status_value == 'inactive':
                client_id = request.data.get('client_id')
                try:
                    custom_user = CustomUser.objects.get(pk=client_id)
                except CustomUser.DoesNotExist:
                    custom_user = CustomUser.objects.create(pk=client_id)
                if custom_user:
                    if order.is_delivery:
                        if bonus_used:
                            print(bonus_used,bonus_amount)
                            custom_user.bonus += int((sum_price-bonus_amount) * 5 / 100)
                        else:
                            custom_user.bonus += int(sum_price * 5 / 100)
                    else:
                        if bonus_used:
                            print(bonus_used, bonus_amount)
                            custom_user.bonus += int((sum_price - bonus_amount) * 10 / 100)
                        else:
                            custom_user.bonus += int(sum_price * 10 / 100)

                    custom_user.save()
            if status_value=='rejected':
                client_id = request.data.get('client_id')
                try:
                    custom_user = CustomUser.objects.get(pk=client_id)
                except CustomUser.DoesNotExist:
                    custom_user = CustomUser.objects.create(pk=client_id)
                if custom_user:
                    if bonus_used:
                        custom_user.bonus+=bonus_amount
                    custom_user.save()

            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        order = self.get_object(pk)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderProductListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        order_products = OrderProduct.objects.all()
        serializer = OrderProductSerializer(order_products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderProductDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return OrderProduct.objects.get(pk=pk)
        except OrderProduct.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        order_product = self.get_object(pk)
        serializer = OrderProductSerializer(order_product)
        return Response(serializer.data)

    def put(self, request, pk):
        order_product = self.get_object(pk)
        serializer = OrderProductSerializer(order_product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        order_product = self.get_object(pk)
        order_product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderWithActionsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, order_id, format=None):
        try:
            order = Order.objects.get(id=order_id)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)


class ModifierListCreateAPIView(APIView):
    def get(self, request):
        modifiers = Modifier.objects.all()
        serializer = ModifierSerializer(modifiers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ModifierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ModifierRetrieveUpdateDestroyAPIView(APIView):
    def get_object(self, pk):
        try:
            return Modifier.objects.get(pk=pk)
        except Modifier.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        modifier = self.get_object(pk)
        serializer = ModifierSerializer(modifier)
        return Response(serializer.data)

    def put(self, request, pk):
        modifier = self.get_object(pk)
        serializer = ModifierSerializer(modifier, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        modifier = self.get_object(pk)
        modifier.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdditionListAPIView(APIView):
    def get(self, request):
        additions = Addition.objects.all()
        serializer = AdditionSerializer(additions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AdditionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdditionDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Addition.objects.get(pk=pk)
        except Addition.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        addition = self.get_object(pk)
        serializer = AdditionSerializer(addition)
        return Response(serializer.data)

    def put(self, request, pk):
        addition = self.get_object(pk)
        serializer = AdditionSerializer(addition, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        addition = self.get_object(pk)
        addition.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagListAPIView(APIView):
    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Tag.objects.get(pk=pk)
        except Tag.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        tag = self.get_object(pk)
        serializer = TagSerializer(tag)
        return Response(serializer.data)

    def put(self, request, pk):
        tag = self.get_object(pk)
        serializer = TagSerializer(tag, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        tag = self.get_object(pk)
        tag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderFilterListAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['client_id', 'company_id', 'status','delivery_id']
    ordering_fields = ['created_at']
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        start_time_str = self.request.query_params.get('start_time')
        end_time_str = self.request.query_params.get('end_time')

        if start_time_str and end_time_str:
            # Парсинг времени из строки
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()

            # Отнять 5 часов
            start_time_utc = datetime.combine(datetime.today(), start_time) - timedelta(hours=5)
            end_time_utc = datetime.combine(datetime.today(), end_time) - timedelta(hours=5)

            # Фильтрация по времени в UTC
            queryset = Order.objects.filter(created_at__time__range=(start_time_utc.time(), end_time_utc.time()))
        else:
            queryset = Order.objects.all()

        return queryset


class OrderCountBonus(APIView):
    permission_classes = [AllowAny]
    def get_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            raise Http404
    def put(self, request, pk):
        order = self.get_object(pk)
        bonus_amount = order.bonus_amount
        bonus_used = order.bonus_used
        sum_price = 0
        for i in list(order.products.values()):
            product = Product.objects.get(id=i['product_id_id'])
            sum_price += product.price
        print(sum_price)
        serializer = OrderSerializer(order, data=request.data)
        if order.is_delivery:
            if bonus_used:
                bonus = int((sum_price - bonus_amount) * 5 / 100)
            else:
                bonus = int(sum_price * 5 / 100)
        else:
            if bonus_used:
                bonus = int((sum_price - bonus_amount) * 10 / 100)
            else:
                bonus = int(sum_price * 10 / 100)
        return Response(bonus)

