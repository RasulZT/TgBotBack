from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category, Product, OrderProduct, Order
from .serializers import CategorySerializer, ProductSerializer, OrderProductSerializer, OrderSerializer

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
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
