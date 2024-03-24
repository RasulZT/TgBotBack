from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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
        print(request.data['products'])
        order_serializer = OrderSerializer(data=request.data)
        if not order_serializer.is_valid(): return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        order_instance = order_serializer.save()
        order_id = order_instance.id

        kaspi_phone = request.data.get('kaspi_phone')
        address = request.data.get('address')
        client_id = request.data.get('client_id')

        try:
            custom_user = CustomUser.objects.get(pk=client_id)
        except CustomUser.DoesNotExist:
            custom_user = CustomUser.objects.create(pk=client_id)

            # Обновляем поля в экземпляре CustomUser
        custom_user.kaspi_phone = kaspi_phone
        custom_user.address = address

        # Сохраняем экземпляр CustomUser
        custom_user.save()
        # Создаем OrderProduct для каждого продукта в списке
        products_data = request.data.get('products', [])

        for product_data in products_data:
            product_serializer = OrderProductSerializer(data=product_data)
            if product_serializer.is_valid():
                productorder_instance= product_serializer.save()
                orderproduct_id=productorder_instance.id
                print("HAHAH")

                print(order_id,orderproduct_id)
                with connection.cursor() as cursor:
                    sql_query = "INSERT INTO food_order_products (order_id, orderproduct_id) VALUES (%s, %s)"
                    cursor.execute(sql_query, [order_id, orderproduct_id])
            else:
                # Если данные продукта некорректны, возвращаем ошибку
                return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(order_serializer.data, status=status.HTTP_201_CREATED)

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
        serializer = OrderSerializer(order, data=request.data)
        if serializer.is_valid():
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