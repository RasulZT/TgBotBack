from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DeliveryLayers, CompanySpots
from .serializers import DeliveryLayersSerializer, CompanySpotsSerializer


class DeliveryLayersAPIView(APIView):
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
    def get(self, request):
        company_spots = CompanySpots.objects.all()
        serializer = CompanySpotsSerializer(company_spots, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CompanySpotsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



