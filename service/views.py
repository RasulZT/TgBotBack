from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from my_auth.models import CustomUser
from my_auth.permissions import IsLogined
from .models import DeliveryLayers, CompanySpots
from .serializers import DeliveryLayersSerializer, CompanySpotsSerializer
from rest_framework.permissions import AllowAny
from django.http import Http404


class DeliveryLayersAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        delivery_layers = DeliveryLayers.objects.all()
        serializer = DeliveryLayersSerializer(delivery_layers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DeliveryLayersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanySpotsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        company_spots = CompanySpots.objects.all()
        serializer = CompanySpotsSerializer(company_spots, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CompanySpotsSerializer(data=request.data)
        if serializer.is_valid():
            company_spot = serializer.save()

            # Найти пользователя по telegram_id
            telegram_id = serializer.validated_data['manager'].telegram_id
            print(telegram_id)
            try:
                manager = CustomUser.objects.get(telegram_id=telegram_id)
            except CustomUser.DoesNotExist:
                return Response({"error": "User with the provided telegram_id does not exist."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Обновить роль пользователя на Manager
            manager.role = 'Manager'
            manager.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeliveryLayersDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return DeliveryLayers.objects.get(pk=pk)
        except DeliveryLayers.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        delivery_layers = self.get_object(pk)
        serializer = DeliveryLayersSerializer(delivery_layers)
        return Response(serializer.data)

    def put(self, request, pk):
        delivery_layers = self.get_object(pk)
        serializer = DeliveryLayersSerializer(delivery_layers, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        delivery_layers = self.get_object(pk)
        delivery_layers.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CompanySpotsDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return CompanySpots.objects.get(pk=pk)
        except CompanySpots.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        company_spot = self.get_object(pk)
        serializer = CompanySpotsSerializer(company_spot)
        return Response(serializer.data)

    def put(self, request, pk):
        company_spot = self.get_object(pk)
        serializer = CompanySpotsSerializer(company_spot, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        company_spot = self.get_object(pk)
        company_spot.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
