import json

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





from django.db import connection
from django.http import JsonResponse

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def get_addresses(request):
    request_data = json.loads(request.body.decode('utf-8'))
    if 'search_string' in request_data:
        search_string = request_data['search_string'].lower()  # Приведение строки запроса к нижнему регистру

        # Разделение строки запроса на улицу и номер дома
        search_parts = search_string.split()
        if len(search_parts) == 2:
            street = search_parts[0]
            housenumber = search_parts[1]
        else:
            street = search_string
            housenumber = None  # Если номер дома не указан в запросе

        with connection.cursor() as cursor:
            if housenumber:
                cursor.execute("""
                    SELECT CONCAT(m.street, ' ', m.housenumber) AS address,
                           m.building,
                           m.levels,
                           m.roof_shape,
                           m.coordinates
                    FROM map AS m
                    WHERE LOWER(m.street) LIKE %s AND m.housenumber = %s
                    limit 20
                """, ['%' + street + '%', housenumber])
            else:
                cursor.execute("""
                    SELECT CONCAT(m.street, ' ', m.housenumber) AS address,
                           m.building,
                           m.levels,
                           m.roof_shape,
                           m.coordinates
                    FROM map AS m
                    WHERE LOWER(m.street) LIKE %s
                    limit 20
                """, ['%' + street + '%'])

            rows = cursor.fetchall()  # Получаем все строки из результата запроса
            addresses = []
            for row in rows:
                address = {
                    'address': row[0],
                    'building': row[1],
                    'levels': row[2],
                    'roof_shape': row[3],
                    'coordinates': row[4]
                }
                addresses.append(address)

        return JsonResponse(addresses, safe=False)
    else:
        return JsonResponse({'error': 'Search string not provided'}, status=400)




@csrf_exempt
@require_POST
def get_matching_coordinates(request):
    request_data = json.loads(request.body.decode('utf-8')) # Assuming the data is sent via POST request
    lat = request_data.get('lat')
    long = request_data.get('long')

    if lat is None or long is None:
        return JsonResponse({'error': 'Latitude or longitude is missing'}, status=400)

    try:
        lat = float(lat)
        long = float(long)
    except ValueError:
        return JsonResponse({'error': 'Latitude or longitude is not a valid number'}, status=400)

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM map WHERE coordinates::jsonb @> %s::jsonb",
            [f'[[{lat}, {long}]]']
        )
        matching_data = cursor.fetchall()

    matching_results = []
    for row in matching_data:
        matching_results.append({
            'id': row[0],
            'housenumber': row[1],
            'street': row[2],
            'building': row[3],
            'levels': row[4],
            'roof_shape': row[5],
            'coordinates': row[6],
        })

    return JsonResponse(matching_results, safe=False)


class AddressListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, user_id):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT address FROM Addresses WHERE user_id = %s",
                [user_id]
            )
            addresses = cursor.fetchall()
        address_dicts = [json.loads(address[0]) for address in addresses]

        # Создаем список словарей с ключом 'address'
        addresses_list = [{'address': address} for address in address_dicts]


        # Возвращаем JSON-ответ
        return JsonResponse(addresses_list, safe=False)